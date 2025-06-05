#!/bin/bash
# Script para configurar a integração com Claude Desktop

HOME_DIR="/Users/lucascardoso"
CONTINUITY_DIR="${HOME_DIR}/apps/MCP/CONTINUITY"
CLAUDE_CONFIG_DIR="${HOME_DIR}/Library/Application Support/Claude"
CLAUDE_CONFIG_FILE="${CLAUDE_CONFIG_DIR}/claude_desktop_config.json"
SERVER_NAME="unified-continuity-protocol"
SERVER_PORT=3457

# Cores para output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Verificar se o diretório de configuração do Claude existe
if [ ! -d "$CLAUDE_CONFIG_DIR" ]; then
    echo "Criando diretório de configuração do Claude..."
    mkdir -p "$CLAUDE_CONFIG_DIR"
fi

# Verificar se o arquivo de configuração existe
if [ ! -f "$CLAUDE_CONFIG_FILE" ]; then
    echo "Criando arquivo de configuração básico do Claude..."
    echo '{
  "mcpServers": {}
}' > "$CLAUDE_CONFIG_FILE"
fi

# Verificar se o arquivo é um JSON válido
if ! command -v jq &> /dev/null; then
    echo -e "${RED}jq não está instalado. Por favor, instale para continuar:${NC}"
    echo "brew install jq"
    exit 1
fi

if ! jq empty "$CLAUDE_CONFIG_FILE" 2>/dev/null; then
    echo -e "${RED}Arquivo de configuração do Claude não é um JSON válido${NC}"
    echo "Fazendo backup e criando um novo..."
    cp "$CLAUDE_CONFIG_FILE" "${CLAUDE_CONFIG_FILE}.bak.$(date +%Y%m%d%H%M%S)"
    echo '{
  "mcpServers": {}
}' > "$CLAUDE_CONFIG_FILE"
fi

# Adicionar ou atualizar a configuração do servidor
echo "Configurando servidor MCP no Claude Desktop..."
TMP_FILE=$(mktemp)

# Ler configuração atual e adicionar/atualizar o servidor
jq --arg name "$SERVER_NAME" --arg cmd "python3" --arg arg "${CONTINUITY_DIR}/src/servers/unified-mcp-server.py" '
.mcpServers[$name] = {
  "command": $cmd,
  "args": [$arg],
  "description": "Unified Continuity Protocol - Servidor MCP"
}
' "$CLAUDE_CONFIG_FILE" > "$TMP_FILE"

# Verificar se o JSON resultante é válido
if jq empty "$TMP_FILE" 2>/dev/null; then
    mv "$TMP_FILE" "$CLAUDE_CONFIG_FILE"
    echo -e "${GREEN}Servidor MCP configurado com sucesso no Claude Desktop!${NC}"
    echo "Nome: $SERVER_NAME"
    echo "Comando: python3 ${CONTINUITY_DIR}/src/servers/unified-mcp-server.py"
else
    echo -e "${RED}Falha ao criar configuração JSON válida${NC}"
    rm -f "$TMP_FILE"
    exit 1
fi

echo -e "${YELLOW}IMPORTANTE:${NC} Reinicie o Claude Desktop para aplicar as mudanças"
echo "Após reiniciar, você pode testar o servidor em:"
echo "Configurações > Integrações > $SERVER_NAME"
