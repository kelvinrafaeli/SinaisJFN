# 🔧 Troubleshooting - Deploy na VPS

## Problema: Bot do Telegram não conecta na VPS

### Solução 1: Verificar variáveis de ambiente

```bash
# Conectar na VPS
ssh user@seu-ip-vps
cd /home/user/sinaisjfn

# Verificar se o .env existe
cat .env

# O arquivo deve conter:
# TELEGRAM_TOKEN=8463181734:AAEh1G4kXq-36uva-suuzv0u1liBumn-bts
# TELEGRAM_CHAT_ID=-1003850170115
```

### Solução 2: Verificar logs do container

```bash
# Ver logs do container
docker-compose logs -f sinaisjfn

# Deve aparecer:
# ✅ Bot do Telegram conectado com sucesso!
```

### Solução 3: Recriar container com .env

```bash
# Parar containers
docker-compose down

# Verificar se .env existe
ls -la .env

# Se não existir, criar:
nano .env

# Adicionar:
TELEGRAM_TOKEN=8463181734:AAEh1G4kXq-36uva-suuzv0u1liBumn-bts
TELEGRAM_CHAT_ID=-1003850170115

# Salvar (CTRL+O, ENTER, CTRL+X)

# Reconstruir e iniciar
docker-compose up -d --build

# Ver logs
docker-compose logs -f
```

## Problema: Erro ao construir imagem (aiohttp)

### Solução: Usar imagem Python mais recente

O Dockerfile já foi atualizado para usar Python 3.11 e instalar o aiohttp atualizado.

```bash
# Limpar cache do Docker
docker system prune -a

# Reconstruir sem cache
docker-compose build --no-cache

# Iniciar
docker-compose up -d
```

## Problema: Container não inicia

### Diagnóstico:

```bash
# Ver status dos containers
docker-compose ps

# Ver logs completos
docker-compose logs

# Ver logs apenas de erros
docker-compose logs | grep -i error

# Entrar no container (se estiver rodando)
docker-compose exec sinaisjfn bash

# Testar Python manualmente
python -c "from telegram_bot import TelegramBot; print('OK')"
```

## Problema: API não responde (porta 8000)

### Solução 1: Verificar firewall

```bash
# Ubuntu/Debian - Liberar porta 8000
sudo ufw allow 8000
sudo ufw reload
sudo ufw status
```

### Solução 2: Verificar se está rodando

```bash
# Ver processos Docker
docker ps

# Testar localmente na VPS
curl http://localhost:8000/api/status

# Testar do seu PC
curl http://IP-DA-VPS:8000/api/status
```

## Checklist Completo de Deploy

✅ **Antes do deploy:**
1. [ ] Arquivo `.env` configurado com token e chat_id
2. [ ] Docker e Docker Compose instalados na VPS
3. [ ] Porta 8000 liberada no firewall

✅ **Durante o deploy:**
1. [ ] Upload dos arquivos incluindo `.env`
2. [ ] Build da imagem sem erros
3. [ ] Container iniciado com sucesso

✅ **Após o deploy:**
1. [ ] Logs mostram "Bot do Telegram conectado com sucesso!"
2. [ ] API responde em http://IP-VPS:8000/api/status
3. [ ] Interface acessível em http://IP-VPS:8000

## Comandos Rápidos de Debug

```bash
# Tudo em um comando - ver se está ok
docker-compose ps && docker-compose logs --tail=50

# Reiniciar tudo do zero
docker-compose down -v
docker-compose up -d --build
docker-compose logs -f

# Testar Telegram manualmente
docker-compose exec sinaisjfn python test_telegram.py
```

## Deploy Correto Passo a Passo

### No seu PC (Windows):

```powershell
# 1. Verificar se .env está configurado
cat .env

# 2. Enviar para VPS
.\upload-to-vps.ps1 -VpsUser "seu-usuario" -VpsIP "seu-ip"
```

### Na VPS (Linux):

```bash
# 1. Conectar
ssh seu-usuario@seu-ip

# 2. Entrar na pasta
cd sinaisjfn

# 3. Verificar .env
cat .env

# 4. Executar deploy
chmod +x deploy.sh
./deploy.sh

# 5. Aguardar build e ver logs
docker-compose logs -f
```

### Esperado nos logs:

```
Testando conexão com Telegram...
Bot conectado: Sinais JFN
✅ Bot do Telegram conectado com sucesso!
INFO:     Started server process [1]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

## Suporte Adicional

Se nada funcionar, colete as seguintes informações:

```bash
# Sistema operacional
cat /etc/os-release

# Versões
docker --version
docker-compose --version
python --version

# Logs completos
docker-compose logs > logs.txt

# Status
docker-compose ps > status.txt
```

E envie para análise.
