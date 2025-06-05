#!/bin/bash
# Script para parar o servidor unificado Continuity Protocol

CONTINUITY_DIR="/Users/lucascardoso/apps/MCP/CONTINUITY"
PID_FILE="${CONTINUITY_DIR}/continuity-server.pid"

# Cores para output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Verificar se o arquivo PID existe
if [ ! -f "$PID_FILE" ]; then
    echo -e "${RED}Servidor não está em execução (arquivo PID não encontrado)${NC}"
    exit 1
fi

# Ler o PID
PID=$(cat "$PID_FILE")

# Verificar se o processo existe
if ! ps -p "$PID" > /dev/null; then
    echo -e "${RED}Processo com PID $PID não está em execução${NC}"
    rm -f "$PID_FILE"
    exit 1
fi

# Parar o processo
echo "Parando servidor Continuity Protocol com PID $PID..."
kill "$PID"

# Verificar se o processo foi encerrado
sleep 2
if ps -p "$PID" > /dev/null; then
    echo -e "${RED}Falha ao parar o servidor. Forçando encerramento...${NC}"
    kill -9 "$PID"
    sleep 1
fi

# Verificar novamente
if ps -p "$PID" > /dev/null; then
    echo -e "${RED}Não foi possível encerrar o processo com PID $PID${NC}"
    exit 1
else
    echo -e "${GREEN}Servidor parado com sucesso${NC}"
    rm -f "$PID_FILE"
fi