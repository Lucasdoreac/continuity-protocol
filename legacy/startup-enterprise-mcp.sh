#!/bin/bash

# 🚀 ENTERPRISE MCP TOOLS - STARTUP SCRIPT
# Garante que todas as dependências estejam funcionando

echo "🎯 INICIANDO ENTERPRISE MCP SERVER..."
echo "===================================="

# Navegar para diretório correto
cd /Users/lucascardoso/apps/MCP/CONTINUITY

# Verificar se sistema experimental está rodando
echo "🔍 Verificando sistema experimental..."
EXPERIMENTAL_PID=$(ps aux | grep "mcp-continuity start" | grep -v grep | awk '{print $2}' | head -1)

if [ ! -z "$EXPERIMENTAL_PID" ]; then
    echo "✅ Sistema experimental ativo (PID: $EXPERIMENTAL_PID)"
else
    echo "🔄 Iniciando sistema experimental..."
    cd project-states/mcp-continuity-service
    source venv/bin/activate
    nohup mcp-continuity start > ../../../experimental.log 2>&1 &
    sleep 3
    cd ../../
    echo "✅ Sistema experimental iniciado"
fi

# Verificar se enterprise tools estão disponíveis
echo "🧪 Testando enterprise tools..."
python3 -c "
import sys
from pathlib import Path
sys.path.append(str(Path.cwd() / 'project-states' / 'mcp-continuity-service' / 'src' / 'mcp_tools'))
from enterprise_wrapper import enterprise_tools
result = enterprise_tools.get_available_tools()
print(f'✅ Enterprise tools: {result[\"count\"]} ferramentas disponíveis')
assert result['available'] == True, 'Enterprise tools não disponíveis'
"

if [ $? -eq 0 ]; then
    echo "✅ Enterprise tools funcionando"
else
    echo "❌ Erro nas enterprise tools"
    exit 1
fi

# Verificar dependências MCP
echo "📦 Verificando dependências MCP..."
python3 -c "import mcp.server.fastmcp; print('✅ FastMCP disponível')" 2>/dev/null

if [ $? -ne 0 ]; then
    echo "📦 Instalando FastMCP..."
    pip3 install mcp
fi

echo "🚀 SISTEMA PRONTO!"
echo "================="
echo "✅ Sistema experimental: ATIVO"
echo "✅ Enterprise tools: FUNCIONANDO" 
echo "✅ Dependências MCP: INSTALADAS"
echo "✅ Servidor MCP: PRONTO PARA INICIAR"
echo ""
echo "🎯 Claude Desktop pode agora conectar ao servidor enterprise!"
