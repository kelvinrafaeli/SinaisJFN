"""
Sistema de Monitoramento e Gerenciamento de Posições
Inclui Stop Loss e Take Profit
"""
import pandas as pd
from typing import Dict, List, Optional
from datetime import datetime


class PositionManager:
    """Gerencia posições abertas com Stop Loss e Take Profit"""
    
    def __init__(self, 
                 stop_loss_pct: float = 2.0,
                 take_profit_pct: float = 3.0,
                 risk_reward_ratio: float = 1.5):
        """
        Inicializa o gerenciador de posições
        
        Args:
            stop_loss_pct: Percentual de stop loss (padrão 2%)
            take_profit_pct: Percentual de take profit (padrão 3%)
            risk_reward_ratio: Razão risco/retorno (padrão 1.5:1)
        """
        self.stop_loss_pct = stop_loss_pct
        self.take_profit_pct = take_profit_pct
        self.risk_reward_ratio = risk_reward_ratio
        self.positions: Dict[str, Dict] = {}
        # Estatísticas por símbolo: {symbol: {wins: 0, losses: 0, total: 0, win_rate: 0.0}}
        self.statistics: Dict[str, Dict] = {}
    
    def calculate_stop_loss(self, entry_price: float, position_type: str) -> float:
        """
        Calcula o preço de stop loss
        
        Args:
            entry_price: Preço de entrada
            position_type: 'LONG' ou 'SHORT'
        """
        if position_type == 'LONG':
            return entry_price * (1 - self.stop_loss_pct / 100)
        else:  # SHORT
            return entry_price * (1 + self.stop_loss_pct / 100)
    
    def calculate_take_profit(self, entry_price: float, position_type: str) -> float:
        """
        Calcula o preço de take profit
        
        Args:
            entry_price: Preço de entrada
            position_type: 'LONG' ou 'SHORT'
        """
        if position_type == 'LONG':
            return entry_price * (1 + self.take_profit_pct / 100)
        else:  # SHORT
            return entry_price * (1 - self.take_profit_pct / 100)
    
    def open_position(self, 
                      symbol: str, 
                      position_type: str, 
                      entry_price: float,
                      signal_strength: int = 1,
                      message: str = '') -> Dict:
        """
        Abre uma nova posição
        
        Args:
            symbol: Símbolo do ativo (ex: BTC/USDT)
            position_type: 'LONG' ou 'SHORT'
            entry_price: Preço de entrada
            signal_strength: Força do sinal (1-3)
            message: Mensagem descritiva
        """
        stop_loss = self.calculate_stop_loss(entry_price, position_type)
        take_profit = self.calculate_take_profit(entry_price, position_type)
        
        position = {
            'symbol': symbol,
            'type': position_type,
            'entry_price': entry_price,
            'stop_loss': stop_loss,
            'take_profit': take_profit,
            'signal_strength': signal_strength,
            'entry_time': datetime.now().isoformat(),
            'status': 'OPEN',
            'message': message,
            'pnl': 0.0,
            'pnl_pct': 0.0
        }
        
        self.positions[symbol] = position
        return position
    
    def check_exit_conditions(self, symbol: str, current_price: float) -> Optional[Dict]:
        """
        Verifica se alguma condição de saída foi atingida
        
        Args:
            symbol: Símbolo do ativo
            current_price: Preço atual
            
        Returns:
            Dict com informações de saída se alguma condição foi atingida, None caso contrário
        """
        if symbol not in self.positions:
            return None
        
        position = self.positions[symbol]
        
        if position['status'] != 'OPEN':
            return None
        
        position_type = position['type']
        entry_price = position['entry_price']
        stop_loss = position['stop_loss']
        take_profit = position['take_profit']
        
        # Calcula PnL
        if position_type == 'LONG':
            pnl_pct = ((current_price - entry_price) / entry_price) * 100
        else:  # SHORT
            pnl_pct = ((entry_price - current_price) / entry_price) * 100
        
        position['pnl_pct'] = pnl_pct
        
        # Verifica Stop Loss
        if position_type == 'LONG' and current_price <= stop_loss:
            return self.close_position(symbol, current_price, 'STOP_LOSS')
        elif position_type == 'SHORT' and current_price >= stop_loss:
            return self.close_position(symbol, current_price, 'STOP_LOSS')
        
        # Verifica Take Profit
        if position_type == 'LONG' and current_price >= take_profit:
            return self.close_position(symbol, current_price, 'TAKE_PROFIT')
        elif position_type == 'SHORT' and current_price <= take_profit:
            return self.close_position(symbol, current_price, 'TAKE_PROFIT')
        
        return None
    
    def close_position(self, symbol: str, exit_price: float, exit_reason: str) -> Dict:
        """
        Fecha uma posição
        
        Args:
            symbol: Símbolo do ativo
            exit_price: Preço de saída
            exit_reason: Razão da saída (STOP_LOSS, TAKE_PROFIT, MANUAL, SIGNAL)
        """
        if symbol not in self.positions:
            return {'error': 'Position not found'}
        
        position = self.positions[symbol]
        entry_price = position['entry_price']
        position_type = position['type']
        
        # Calcula PnL final
        if position_type == 'LONG':
            pnl_pct = ((exit_price - entry_price) / entry_price) * 100
        else:  # SHORT
            pnl_pct = ((entry_price - exit_price) / entry_price) * 100
        
        position['exit_price'] = exit_price
        position['exit_time'] = datetime.now().isoformat()
        position['exit_reason'] = exit_reason
        position['status'] = 'CLOSED'
        position['pnl_pct'] = pnl_pct
        
        # Atualiza estatísticas
        self._update_statistics(symbol, exit_reason, pnl_pct)
        
        return position
    
    def get_position(self, symbol: str) -> Optional[Dict]:
        """Retorna informações de uma posição"""
        return self.positions.get(symbol)
    
    def get_all_positions(self) -> List[Dict]:
        """Retorna todas as posições"""
        return list(self.positions.values())
    
    def get_open_positions(self) -> List[Dict]:
        """Retorna apenas posições abertas"""
        return [p for p in self.positions.values() if p['status'] == 'OPEN']
    
    def _update_statistics(self, symbol: str, exit_reason: str, pnl_pct: float):
        """
        Atualiza estatísticas do símbolo
        
        Args:
            symbol: Símbolo do ativo
            exit_reason: Razão da saída
            pnl_pct: Percentual de lucro/prejuízo
        """
        if symbol not in self.statistics:
            self.statistics[symbol] = {
                'wins': 0,
                'losses': 0,
                'total': 0,
                'win_rate': 0.0,
                'total_pnl': 0.0,
                'avg_win': 0.0,
                'avg_loss': 0.0
            }
        
        stats = self.statistics[symbol]
        stats['total'] += 1
        stats['total_pnl'] += pnl_pct
        
        # Considera win se atingiu take profit OU teve lucro positivo
        is_win = exit_reason == 'TAKE_PROFIT' or pnl_pct > 0
        
        if is_win:
            stats['wins'] += 1
            # Calcula média de ganhos
            stats['avg_win'] = ((stats['avg_win'] * (stats['wins'] - 1)) + pnl_pct) / stats['wins']
        else:
            stats['losses'] += 1
            # Calcula média de perdas
            stats['avg_loss'] = ((stats['avg_loss'] * (stats['losses'] - 1)) + pnl_pct) / stats['losses']
        
        # Calcula taxa de acerto
        stats['win_rate'] = (stats['wins'] / stats['total']) * 100 if stats['total'] > 0 else 0.0
    
    def get_statistics(self, symbol: str = None) -> Dict:
        """
        Retorna estatísticas de assertividade
        
        Args:
            symbol: Símbolo específico (opcional). Se None, retorna todas
        """
        if symbol:
            return self.statistics.get(symbol, {
                'wins': 0,
                'losses': 0,
                'total': 0,
                'win_rate': 0.0,
                'total_pnl': 0.0,
                'avg_win': 0.0,
                'avg_loss': 0.0
            })
        return self.statistics
    
    def reset_statistics(self, symbol: str = None):
        """
        Reseta estatísticas
        
        Args:
            symbol: Símbolo específico (opcional). Se None, reseta todas
        """
        if symbol:
            if symbol in self.statistics:
                del self.statistics[symbol]
        else:
            self.statistics = {}


class AlertMonitor:
    """Monitora e gerencia alertas de sinais"""
    
    def __init__(self):
        self.alerts: List[Dict] = []
        self.max_alerts = 100  # Mantém apenas os últimos 100 alertas
        self.last_alert_candle: Dict[str, int] = {}  # Armazena timestamp da última vela alertada por símbolo
    
    def should_alert(self, symbol: str, candle_timestamp: int) -> bool:
        """
        Verifica se deve gerar alerta para o símbolo
        Retorna True apenas se for uma nova vela
        
        Args:
            symbol: Símbolo do ativo
            candle_timestamp: Timestamp da vela atual (em milissegundos)
        """
        if symbol not in self.last_alert_candle:
            return True
        
        # Se o timestamp da vela é diferente da última alertada, pode alertar
        return candle_timestamp != self.last_alert_candle[symbol]
    
    def add_alert(self, 
                  symbol: str, 
                  signal_type: str, 
                  message: str, 
                  data: Dict,
                  candle_timestamp: int = None) -> Dict:
        """
        Adiciona um novo alerta
        
        Args:
            symbol: Símbolo do ativo
            signal_type: Tipo do sinal (BUY, SELL, INFO)
            message: Mensagem descritiva
            data: Dados adicionais
            candle_timestamp: Timestamp da vela (em milissegundos)
        """
        alert = {
            'timestamp': datetime.now().isoformat(),
            'symbol': symbol,
            'signal_type': signal_type,
            'message': message,
            'data': data
        }
        
        # Registra o timestamp da vela alertada
        if candle_timestamp:
            self.last_alert_candle[symbol] = candle_timestamp
        
        self.alerts.insert(0, alert)  # Adiciona no início da lista
        
        # Limita o número de alertas
        if len(self.alerts) > self.max_alerts:
            self.alerts = self.alerts[:self.max_alerts]
        
        return alert
    
    def get_alerts(self, limit: int = 50) -> List[Dict]:
        """Retorna os alertas mais recentes"""
        return self.alerts[:limit]
    
    def clear_alerts(self):
        """Limpa todos os alertas"""
        self.alerts = []


class TradingStrategy:
    """Estratégia de trading baseada no GCM HRT"""
    
    def __init__(self, 
                 position_manager: PositionManager,
                 alert_monitor: AlertMonitor):
        """
        Inicializa a estratégia
        
        Args:
            position_manager: Gerenciador de posições
            alert_monitor: Monitor de alertas
        """
        self.position_manager = position_manager
        self.alert_monitor = alert_monitor
    
    def process_signal(self, symbol: str, signal: Dict, current_price: float, candle_timestamp: int = None) -> Dict:
        """
        Processa um sinal e decide se abre/fecha posições
        
        Args:
            symbol: Símbolo do ativo
            signal: Sinal do indicador
            current_price: Preço atual
            candle_timestamp: Timestamp da vela atual (em milissegundos)
            
        Returns:
            Dict com ação tomada
        """
        signal_type = signal['signal']
        strength = signal['strength']
        
        # Verifica se já existe posição aberta
        current_position = self.position_manager.get_position(symbol)
        
        result = {
            'action': 'NONE',
            'message': '',
            'position': None,
            'alert': None
        }
        
        # Se já tem posição aberta, verifica condições de saída
        if current_position and current_position['status'] == 'OPEN':
            exit_info = self.position_manager.check_exit_conditions(symbol, current_price)
            
            if exit_info:
                result['action'] = 'EXIT'
                result['position'] = exit_info
                result['message'] = f"Posição fechada: {exit_info['exit_reason']}"
                
                # Adiciona alerta
                alert = self.alert_monitor.add_alert(
                    symbol=symbol,
                    signal_type='INFO',
                    message=result['message'],
                    data=exit_info
                )
                result['alert'] = alert
                
                return result
            
            # Atualiza PnL da posição
            current_position['current_price'] = current_price
            result['position'] = current_position
        
        # Processa sinais de entrada (apenas se não tem posição)
        if not current_position or current_position['status'] != 'OPEN':
            # Apenas opera com sinais confirmados (strength >= 3)
            # Sinais de força 1-2 são apenas alertas/avisos
            if signal_type == 'BUY' and strength >= 3:
                # Verifica se deve alertar (nova vela)
                if not candle_timestamp or self.alert_monitor.should_alert(symbol, candle_timestamp):
                    # Abre posição LONG
                    position = self.position_manager.open_position(
                        symbol=symbol,
                        position_type='LONG',
                        entry_price=current_price,
                        signal_strength=strength,
                        message=signal['message']
                    )
                    
                    result['action'] = 'ENTRY_LONG'
                    result['position'] = position
                    
                    # Obtém estatísticas do símbolo
                    stats = self.position_manager.get_statistics(symbol)
                    stats_msg = ""
                    if stats['total'] > 0:
                        stats_msg = f" | 🎯 Assertividade: {stats['win_rate']:.1f}% ({stats['wins']}W/{stats['losses']}L)"
                    
                    result['message'] = f"✅ COMPRA: {symbol} a ${current_price:.4f} | SL: ${position['stop_loss']:.4f} (-2%) | TP: ${position['take_profit']:.4f} (+3%) | {signal['message']}{stats_msg}"
                    
                    # Adiciona alerta
                    alert = self.alert_monitor.add_alert(
                        symbol=symbol,
                        signal_type='BUY',
                        message=result['message'],
                        data=position,
                        candle_timestamp=candle_timestamp
                    )
                    result['alert'] = alert
            
            elif signal_type == 'SELL' and strength >= 3:
                # Verifica se deve alertar (nova vela)
                if not candle_timestamp or self.alert_monitor.should_alert(symbol, candle_timestamp):
                    # Abre posição SHORT
                    position = self.position_manager.open_position(
                        symbol=symbol,
                        position_type='SHORT',
                        entry_price=current_price,
                        signal_strength=strength,
                        message=signal['message']
                    )
                    
                    result['action'] = 'ENTRY_SHORT'
                    result['position'] = position
                    
                    # Obtém estatísticas do símbolo
                    stats = self.position_manager.get_statistics(symbol)
                    stats_msg = ""
                    if stats['total'] > 0:
                        stats_msg = f" | 🎯 Assertividade: {stats['win_rate']:.1f}% ({stats['wins']}W/{stats['losses']}L)"
                    
                    result['message'] = f"✅ VENDA: {symbol} a ${current_price:.4f} | SL: ${position['stop_loss']:.4f} (+2%) | TP: ${position['take_profit']:.4f} (-3%) | {signal['message']}{stats_msg}"
                    
                    # Adiciona alerta
                    alert = self.alert_monitor.add_alert(
                        symbol=symbol,
                        signal_type='SELL',
                        message=result['message'],
                        data=position,
                        candle_timestamp=candle_timestamp
                    )
                    result['alert'] = alert
        
        return result
