"""
Sistema de envio de alertas via Telegram
"""
import requests
from typing import Optional
from datetime import datetime


class TelegramBot:
    """Bot para enviar alertas via Telegram"""
    
    def __init__(self, token: str, chat_id: str):
        """
        Inicializa o bot do Telegram
        
        Args:
            token: Token do bot do Telegram
            chat_id: ID do grupo/chat para enviar mensagens
        """
        self.token = token
        self.chat_id = chat_id
        self.base_url = f"https://api.telegram.org/bot{token}"
        
    def send_message(self, message: str, parse_mode: str = "Markdown") -> bool:
        """
        Envia uma mensagem para o chat/grupo
        
        Args:
            message: Mensagem a ser enviada
            parse_mode: Formato da mensagem (Markdown ou HTML)
            
        Returns:
            True se enviado com sucesso, False caso contrário
        """
        try:
            url = f"{self.base_url}/sendMessage"
            payload = {
                "chat_id": self.chat_id,
                "text": message,
                "parse_mode": parse_mode
            }
            
            response = requests.post(url, json=payload, timeout=10)
            
            if response.status_code == 200:
                return True
            else:
                print(f"Erro ao enviar mensagem: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"Erro ao enviar mensagem para o Telegram: {str(e)}")
            return False
    
    def format_signal_message(self, alert: dict) -> str:
        """
        Formata uma mensagem de alerta para o Telegram
        
        Args:
            alert: Dicionário com dados do alerta
            
        Returns:
            Mensagem formatada
        """
        signal_type = alert['signal_type']
        symbol = alert['symbol']
        message = alert['message']
        timestamp = alert['timestamp']
        data = alert.get('data', {})
        
        # Emojis para cada tipo de sinal
        emoji_map = {
            'BUY': '🟢',
            'SELL': '🔴',
            'INFO': 'ℹ️'
        }
        
        emoji = emoji_map.get(signal_type, '📊')
        
        # Extrai informações da mensagem original
        if signal_type in ['BUY', 'SELL']:
            # Parse da mensagem para extrair preço, SL, TP, etc
            parts = message.split('|')
            
            formatted_message = f"{'═' * 30}\n"
            formatted_message += f"{emoji} **{signal_type}** - **{symbol}**\n"
            formatted_message += f"{'═' * 30}\n\n"
            
            # Adiciona preço de entrada
            if 'entry_price' in data:
                formatted_message += f"💰 **Preço de Entrada**\n"
                formatted_message += f"   `${data['entry_price']:.4f}`\n\n"
            
            # Adiciona Stop Loss
            if 'stop_loss' in data:
                formatted_message += f"🛑 **Stop Loss**\n"
                formatted_message += f"   `${data['stop_loss']:.4f}` (-2%)\n\n"
            
            # Adiciona Take Profit
            if 'take_profit' in data:
                formatted_message += f"🎯 **Take Profit**\n"
                formatted_message += f"   `${data['take_profit']:.4f}` (+3%)\n\n"
            
            # Adiciona razão do sinal (última parte da mensagem)
            if len(parts) > 3:
                reason = parts[-1].strip()
                formatted_message += f"📊 **Análise**\n"
                formatted_message += f"   {reason}\n\n"
            
            # Adiciona estatísticas se houver
            if 'Assertividade' in message:
                stats_part = [p for p in parts if 'Assertividade' in p]
                if stats_part:
                    formatted_message += f"{stats_part[0].strip()}\n\n"
            
            formatted_message += f"{'─' * 30}\n"
            formatted_message += f"🕐 {datetime.fromisoformat(timestamp).strftime('%d/%m/%Y %H:%M:%S')}"
            
        else:
            # Para mensagens INFO, mantém formato mais simples
            formatted_message = f"{emoji} **{signal_type}**\n\n"
            formatted_message += f"**{symbol}**\n"
            formatted_message += f"{message}\n\n"
            formatted_message += f"🕐 {datetime.fromisoformat(timestamp).strftime('%d/%m/%Y %H:%M:%S')}"
        
        return formatted_message
    
    def send_alert(self, alert: dict) -> bool:
        """
        Envia um alerta formatado para o Telegram
        
        Args:
            alert: Dicionário com dados do alerta
            
        Returns:
            True se enviado com sucesso, False caso contrário
        """
        message = self.format_signal_message(alert)
        return self.send_message(message)
    
    def test_connection(self) -> bool:
        """
        Testa a conexão com o Telegram
        
        Returns:
            True se a conexão está ok, False caso contrário
        """
        try:
            url = f"{self.base_url}/getMe"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                bot_info = response.json()
                print(f"Bot conectado: {bot_info['result']['first_name']}")
                return True
            else:
                print(f"Erro ao conectar: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"Erro ao testar conexão: {str(e)}")
            return False
