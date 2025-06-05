#!/bin/bash
# Script para configurar a integração do servidor minimal com Claude Desktop

HOME_DIR="/Users/lucascardoso"
CONTINUITY_DIR="${HOME_DIR}/apps/MCP/CONTINUITY"
CLAUDE_CONFIG_DIR="${HOME_DIR}/Library/Application Support/Claude"
CLAUDE_CONFIG_FILE="${CLAUDE_CONFIG_DIR}/claude_desktop_config.json"
SERVER_NAME="continuity-minimal"

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

# Adicionar ou atualizar a configuração do servidor
echo "Configurando servidor MCP minimal no Claude Desktop..."
TMP_FILE=$(mktemp)

# Ler configuração atual e adicionar/atualizar o servidor
jq --arg name "$SERVER_NAME" --arg cmd "python3" --arg arg "${CONTINUITY_DIR}/minimal-mcp-server.py" '
.mcpServers[$name] = {
  "command": $cmd,
  "args": [$arg],
  "description": "Minimal Continuity Protocol - Servidor Ultrabásico"
}
' "$CLAUDE_CONFIG_FILE" > "$TMP_FILE"

# Verificar se o JSON resultante é válido
if jq empty "$TMP_FILE" 2>/dev/null; then
    mv "$TMP_FILE" "$CLAUDE_CONFIG_FILE"
    echo -e "${GREEN}Servidor MCP minimal configurado com sucesso no Claude Desktop!${NC}"
    echo "Nome: $SERVER_NAME"
    echo "Comando: python3 ${CONTINUITY_DIR}/minimal-mcp-server.py"
else
    echo -e "${RED}Falha ao criar configuração JSON válida${NC}"
    rm -f "$TMP_FILE"
    exit 1
fi

echo -e "${YELLOW}IMPORTANTE:${NC} Reinicie o Claude Desktop para aplicar as mudanças"
echo "Após reiniciar, você pode testar o servidor em:"
echo "Configurações > Integrações > $SERVER_NAME"