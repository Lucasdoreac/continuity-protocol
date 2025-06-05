#!/bin/bash
# Script para iniciar o Continuity Protocol e carregar o plano de retomada

echo "🚀 Iniciando Continuity Protocol e carregando plano de retomada..."

# Verificar se os servidores MCP estão em execução
echo "📊 Verificando servidores MCP..."

# Verificar PID 4421 (novo servidor)
if ps -p 4421 > /dev/null; then
    echo "✅ Servidor MCP novo (PID 4421) está em execução"
else
    echo "❌ Servidor MCP novo não está em execução. Iniciando..."
    cd /Users/lucascardoso/continuity-protocol
    nohup python3 mcp-server.py > mcp-server.log 2>&1 &
    echo $! > mcp-server.pid
    echo "✅ Servidor MCP novo iniciado com PID $!"
fi

# Verificar PID 4422 (servidor legado)
if ps -p 4422 > /dev/null; then
    echo "✅ Servidor MCP legado (PID 4422) está em execução"
else
    echo "❌ Servidor MCP legado não está em execução. Iniciando..."
    cd /Users/lucascardoso/apps/MCP/CONTINUITY
    nohup python3 mcp-continuity-server-fastmcp.py > mcp-continuity-server.log 2>&1 &
    echo $! > mcp-continuity-server.pid
    echo "✅ Servidor MCP legado iniciado com PID $!"
fi

# Verificar se o plano de retomada existe
PLANO_PATH="/Users/lucascardoso/continuity-protocol/plano_retomada.md"
if [ -f "$PLANO_PATH" ]; then
    echo "✅ Plano de retomada encontrado em $PLANO_PATH"
else
    echo "❌ Plano de retomada não encontrado. Algo está errado."
    exit 1
fi

# Atualizar a sessão para garantir que o plano seja acessível
echo "📝 Atualizando sessão para garantir acesso ao plano..."
SESSION_FILE="/Users/lucascardoso/continuity-protocol/sessions/default-session.json"
if [ -f "$SESSION_FILE" ]; then
    # Garantir que o arquivo de sessão tem as informações corretas
    # (Já foi atualizado anteriormente, então apenas verificamos)
    if grep -q "plano_retomada.md" "$SESSION_FILE"; then
        echo "✅ Sessão já está configurada corretamente"
    else
        echo "⚠️ Sessão precisa ser atualizada. Por favor, execute o Claude Desktop novamente."
    fi
else
    echo "❌ Arquivo de sessão não encontrado. Algo está errado."
    exit 1
fi

# Instruções para o usuário
echo ""
echo "🎯 CONTINUITY PROTOCOL PRONTO PARA USO"
echo "======================================="
echo "Para continuar o desenvolvimento com o Amazon Q CLI:"
echo "1. Abra um novo terminal"
echo "2. Execute: q chat"
echo "3. Digite: onde paramos com o Continuity Protocol?"
echo ""
echo "O Amazon Q CLI carregará automaticamente o contexto e o plano de retomada."
echo "Você pode continuar o desenvolvimento de onde parou."
echo ""
echo "📋 Próximos passos (conforme plano):"
echo "1. Auditoria técnica dos PIDs 4421 e 4422"
echo "2. Implementação de safeguards contra operações extensas"
echo "3. Estabelecimento do protocolo de coordenação Amazon Q CLI + Claude Desktop"
echo "4. Desenvolvimento incremental controlado em chunks"
echo ""
echo "✅ Tudo pronto! Boa sorte com o desenvolvimento!"
