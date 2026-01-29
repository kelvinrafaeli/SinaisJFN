#!/bin/bash

# Script de Deploy para VPS
# Sistema de Sinais JFN - Crypto Trading

set -e  # Para em caso de erro

echo "🚀 Iniciando deploy do Sistema de Sinais JFN..."

# Cores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Verifica se Docker está instalado
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker não está instalado!${NC}"
    echo "Instale o Docker com:"
    echo "curl -fsSL https://get.docker.com -o get-docker.sh && sh get-docker.sh"
    exit 1
fi

# Verifica se Docker Compose está instalado
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}❌ Docker Compose não está instalado!${NC}"
    echo "Instale o Docker Compose com:"
    echo "sudo curl -L \"https://github.com/docker/compose/releases/latest/download/docker-compose-\$(uname -s)-\$(uname -m)\" -o /usr/local/bin/docker-compose"
    echo "sudo chmod +x /usr/local/bin/docker-compose"
    exit 1
fi

echo -e "${GREEN}✅ Docker e Docker Compose encontrados${NC}"

# Para containers existentes
echo -e "${YELLOW}🛑 Parando containers existentes...${NC}"
docker-compose down || true

# Remove imagens antigas (opcional)
read -p "Deseja remover imagens antigas? (s/N) " -n 1 -r
echo
if [[ $REPLY =~ ^[Ss]$ ]]; then
    echo -e "${YELLOW}🗑️  Removendo imagens antigas...${NC}"
    docker-compose down --rmi all || true
fi

# Constrói a nova imagem
echo -e "${YELLOW}🔨 Construindo nova imagem...${NC}"
docker-compose build --no-cache

# Inicia os containers
echo -e "${YELLOW}🚢 Iniciando containers...${NC}"
docker-compose up -d

# Aguarda o serviço ficar pronto
echo -e "${YELLOW}⏳ Aguardando serviço ficar disponível...${NC}"
sleep 10

# Verifica status
echo -e "${YELLOW}📊 Verificando status dos containers...${NC}"
docker-compose ps

# Testa a aplicação
echo -e "${YELLOW}🔍 Testando aplicação...${NC}"
if curl -f http://localhost:8000/api/status &> /dev/null; then
    echo -e "${GREEN}✅ Aplicação está rodando corretamente!${NC}"
    echo -e "${GREEN}🌐 Acesse: http://seu-ip:80${NC}"
else
    echo -e "${RED}❌ Erro ao acessar a aplicação${NC}"
    echo -e "${YELLOW}📋 Logs do container:${NC}"
    docker-compose logs --tail=50
    exit 1
fi

# Mostra logs
echo -e "${YELLOW}📋 Últimas linhas do log:${NC}"
docker-compose logs --tail=20

echo ""
echo -e "${GREEN}✅ Deploy concluído com sucesso!${NC}"
echo ""
echo "Comandos úteis:"
echo "  Ver logs:           docker-compose logs -f"
echo "  Parar:              docker-compose stop"
echo "  Reiniciar:          docker-compose restart"
echo "  Parar e remover:    docker-compose down"
echo "  Status:             docker-compose ps"
