#!/bin/bash
# Script para iniciar o servidor MCP simplificado

CONTINUITY_DIR="/Users/lucascardoso/apps/MCP/CONTINUITY"
SERVER_SCRIPT="${CONTINUITY_DIR}/src/servers/simple-mcp-server.py"
LOG_FILE="${CONTINUITY_DIR}/logs/simple-server.log"
PID_FILE="${CONTINUITY_DIR}/simple-mcp-server.pid"

# Cores para output
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Criar diretório de logs se não existir
mkdir -p "$(dirname "$LOG_FILE")"

# Verificar se o servidor já está em execução
if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    if ps -p "$PID" > /dev/null; then
        echo -e "${RED}Servidor já está em execução com PID $PID${NC}"
        echo "Use: ${CONTINUITY_DIR}/scripts/stop-simple-server.sh para parar"
        exit 1
    else
        echo "Removendo PID file antigo..."
        rm -f "$PID_FILE"
    fi
fi

# Iniciar o servidor
echo -e "${BLUE}Iniciando servidor MCP simplificado...${NC}"
nohup python3 "$SERVER_SCRIPT" > "$LOG_FILE" 2>&1 &
PID=$!
echo $PID > "$PID_FILE"

# Verificar se o servidor iniciou corretamente
sleep 2
if ps -p "$PID" > /dev/null; then
    echo -e "${GREEN}Servidor iniciado com sucesso!${NC}"
    echo "PID: $PID"
    echo "Log: $LOG_FILE"
    echo "Para parar o servidor: ${CONTINUITY_DIR}/scripts/stop-simple-server.sh"
else
    echo -e "${RED}Falha ao iniciar o servidor${NC}"
    echo "Verifique o log: $LOG_FILE"
    rm -f "$PID_FILE"
    exit 1
fi