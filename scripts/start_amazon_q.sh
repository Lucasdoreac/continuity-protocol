#!/bin/bash
# Script para iniciar o Amazon Q CLI com o servidor MCP do Protocolo de Continuidade

echo "Iniciando Amazon Q CLI com o Protocolo de Continuidade..."

# Verificar se o servidor está em execução
if ! curl -s http://localhost:8765/health > /dev/null; then
    echo "Servidor de continuidade não está em execução. Iniciando servidor..."
    cd "$(dirname "$0")"
    ./start_enhanced_server.sh
    echo ""
fi

# Definir a sessão de continuidade se não estiver definida
if [ -z "$CONTINUITY_SESSION" ]; then
    export CONTINUITY_SESSION="amazon-q-session"
    echo "Definindo CONTINUITY_SESSION=$CONTINUITY_SESSION"
fi

# Iniciar o Amazon Q CLI
echo "Iniciando Amazon Q CLI..."
echo "Use 'onde paramos?' para verificar o contexto atual"
echo ""
q chat
