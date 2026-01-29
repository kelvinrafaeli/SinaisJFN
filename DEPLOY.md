# 🐳 Deploy Docker - Sistema de Sinais JFN

## 📋 Pré-requisitos na VPS

### 1. Instalar Docker
```bash
# Ubuntu/Debian
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Adicionar seu usuário ao grupo docker (para não precisar de sudo)
sudo usermod -aG docker $USER

# Sair e entrar novamente ou executar:
newgrp docker
```

### 2. Instalar Docker Compose
```bash
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Verificar instalação
docker --version
docker-compose --version
```

## 🚀 Deploy na VPS

### Opção 1: Deploy Automático (Recomendado)

```bash
# 1. Enviar arquivos para VPS
scp -r * user@seu-ip-vps:/home/user/sinaisjfn/

# 2. Conectar na VPS
ssh user@seu-ip-vps

# 3. Entrar na pasta
cd /home/user/sinaisjfn

# 4. Dar permissão ao script
chmod +x deploy.sh

# 5. Executar deploy
./deploy.sh
```

### Opção 2: Deploy Manual

```bash
# 1. Na VPS, clonar ou enviar os arquivos
cd /home/user/sinaisjfn

# 2. Construir e iniciar
docker-compose up -d --build

# 3. Verificar status
docker-compose ps

# 4. Ver logs
docker-compose logs -f
```

## 🌐 Acessar Aplicação

- **Com Nginx (porta 80)**: `http://seu-ip-vps`
- **Direto (porta 8000)**: `http://seu-ip-vps:8000`

## 🔧 Comandos Úteis

```bash
# Ver logs em tempo real
docker-compose logs -f

# Ver logs de um serviço específico
docker-compose logs -f sinaisjfn

# Parar containers
docker-compose stop

# Reiniciar containers
docker-compose restart

# Parar e remover containers
docker-compose down

# Parar, remover e limpar volumes
docker-compose down -v

# Reconstruir imagem
docker-compose build --no-cache

# Atualizar aplicação (após mudanças no código)
docker-compose down
docker-compose up -d --build

# Entrar no container
docker-compose exec sinaisjfn bash

# Ver status dos containers
docker-compose ps

# Ver uso de recursos
docker stats
```

## 🔒 Configuração SSL/HTTPS (Opcional)

### Com Certbot (Let's Encrypt - Gratuito)

```bash
# 1. Instalar Certbot
sudo apt-get update
sudo apt-get install certbot

# 2. Obter certificado (certifique-se que as portas 80/443 estão abertas)
sudo certbot certonly --standalone -d seu-dominio.com

# 3. Copiar certificados para pasta do projeto
sudo cp /etc/letsencrypt/live/seu-dominio.com/fullchain.pem ./ssl/cert.pem
sudo cp /etc/letsencrypt/live/seu-dominio.com/privkey.pem ./ssl/key.pem

# 4. Editar nginx.conf e descomentar a seção SSL

# 5. Reiniciar
docker-compose restart nginx
```

### Renovação Automática

```bash
# Adicionar ao crontab
sudo crontab -e

# Adicionar linha (renova a cada 2 meses):
0 0 1 */2 * certbot renew --quiet && docker-compose restart nginx
```

## 🔥 Firewall

```bash
# Permitir portas necessárias
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 22/tcp  # SSH

# Se quiser acesso direto à porta 8000
sudo ufw allow 8000/tcp

# Habilitar firewall
sudo ufw enable

# Ver status
sudo ufw status
```

## 📊 Monitoramento

### Ver uso de CPU/RAM
```bash
docker stats
```

### Ver logs de erro
```bash
docker-compose logs --tail=100 | grep -i error
```

## 🔄 Atualização da Aplicação

```bash
# 1. Fazer backup (opcional)
docker-compose down
tar -czf backup-$(date +%Y%m%d).tar.gz .

# 2. Atualizar código (git pull ou scp novos arquivos)
git pull origin main
# ou
scp -r * user@vps:/home/user/sinaisjfn/

# 3. Reconstruir e reiniciar
docker-compose up -d --build

# 4. Verificar logs
docker-compose logs -f
```

## ❌ Solução de Problemas

### Container não inicia
```bash
# Ver logs detalhados
docker-compose logs sinaisjfn

# Verificar se a porta está em uso
sudo netstat -tulpn | grep 8000

# Remover tudo e tentar novamente
docker-compose down -v
docker system prune -a
docker-compose up -d --build
```

### Aplicação não responde
```bash
# Verificar se está rodando
curl http://localhost:8000/api/status

# Reiniciar container
docker-compose restart sinaisjfn

# Ver uso de recursos
docker stats
```

### Erro de memória
```bash
# Adicionar limite de memória no docker-compose.yml
# Adicionar em services.sinaisjfn:
mem_limit: 512m
mem_reservation: 256m
```

## 📝 Variáveis de Ambiente

Crie um arquivo `.env` (opcional):
```bash
# .env
TZ=America/Sao_Paulo
PYTHONUNBUFFERED=1
```

## 🎯 Estrutura de Arquivos

```
SinaisJFN/
├── Dockerfile              # Imagem da aplicação
├── docker-compose.yml      # Orquestração dos containers
├── nginx.conf             # Configuração do Nginx
├── .dockerignore          # Arquivos ignorados no build
├── deploy.sh              # Script de deploy automático
├── requirements.txt       # Dependências Python
├── main.py               # Aplicação FastAPI
├── indicator.py          # Indicador GCM HRT
├── trading.py            # Lógica de trading
├── static/               # Frontend HTML/CSS/JS
├── logs/                 # Logs da aplicação (criado automaticamente)
└── ssl/                  # Certificados SSL (se usar HTTPS)
```

## 🌟 Produção Recomendada

1. ✅ Use Nginx como proxy reverso (já incluído)
2. ✅ Configure SSL/HTTPS com Let's Encrypt
3. ✅ Configure firewall (ufw)
4. ✅ Configure backup automático
5. ✅ Configure monitoramento (Grafana/Prometheus - opcional)
6. ✅ Use domínio próprio
7. ✅ Configure renovação automática de SSL

## 📞 Suporte

Se encontrar problemas:
1. Verifique os logs: `docker-compose logs -f`
2. Verifique portas: `sudo netstat -tulpn`
3. Verifique recursos: `docker stats`
4. Reinicie: `docker-compose restart`
