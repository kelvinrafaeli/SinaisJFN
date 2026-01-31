# API Telegram - Sistema de Sinais GCM HRT

## Endpoints Disponíveis

### 1. Testar Conexão com Telegram
**POST** `/api/telegram/test`

Envia uma mensagem de teste para o grupo do Telegram para verificar se está funcionando.

**Resposta de Sucesso:**
```json
{
  "success": true,
  "message": "Mensagem de teste enviada com sucesso!"
}
```

**Exemplo com curl:**
```bash
curl -X POST http://localhost:8000/api/telegram/test
```

### 2. Verificar Status do Telegram
**GET** `/api/telegram/status`

Verifica se o bot está conectado e retorna informações básicas.

**Resposta:**
```json
{
  "connected": true,
  "chat_id": "-1003850170115"
}
```

**Exemplo com curl:**
```bash
curl http://localhost:8000/api/telegram/status
```

## Funcionamento Automático

O sistema envia alertas automaticamente para o Telegram quando:

1. **Sinal de Compra (LONG)** - Força ≥ 3
   - Mensagem inclui: preço de entrada, stop loss, take profit
   - Emoji: 🟢

2. **Sinal de Venda (SHORT)** - Força ≥ 3
   - Mensagem inclui: preço de entrada, stop loss, take profit
   - Emoji: 🔴

3. **Fechamento de Posição**
   - Stop Loss atingido
   - Take Profit atingido
   - Fechamento manual
   - Emoji: ℹ️

## Formato das Mensagens

### Exemplo de Alerta de Compra:
```
🟢 **BUY** - BTC/USDT

✅ COMPRA: BTC/USDT a $45000.0000 | SL: $44100.0000 (-2%) | TP: $46350.0000 (+3%) | HARSI cruza -20 (sobrevenda) | 🎯 Assertividade: 75.0% (3W/1L)

🕐 31/01/2026 10:30:00
```

### Exemplo de Alerta de Venda:
```
🔴 **SELL** - ETH/USDT

✅ VENDA: ETH/USDT a $2500.0000 | SL: $2550.0000 (+2%) | TP: $2425.0000 (-3%) | HARSI cruza +20 (sobrecompra) | 🎯 Assertividade: 80.0% (4W/1L)

🕐 31/01/2026 10:35:00
```

## Configuração

As credenciais do Telegram são carregadas do arquivo `.env`:

```env
TELEGRAM_TOKEN=8463181734:AAEh1G4kXq-36uva-suuzv0u1liBumn-bts
TELEGRAM_CHAT_ID=-1003850170115
```

## Segurança

- ⚠️ **NUNCA** commite o arquivo `.env` no git
- O token do bot dá acesso completo ao bot
- Use grupos privados para receber alertas
- Considere usar variáveis de ambiente em produção

## Troubleshooting

### Bot não está enviando mensagens

1. Verifique se o bot está adicionado ao grupo
2. Verifique se o `CHAT_ID` está correto (deve ter o `-` antes se for grupo)
3. Teste a conexão: `POST /api/telegram/test`
4. Verifique os logs do servidor

### Erro "Chat not found"

O `CHAT_ID` está incorreto. Para obter o ID correto:
1. Adicione [@RawDataBot](https://t.me/rawdatabot) ao grupo
2. Copie o `chat.id` da mensagem enviada
3. Atualize o `.env` com o ID correto

### Bot sem permissões

Certifique-se de que o bot tem permissões para:
- Enviar mensagens no grupo
- Não está em modo "silent" (se aplicável)
