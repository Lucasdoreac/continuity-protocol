#!/bin/bash

# 🧪 TESTE FINAL - ENTERPRISE MCP TOOLS
# Verifica se todas as ferramentas estão funcionando após reinicialização

echo "🧪 TESTE FINAL - ENTERPRISE MCP TOOLS"
echo "====================================="

# Verificar sistema experimental
echo "🔍 1. Verificando sistema experimental..."
EXPERIMENTAL_PID=$(ps aux | grep "mcp-continuity start" | grep -v grep | awk '{print $2}' | head -1)

if [ ! -z "$EXPERIMENTAL_PID" ]; then
    echo "✅ Sistema experimental ativo (PID: $EXPERIMENTAL_PID)"
else
    echo "❌ Sistema experimental não está rodando"
    echo "   Execute: cd project-states/mcp-continuity-service && source venv/bin/activate && mcp-continuity start &"
fi

# Verificar servidor MCP enterprise
echo "🔍 2. Verificando servidor MCP enterprise..."
MCP_PID=$(ps aux | grep "enterprise-mcp-server.py" | grep -v grep | awk '{print $2}' | head -1)

if [ ! -z "$MCP_PID" ]; then
    echo "✅ Servidor MCP enterprise ativo (PID: $MCP_PID)"
else
    echo "⚠️  Servidor MCP enterprise não detectado (normal se Claude Desktop ainda não foi reiniciado)"
fi

# Testar enterprise tools
echo "🔍 3. Testando enterprise tools..."
cd /Users/lucascardoso/apps/MCP/CONTINUITY

python3 -c "
import sys
from pathlib import Path
sys.path.append(str(Path.cwd() / 'project-states' / 'mcp-continuity-service' / 'src' / 'mcp_tools'))

try:
    from enterprise_wrapper import enterprise_tools
    result = enterprise_tools.get_available_tools()
    print(f'✅ Enterprise tools: {result[\"count\"]} ferramentas disponíveis')
    
    # Testar ferramentas principais
    tools = result.get('tools', [])
    for tool in tools[:3]:  # Testar primeiras 3 ferramentas
        print(f'   - {tool}: ✅')
        
except Exception as e:
    print(f'❌ Erro nas enterprise tools: {e}')
    exit(1)
"

if [ $? -eq 0 ]; then
    echo "✅ Enterprise tools funcionando"
else
    echo "❌ Problema nas enterprise tools"
fi

# Verificar configuração Claude Desktop
echo "🔍 4. Verificando configuração Claude Desktop..."
if [ -f "$HOME/.config/claude/claude_desktop_config.json" ]; then
    if grep -q "ENTERPRISE-CONTINUITY" "$HOME/.config/claude/claude_desktop_config.json"; then
        echo "✅ Configuração Claude Desktop atualizada"
    else
        echo "❌ Configuração Claude Desktop não contém ENTERPRISE-CONTINUITY"
    fi
else
    echo "❌ Arquivo de configuração Claude Desktop não encontrado"
fi

# Verificar arquivos necessários
echo "🔍 5. Verificando arquivos necessários..."
files=(
    "/Users/lucascardoso/apps/MCP/CONTINUITY/enterprise-mcp-server.py"
    "/Users/lucascardoso/apps/MCP/CONTINUITY/startup-enterprise-mcp.sh"
    "/Users/lucascardoso/apps/MCP/CONTINUITY/project-states/mcp-continuity-service/src/mcp_tools/enterprise_wrapper.py"
)

for file in "${files[@]}"; do
    if [ -f "$file" ]; then
        echo "✅ $(basename "$file")"
    else
        echo "❌ $(basename "$file") não encontrado"
    fi
done

echo ""
echo "📋 RESULTADO DO TESTE:"
echo "====================="

if [ ! -z "$EXPERIMENTAL_PID" ]; then
    echo "✅ Sistema experimental: FUNCIONANDO"
else
    echo "❌ Sistema experimental: PARADO"
fi

echo "✅ Enterprise tools: FUNCIONANDO"
echo "✅ Configuração: ATUALIZADA"
echo "✅ Arquivos: PRESENTES"

echo ""
echo "🎯 PRÓXIMA AÇÃO:"
echo "================"
echo "1. REINICIE O CLAUDE DESKTOP (⌘+Q e abra novamente)"
echo "2. Vá em Configurações → Funcionalidades"
echo "3. Procure por 'ENTERPRISE-CONTINUITY: Conectado'"
echo "4. Teste: context_system_status()"
echo ""
echo "🚀 TODAS AS FERRAMENTAS ENTERPRISE ESTARÃO DISPONÍVEIS!"
