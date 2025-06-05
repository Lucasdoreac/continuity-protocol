#!/bin/bash
# Script para instalar o Continuity Protocol em vários clientes MCP

CONTINUITY_DIR="/Users/lucascardoso/apps/MCP/CONTINUITY"
INTEGRATION_DIR="${CONTINUITY_DIR}/integration"

# Cores para output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Criar diretório de integração se não existir
mkdir -p "$INTEGRATION_DIR"

echo -e "${BLUE}=== Instalação do Continuity Protocol ===${NC}"
echo "Este script instalará o Continuity Protocol em vários clientes MCP."

# Verificar dependências
echo -e "${YELLOW}Verificando dependências...${NC}"
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Python 3 não encontrado. Por favor, instale para continuar.${NC}"
    exit 1
fi

if ! command -v jq &> /dev/null; then
    echo -e "${RED}jq não encontrado. Por favor, instale para continuar:${NC}"
    echo "brew install jq"
    exit 1
fi

# Claude Desktop
echo -e "${YELLOW}Configurando Claude Desktop...${NC}"
"${CONTINUITY_DIR}/update-claude-protocol.sh"
echo ""

# Claude Code CLI (se estiver instalado)
echo -e "${YELLOW}Configurando Claude Code CLI...${NC}"
if command -v claude &> /dev/null; then
    echo "Claude Code CLI encontrado. Configurando..."
    claude mcp remove continuity-protocol &> /dev/null || true
    claude mcp add continuity-protocol --transport stdio python3 "${CONTINUITY_DIR}/continuity-protocol-server.py"
    echo -e "${GREEN}Claude Code CLI configurado com sucesso!${NC}"
else
    echo -e "${YELLOW}Claude Code CLI não encontrado. Pulando...${NC}"
    echo "Para instalar manualmente após a instalação do Claude Code CLI:"
    echo "claude mcp add continuity-protocol --transport stdio python3 ${CONTINUITY_DIR}/continuity-protocol-server.py"
fi
echo ""

# Servidor HTTP (opcional)
echo -e "${YELLOW}Deseja iniciar o servidor HTTP? (y/n)${NC}"
read -r start_http
if [[ "$start_http" == "y" ]]; then
    echo "Iniciando servidor HTTP na porta 3000..."
    nohup python3 "${CONTINUITY_DIR}/continuity-protocol-server.py" http 3000 > "${CONTINUITY_DIR}/logs/http-server.log" 2>&1 &
    HTTP_PID=$!
    echo $HTTP_PID > "${CONTINUITY_DIR}/http-server.pid"
    echo -e "${GREEN}Servidor HTTP iniciado com PID $HTTP_PID${NC}"
    echo "Para parar o servidor: kill $HTTP_PID"
fi
echo ""

# Criar arquivo de configuração para outros clientes
echo -e "${YELLOW}Criando arquivo de configuração para outros clientes...${NC}"
cat > "${INTEGRATION_DIR}/install-config.json" << EOF
{
  "continuity_protocol": {
    "server_name": "continuity-protocol",
    "stdio": {
      "command": "python3",
      "args": ["${CONTINUITY_DIR}/continuity-protocol-server.py"]
    },
    "http": {
      "url": "http://localhost:3000"
    }
  }
}
EOF
echo -e "${GREEN}Arquivo de configuração criado em ${INTEGRATION_DIR}/install-config.json${NC}"
echo ""

echo -e "${BLUE}=== Instalação Concluída ===${NC}"
echo -e "${GREEN}O Continuity Protocol foi instalado com sucesso!${NC}"
echo ""
echo -e "${YELLOW}Para usar com Claude Desktop:${NC}"
echo "1. Reinicie o Claude Desktop"
echo "2. Use ferramentas como /tools project_list"
echo ""
echo -e "${YELLOW}Para usar com Claude Code CLI:${NC}"
echo "claude mcp run continuity-protocol project_list"
echo ""
echo -e "${YELLOW}Para usar com outros clientes:${NC}"
echo "Consulte a documentação em ${INTEGRATION_DIR}/other-mcp-clients.md"
echo ""