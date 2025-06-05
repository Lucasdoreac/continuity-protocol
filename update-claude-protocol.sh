#!/bin/bash
# Script para atualizar a configuração do Claude Desktop para usar o servidor de Protocolo de Continuidade

HOME_DIR="/Users/lucascardoso"
CONTINUITY_DIR="${HOME_DIR}/apps/MCP/CONTINUITY"
CLAUDE_CONFIG_DIR="${HOME_DIR}/Library/Application Support/Claude"
CLAUDE_CONFIG_FILE="${CLAUDE_CONFIG_DIR}/claude_desktop_config.json"
SERVER_NAME="continuity-protocol"

# Cores para output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Verificar se jq está instalado
if ! command -v jq &> /dev/null; then
    echo -e "${RED}jq não está instalado. Por favor, instale para continuar:${NC}"
    echo "brew install jq"
    exit 1
fi

echo "Atualizando configuração do Claude Desktop para usar o servidor de Protocolo de Continuidade..."
TMP_FILE=$(mktemp)

# Atualizar o servidor Continuity Protocol para usar o servidor completo
jq --arg cmd "python3" --arg arg "${CONTINUITY_DIR}/continuity-protocol-server.py" --arg desc "Continuity Protocol - Servidor de Protocolo de Continuidade de Projetos" '
.mcpServers["continuity-protocol"] = {
  "command": $cmd,
  "args": [$arg],
  "description": $desc
}
' "$CLAUDE_CONFIG_FILE" > "$TMP_FILE"

# Verificar se o JSON resultante é válido
if jq empty "$TMP_FILE" 2>/dev/null; then
    mv "$TMP_FILE" "$CLAUDE_CONFIG_FILE"
    echo -e "${GREEN}Configuração atualizada com sucesso!${NC}"
    echo "O servidor Continuity Protocol agora usa: continuity-protocol-server.py"
    echo -e "${YELLOW}IMPORTANTE:${NC} Reinicie o Claude Desktop para aplicar as mudanças"
else
    echo -e "${RED}Falha ao criar configuração JSON válida${NC}"
    rm -f "$TMP_FILE"
    exit 1
fi