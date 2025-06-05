#!/bin/bash
# Script para testar o servidor Continuity Protocol

# Cores para output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== Teste do Continuity Protocol ===${NC}"

# Verificar se os arquivos principais existem
echo -e "${YELLOW}Verificando arquivos principais...${NC}"

FILES=(
    "/Users/lucascardoso/apps/MCP/CONTINUITY/basic-unified-server.py"
    "/Users/lucascardoso/apps/MCP/CONTINUITY/autonomous-recovery.sh"
    "/Users/lucascardoso/apps/MCP/CONTINUITY/magic-system.sh"
    "/Users/lucascardoso/apps/MCP/CONTINUITY/emergency-absolute.sh"
)

all_files_exist=true
for file in "${FILES[@]}"; do
    if [ -f "$file" ]; then
        echo -e "  ${GREEN}✓${NC} $file"
    else
        echo -e "  ${RED}✗${NC} $file"
        all_files_exist=false
    fi
done

if [ "$all_files_exist" = false ]; then
    echo -e "${RED}Alguns arquivos principais estão faltando!${NC}"
    exit 1
fi

echo -e "${GREEN}Todos os arquivos principais existem.${NC}"

# Verificar se o servidor pode ser executado
echo -e "${YELLOW}Verificando se o servidor pode ser executado...${NC}"
if python3 -c "from mcp.server.fastmcp import FastMCP; print('OK')"; then
    echo -e "${GREEN}FastMCP está disponível.${NC}"
else
    echo -e "${RED}FastMCP não está disponível. Instale com: pip install mcp${NC}"
    exit 1
fi

# Verificar a configuração do Claude Desktop
echo -e "${YELLOW}Verificando configuração do Claude Desktop...${NC}"
CONFIG_FILE="/Users/lucascardoso/Library/Application Support/Claude/claude_desktop_config.json"

if [ -f "$CONFIG_FILE" ]; then
    if grep -q "basic-unified-server.py" "$CONFIG_FILE"; then
        echo -e "${GREEN}Configuração do Claude Desktop está correta.${NC}"
    else
        echo -e "${RED}Configuração do Claude Desktop não está apontando para o servidor unificado.${NC}"
        echo -e "${YELLOW}Execute ./update-to-basic.sh para corrigir.${NC}"
    fi
else
    echo -e "${RED}Arquivo de configuração do Claude Desktop não encontrado.${NC}"
fi

# Testar backup de emergência
echo -e "${YELLOW}Testando sistema de backup de emergência...${NC}"
if [ -f "/Users/lucascardoso/apps/MCP/CONTINUITY/emergency-absolute.sh" ]; then
    echo -e "${GREEN}Sistema de backup de emergência está disponível.${NC}"
else
    echo -e "${RED}Sistema de backup de emergência não está disponível.${NC}"
fi

echo -e "${BLUE}=== Teste Concluído ===${NC}"
echo ""
echo -e "${GREEN}✓ O Continuity Protocol está pronto para uso!${NC}"
echo -e "${YELLOW}Reinicie o Claude Desktop para ativar o servidor unificado.${NC}"
echo -e "${YELLOW}Depois, use o comando /tools continuity_test para verificar se está funcionando.${NC}"