#!/bin/bash
# Script para limpar a configuração do Claude Desktop e manter apenas um servidor Continuity

HOME_DIR="/Users/lucascardoso"
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

echo "Fazendo backup da configuração atual..."
cp "$CLAUDE_CONFIG_FILE" "${CLAUDE_CONFIG_FILE}.bak.$(date +%Y%m%d%H%M%S)"

echo "Limpando configuração e mantendo apenas um servidor Continuity..."
TMP_FILE=$(mktemp)

# Primeiro, preservar todos os servidores que não são do Continuity Protocol
jq 'del(.mcpServers["continuity-protocol-enterprise"]) | 
    del(.mcpServers["unified-continuity-protocol"]) | 
    del(.mcpServers["simple-continuity-protocol"]) | 
    del(.mcpServers["basic-continuity-protocol"]) | 
    del(.mcpServers["continuity-minimal"])' "$CLAUDE_CONFIG_FILE" > "$TMP_FILE"

# Verificar se o JSON resultante é válido
if ! jq empty "$TMP_FILE" 2>/dev/null; then
    echo -e "${RED}Erro ao processar JSON. Arquivo de configuração não modificado.${NC}"
    rm -f "$TMP_FILE"
    exit 1
fi

# Agora adicionar o único servidor Continuity Protocol
jq --arg name "$SERVER_NAME" '
.mcpServers[$name] = {
  "command": "python3",
  "args": [
    "/Users/lucascardoso/apps/MCP/CONTINUITY/minimal-mcp-server.py"
  ],
  "description": "Continuity Protocol - Servidor Unificado"
}
' "$TMP_FILE" > "${TMP_FILE}.2"

# Verificar se o JSON resultante é válido
if ! jq empty "${TMP_FILE}.2" 2>/dev/null; then
    echo -e "${RED}Erro ao adicionar novo servidor. Arquivo de configuração não modificado.${NC}"
    rm -f "$TMP_FILE" "${TMP_FILE}.2"
    exit 1
fi

# Aplicar as mudanças
mv "${TMP_FILE}.2" "$CLAUDE_CONFIG_FILE"
rm -f "$TMP_FILE"

echo -e "${GREEN}Configuração limpa com sucesso!${NC}"
echo "Todos os servidores Continuity Protocol foram removidos e substituídos por: $SERVER_NAME"
echo -e "${YELLOW}IMPORTANTE:${NC} Reinicie o Claude Desktop para aplicar as mudanças"