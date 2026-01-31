# Sistema de Sinais GCM HRT - Crypto Trading

Sistema completo de análise técnica e alertas para criptomoedas baseado no indicador **GCM Heikin Ashi RSI Trend Cloud**.

## 🚀 Características

- ✅ **Indicador GCM HRT** adaptado do Pine Script para Python
- ✅ **Monitoramento automático** de múltiplos símbolos
- ✅ **Stop Loss e Take Profit** configuráveis
- ✅ **Interface web** moderna e responsiva
- ✅ **API REST** completa para integração
- ✅ **Alertas em tempo real** de sinais de compra/venda
- ✅ **Gerenciamento de posições** com tracking de PnL
- ✅ **Notificações via Telegram** automáticas

## 📦 Instalação

### 1. Instalar Python 3.9+

Certifique-se de ter Python 3.9 ou superior instalado.

### 2. Instalar dependências

```powershell
pip install -r requirements.txt
```

### 3. Configurar Telegram

Copie o arquivo `.env.example` para `.env` e configure suas credenciais do Telegram:

```powershell
copy .env.example .env
```

Edite o arquivo `.env` e adicione:
```env
TELEGRAM_TOKEN=seu_token_aqui
TELEGRAM_CHAT_ID=seu_chat_id_aqui
```

## 🤖 Configuração do Bot Telegram

### 1. Criar um Bot

1. Abra o Telegram e procure por [@BotFather](https://t.me/botfather)
2. Envie `/newbot` e siga as instruções
3. Copie o **token** fornecido

### 2. Adicionar o Bot ao Grupo

1. Crie um grupo no Telegram ou use um existente
2. Adicione seu bot ao grupo
3. Para obter o Chat ID:
   - Adicione [@RawDataBot](https://t.me/rawdatabot) ao grupo
   - O bot enviará uma mensagem com o `chat.id` do grupo
   - Use esse ID no arquivo `.env`

## 🎯 Como Usar

### Iniciar o servidor

```powershell
python main.py
```

O servidor estará disponível em: **http://localhost:8000**

### Acessar a interface web

Abra o navegador e acesse: **http://localhost:8000**

### Testar Telegram

Você pode testar se o Telegram está funcionando:

1. Via API: `POST http://localhost:8000/api/telegram/test`
2. Via interface web (se implementado)
3. O bot enviará automaticamente alertas quando detectar **sinais de compra/venda com força ≥ 3**

> 💡 **Nota**: Apenas sinais confirmados (força ≥ 3) são enviados via Telegram. Fechamentos de posição não geram notificações.

## 📊 Funcionalidades da Interface

### 1. **Status do Sistema**
- Monitora se o sistema está ativo
- Mostra última atualização
- Exibe símbolos configurados e posições abertas

### 2. **Análise de Símbolos**
- Analisa um símbolo específico
- Analisa todos os símbolos configurados
- Mostra sinais de compra/venda baseados no GCM HRT

### 3. **Configuração**
- Configure quais símbolos monitorar (BTC/USDT, ETH/USDT, etc)
- Ajuste o timeframe (1d = diário, 4h = 4 horas, etc)
- Configure Stop Loss e Take Profit em percentual

### 4. **Posições Abertas**
- Visualize todas as posições abertas
- Acompanhe PnL em tempo real
- Feche posições manualmente

### 5. **Alertas**
- Receba alertas de sinais importantes
- Veja histórico de alertas
- Alertas de cruzamento dos níveis 20/-20
- **Notificações automáticas via Telegram**

### 6. **Histórico**
- Visualize todas as posições fechadas
- Acompanhe performance histórica

## 🎲 Indicador GCM HRT

### Sinais de Compra (BUY)
- RSI cruza **-20** (sobrevenda)
- RSI cruza **-30** (sobrevenda extrema)
- Reversão bullish no Heikin Ashi RSI
- Reversão bullish no RSI

### Sinais de Venda (SELL)
- RSI cruza **+20** (sobrecompra)
- RSI cruza **+30** (sobrecompra extrema)
- Reversão bearish no Heikin Ashi RSI
- Reversão bearish no RSI

### Parâmetros Padrão
- **Length HARSI**: 10
- **Smoothing**: 5
- **Length RSI**: 7
- **Timeframe**: 1d (diário)
- **Stop Loss**: 2%
- **Take Profit**: 3% (risco/retorno 1:1.5)

## 🔧 API REST

### Endpoints Principais

#### Status do Sistema
```
GET /api/status
```

#### Analisar Símbolo
```
GET /api/analyze/{symbol}?timeframe=1d
```

#### Analisar Todos
```
GET /api/analyze-all
```

#### Iniciar/Parar Monitoramento
```
POST /api/monitoring/start
POST /api/monitoring/stop
```

#### Posições
```
GET /api/positions
GET /api/positions/{symbol}
POST /api/positions/{symbol}/close
```

#### Alertas
```
GET /api/alerts?limit=50
DELETE /api/alerts
```

#### Configuração
```
POST /api/monitoring/config
POST /api/config/position
```

## 📈 Estratégia de Trading

### Entrada em Posição
- **LONG**: Quando RSI cruza -20 ou -30 (força do sinal ≥ 2)
- **SHORT**: Quando RSI cruza +20 ou +30 (força do sinal ≥ 2)

### Saída de Posição
- **Stop Loss**: Automático quando atinge -2% de perda
- **Take Profit**: Automático quando atinge +3% de lucro
- **Manual**: Você pode fechar manualmente pela interface

### Força do Sinal
- **1**: Sinal fraco (reversão no RSI)
- **2**: Sinal médio (cruzamento de nível ou reversão HARSI)
- **3**: Sinal forte (cruzamento de nível extremo)

## ⚠️ Avisos Importantes

### Modo Demo
- O sistema está configurado para modo **DEMO** (paper trading)
- **Não executa trades reais** automaticamente
- Para trading real, você precisaria integrar com a API da exchange

### Configuração para Trading Real
Se desejar conectar a uma exchange real:

1. Obtenha API keys na exchange (Binance, etc)
2. Configure no arquivo `.env`:
   ```
   API_KEY=sua_api_key
   API_SECRET=seu_api_secret
   ```
3. Modifique o código para executar ordens reais

### Riscos
- Trading de criptomoedas envolve riscos
- Este sistema é apenas uma ferramenta de análise
- Sempre faça sua própria pesquisa (DYOR)
- Nunca invista mais do que pode perder

## 🛠️ Estrutura do Projeto

```
SinaisJFN/
├── main.py              # API FastAPI principal
├── indicator.py         # Implementação do indicador GCM HRT
├── trading.py           # Sistema de gerenciamento de posições
├── requirements.txt     # Dependências Python
├── .env.example         # Exemplo de configuração
├── static/
│   └── index.html      # Interface web
└── README.md           # Este arquivo
```

## 🔄 Próximos Passos

### Melhorias Sugeridas
1. **Notificações**: Adicionar Telegram/Email/WhatsApp
2. **Backtesting**: Testar estratégia em dados históricos
3. **Machine Learning**: Otimizar parâmetros automaticamente
4. **Multi-timeframe**: Analisar múltiplos timeframes
5. **Divergências**: Implementar detecção de divergências
6. **Mais indicadores**: RSI, MACD, Bollinger Bands

## 📝 Licença

Este projeto é fornecido "como está" para fins educacionais.

## 🤝 Suporte

Para dúvidas ou sugestões, abra uma issue no repositório.

---

**Desenvolvido com Python 🐍 e FastAPI ⚡**
