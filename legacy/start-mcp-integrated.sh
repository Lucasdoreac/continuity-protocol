#!/bin/bash
#
# Iniciar o Servidor MCP Continuity Integrado
# Este script inicia o servidor MCP Continuity com integração LLMOps
#

# Diretório base
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Cores para output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Verificar requisitos
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 não encontrado. Por favor, instale o Python 3 antes de continuar.${NC}"
    exit 1
fi

# Verificar se o FastMCP está instalado
if ! python3 -c "import mcp.server.fastmcp" &> /dev/null; then
    echo -e "${BLUE}Instalando FastMCP...${NC}"
    pip install fastmcp
fi

# Verificar se o servidor existe
SERVER_PATH="$SCRIPT_DIR/mcp-continuity-server-integrated.py"
if [ ! -f "$SERVER_PATH" ]; then
    echo -e "${RED}❌ Servidor não encontrado: $SERVER_PATH${NC}"
    exit 1
fi

# Verificar se os diretórios de LLMOps existem
mkdir -p "$SCRIPT_DIR/llmops/timesheets"
mkdir -p "$SCRIPT_DIR/llmops/sprints"
mkdir -p "$SCRIPT_DIR/llmops/reports"

# Iniciar o servidor
echo -e "${BLUE}===== Iniciando MCP Continuity Server (Integrado) =====${NC}"
echo -e "${GREEN}✅ Servidor: $SERVER_PATH${NC}"
echo -e "${GREEN}✅ LLMOps Timesheet ativado${NC}"
echo -e "${BLUE}==================================================${NC}"
echo ""

# Executar o servidor
python3 "$SERVER_PATH"