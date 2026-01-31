"""
API FastAPI para o sistema de sinais de criptomoedas
"""
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional
import ccxt
import pandas as pd
import asyncio
from datetime import datetime
import os
from dotenv import load_dotenv

from indicator import GCMIndicator
from trading import PositionManager, AlertMonitor, TradingStrategy
from telegram_bot import TelegramBot

# Carrega variáveis de ambiente
load_dotenv()

# Inicializa FastAPI
app = FastAPI(title="Sistema de Sinais GCM HRT", version="1.0.0")

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inicializa componentes
indicator = GCMIndicator()
position_manager = PositionManager(
    stop_loss_pct=2.0,
    take_profit_pct=3.0
)
alert_monitor = AlertMonitor()
strategy = TradingStrategy(position_manager, alert_monitor)

# Inicializa bot do Telegram
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "8463181734:AAEh1G4kXq-36uva-suuzv0u1liBumn-bts")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "-1003850170115")
telegram_bot = TelegramBot(TELEGRAM_TOKEN, TELEGRAM_CHAT_ID)

# Testa conexão com Telegram
print("Testando conexão com Telegram...")
if telegram_bot.test_connection():
    print("✅ Bot do Telegram conectado com sucesso!")
else:
    print("⚠️ Erro ao conectar com o Telegram")

# Exchange (modo demo - sem API keys)
exchange = ccxt.binance({
    'enableRateLimit': True,
})

# Estado do monitoramento
monitoring_state = {
    'is_running': False,
    'symbols': [
        'BTC/USDT', 'ETH/USDT', 'BNB/USDT', 'SOL/USDT', 'XRP/USDT',
        'ADA/USDT', 'DOGE/USDT', 'MATIC/USDT', 'DOT/USDT', 'AVAX/USDT',
        'LINK/USDT', 'UNI/USDT', 'ATOM/USDT', 'LTC/USDT', 'ETC/USDT',
        'NEAR/USDT', 'APT/USDT', 'ARB/USDT', 'OP/USDT', 'SUI/USDT'
    ],
    'timeframe': '15m',
    'last_update': None
}


# ==================== MODELOS ====================

class SymbolConfig(BaseModel):
    symbols: List[str]
    timeframe: str = '15m'


class PositionConfig(BaseModel):
    stop_loss_pct: float = 2.0
    take_profit_pct: float = 6.0


# ==================== FUNÇÕES AUXILIARES ====================

async def fetch_ohlcv(symbol: str, timeframe: str = '15m', limit: int = 100):
    """Busca dados OHLCV de uma exchange"""
    try:
        ohlcv = await asyncio.to_thread(
            exchange.fetch_ohlcv,
            symbol,
            timeframe,
            limit=limit
        )
        
        df = pd.DataFrame(
            ohlcv,
            columns=['timestamp', 'open', 'high', 'low', 'close', 'volume']
        )
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        
        return df
    except Exception as e:
        print(f"Erro ao buscar dados para {symbol}: {str(e)}")
        return None


async def analyze_symbol(symbol: str, timeframe: str = '15m') -> Dict:
    """Analisa um símbolo e retorna sinais"""
    try:
        # Busca dados
        df = await fetch_ohlcv(symbol, timeframe, limit=100)
        
        if df is None or len(df) == 0:
            return {
                'symbol': symbol,
                'error': 'Não foi possível buscar dados',
                'success': False
            }
        
        # Calcula indicadores
        df_with_indicators = indicator.calculate(df)
        
        # Obtém sinal
        signal = indicator.get_signal(df_with_indicators)
        
        # Processa com a estratégia
        current_price = float(df['close'].iloc[-1])
        # Converte timestamp do pandas para int (milissegundos)
        if 'timestamp' in df.columns:
            ts = df['timestamp'].iloc[-1]
            candle_timestamp = int(ts.timestamp() * 1000) if hasattr(ts, 'timestamp') else int(ts)
        else:
            candle_timestamp = None
        strategy_result = strategy.process_signal(symbol, signal, current_price, candle_timestamp)
        
        # Envia alerta pelo Telegram se houver uma ação
        if strategy_result['action'] != 'NONE' and strategy_result.get('alert'):
            try:
                telegram_bot.send_alert(strategy_result['alert'])
            except Exception as e:
                print(f"Erro ao enviar alerta para Telegram: {str(e)}")
        
        return {
            'symbol': symbol,
            'success': True,
            'price': current_price,
            'signal': signal,
            'strategy_action': strategy_result,
            'timestamp': datetime.now().isoformat()
        }
    
    except Exception as e:
        return {
            'symbol': symbol,
            'error': str(e),
            'success': False
        }


async def monitor_loop():
    """Loop de monitoramento contínuo"""
    while monitoring_state['is_running']:
        try:
            print(f"[{datetime.now()}] Executando análise...")
            
            # Analisa todos os símbolos
            tasks = [
                analyze_symbol(symbol, monitoring_state['timeframe'])
                for symbol in monitoring_state['symbols']
            ]
            
            results = await asyncio.gather(*tasks)
            
            monitoring_state['last_update'] = datetime.now().isoformat()
            
            # Log dos resultados
            for result in results:
                if result['success']:
                    action = result['strategy_action']['action']
                    if action != 'NONE':
                        print(f"  {result['symbol']}: {action} - {result['strategy_action']['message']}")
            
            # Aguarda intervalo (1 minuto para M15)
            await asyncio.sleep(60)
            
        except Exception as e:
            print(f"Erro no loop de monitoramento: {str(e)}")
            await asyncio.sleep(60)


# ==================== ROTAS ====================

@app.get("/")
async def read_root():
    """Rota raiz - serve a interface web"""
    return FileResponse("static/index.html")


@app.get("/api/status")
async def get_status():
    """Retorna o status do sistema"""
    return {
        'monitoring': monitoring_state['is_running'],
        'symbols': monitoring_state['symbols'],
        'timeframe': monitoring_state['timeframe'],
        'last_update': monitoring_state['last_update'],
        'open_positions': len(position_manager.get_open_positions()),
        'total_positions': len(position_manager.get_all_positions())
    }


@app.get("/api/analyze/{symbol}")
async def analyze_single_symbol(symbol: str, timeframe: str = '15m'):
    """Analisa um símbolo específico"""
    # Substitui - por / (ex: BTC-USDT -> BTC/USDT)
    symbol = symbol.replace('-', '/')
    
    result = await analyze_symbol(symbol, timeframe)
    
    if not result['success']:
        raise HTTPException(status_code=400, detail=result.get('error', 'Erro na análise'))
    
    return result


@app.get("/api/analyze-all")
async def analyze_all_symbols():
    """Analisa todos os símbolos configurados"""
    tasks = [
        analyze_symbol(symbol, monitoring_state['timeframe'])
        for symbol in monitoring_state['symbols']
    ]
    
    results = await asyncio.gather(*tasks)
    
    return {
        'results': results,
        'timestamp': datetime.now().isoformat()
    }


@app.get("/api/chart/{symbol}")
async def get_chart_data(symbol: str, timeframe: str = '1d', limit: int = 100):
    """Retorna dados do gráfico com indicadores"""
    symbol = symbol.replace('-', '/')
    
    df = await fetch_ohlcv(symbol, timeframe, limit)
    
    if df is None:
        raise HTTPException(status_code=400, detail="Não foi possível buscar dados")
    
    # Calcula indicadores
    df_with_indicators = indicator.calculate(df)
    
    # Converte para formato JSON
    chart_data = df_with_indicators.to_dict(orient='records')
    
    # Converte timestamp para string
    for item in chart_data:
        item['timestamp'] = item['timestamp'].isoformat() if pd.notna(item['timestamp']) else None
    
    return {
        'symbol': symbol,
        'timeframe': timeframe,
        'data': chart_data
    }


@app.post("/api/monitoring/start")
async def start_monitoring(background_tasks: BackgroundTasks):
    """Inicia o monitoramento automático"""
    if monitoring_state['is_running']:
        return {'message': 'Monitoramento já está ativo'}
    
    monitoring_state['is_running'] = True
    background_tasks.add_task(monitor_loop)
    
    return {'message': 'Monitoramento iniciado'}


@app.post("/api/monitoring/stop")
async def stop_monitoring():
    """Para o monitoramento automático"""
    monitoring_state['is_running'] = False
    return {'message': 'Monitoramento parado'}


@app.post("/api/monitoring/config")
async def configure_monitoring(config: SymbolConfig):
    """Configura os símbolos e timeframe para monitoramento"""
    monitoring_state['symbols'] = config.symbols
    monitoring_state['timeframe'] = config.timeframe
    
    return {
        'message': 'Configuração atualizada',
        'symbols': config.symbols,
        'timeframe': config.timeframe
    }


@app.get("/api/positions")
async def get_positions():
    """Retorna todas as posições"""
    return {
        'open_positions': position_manager.get_open_positions(),
        'all_positions': position_manager.get_all_positions()
    }


@app.get("/api/positions/{symbol}")
async def get_position(symbol: str):
    """Retorna informações de uma posição específica"""
    symbol = symbol.replace('-', '/')
    
    position = position_manager.get_position(symbol)
    
    if not position:
        raise HTTPException(status_code=404, detail="Posição não encontrada")
    
    return position


@app.post("/api/positions/{symbol}/close")
async def close_position_manual(symbol: str):
    """Fecha uma posição manualmente"""
    symbol = symbol.replace('-', '/')
    
    position = position_manager.get_position(symbol)
    
    if not position or position['status'] != 'OPEN':
        raise HTTPException(status_code=404, detail="Posição aberta não encontrada")
    
    # Busca preço atual
    df = await fetch_ohlcv(symbol, '1m', limit=1)
    if df is None:
        raise HTTPException(status_code=400, detail="Não foi possível obter preço atual")
    
    current_price = float(df['close'].iloc[-1])
    
    # Fecha posição
    closed_position = position_manager.close_position(symbol, current_price, 'MANUAL')
    
    # Adiciona alerta (sem notificação Telegram)
    alert_monitor.add_alert(
        symbol=symbol,
        signal_type='INFO',
        message=f"Posição fechada manualmente",
        data=closed_position
    )
    
    return closed_position


@app.post("/api/config/position")
async def configure_position_settings(config: PositionConfig):
    """Configura stop loss e take profit"""
    position_manager.stop_loss_pct = config.stop_loss_pct
    position_manager.take_profit_pct = config.take_profit_pct
    
    return {
        'message': 'Configurações atualizadas',
        'stop_loss_pct': config.stop_loss_pct,
        'take_profit_pct': config.take_profit_pct
    }


@app.get("/api/alerts")
async def get_alerts(limit: int = 50):
    """Retorna os alertas mais recentes"""
    return {
        'alerts': alert_monitor.get_alerts(limit)
    }


@app.delete("/api/alerts")
async def clear_alerts():
    """Limpa todos os alertas"""
    alert_monitor.clear_alerts()
    return {'message': 'Alertas limpos'}


@app.get("/api/statistics")
async def get_statistics(symbol: str = None):
    """Retorna estatísticas de assertividade"""
    if symbol:
        symbol = symbol.replace('-', '/')
    
    stats = position_manager.get_statistics(symbol)
    
    return {
        'statistics': stats,
        'timestamp': datetime.now().isoformat()
    }


@app.delete("/api/statistics")
async def reset_statistics(symbol: str = None):
    """Reseta estatísticas de assertividade"""
    if symbol:
        symbol = symbol.replace('-', '/')
    
    position_manager.reset_statistics(symbol)
    
    return {
        'message': f'Estatísticas {"do símbolo " + symbol if symbol else "de todos os símbolos"} resetadas'
    }


@app.post("/api/telegram/test")
async def test_telegram():
    """Testa envio de mensagem pelo Telegram"""
    try:
        message = f"🤖 **Teste de Conexão**\n\nSistema de Sinais GCM HRT conectado com sucesso!\n\n🕐 {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}"
        success = telegram_bot.send_message(message)
        
        if success:
            return {
                'success': True,
                'message': 'Mensagem de teste enviada com sucesso!'
            }
        else:
            return {
                'success': False,
                'message': 'Erro ao enviar mensagem de teste'
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/telegram/status")
async def get_telegram_status():
    """Verifica status da conexão com Telegram"""
    try:
        connected = telegram_bot.test_connection()
        return {
            'connected': connected,
            'chat_id': TELEGRAM_CHAT_ID
        }
    except Exception as e:
        return {
            'connected': False,
            'error': str(e)
        }


# Monta pasta estática
app.mount("/static", StaticFiles(directory="static"), name="static")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
