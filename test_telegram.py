"""
Teste rápido do bot do Telegram
"""
from telegram_bot import TelegramBot
import os
from dotenv import load_dotenv

load_dotenv()

# Credenciais
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "8463181734:AAEh1G4kXq-36uva-suuzv0u1liBumn-bts")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "-1003850170115")

print(f"Token: {TELEGRAM_TOKEN}")
print(f"Chat ID: {TELEGRAM_CHAT_ID}")
print()

# Inicializa bot
bot = TelegramBot(TELEGRAM_TOKEN, TELEGRAM_CHAT_ID)

# Testa conexão
print("Testando conexão...")
if bot.test_connection():
    print("✅ Conexão OK!")
    print()
    
    # Envia mensagem de teste
    print("Enviando mensagem de teste...")
    from datetime import datetime
    message = f"🤖 **Teste de Conexão**\n\nSistema de Sinais GCM HRT conectado!\n\n🕐 {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}"
    
    if bot.send_message(message):
        print("✅ Mensagem enviada com sucesso!")
    else:
        print("❌ Erro ao enviar mensagem")
else:
    print("❌ Erro na conexão")
