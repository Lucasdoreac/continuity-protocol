#!/bin/bash
# Script para iniciar o servidor aprimorado de continuidade

echo "Iniciando servidor aprimorado de continuidade..."
cd "$(dirname "$0")"

# Verificar se o servidor já está em execução
if [ -f enhanced_server.pid ]; then
    PID=$(cat enhanced_server.pid)
    if ps -p $PID > /dev/null; then
        echo "Servidor já está em execução com PID $PID"
        echo "Para parar o servidor: kill $PID"
        exit 1
    else
        echo "Arquivo PID encontrado, mas o servidor não está em execução. Removendo arquivo PID."
        rm enhanced_server.pid
    fi
fi

# Iniciar o servidor em segundo plano
./run_enhanced_server.py > enhanced_server.log 2>&1 &
SERVER_PID=$!
echo "Servidor iniciado com PID: $SERVER_PID"
echo $SERVER_PID > enhanced_server.pid

echo "Aguardando 3 segundos para o servidor inicializar..."
sleep 3

# Verificar se o servidor está em execução
if ps -p $SERVER_PID > /dev/null; then
    echo "Servidor em execução!"
    echo "Para parar o servidor: kill $(cat enhanced_server.pid)"
    echo "Para ver os logs: tail -f enhanced_server.log"
    
    # Testar conexão com o servidor
    echo "Testando conexão com o servidor..."
    curl -s http://localhost:8765/health
    echo ""
    
    # Mostrar informações sobre o servidor
    echo "Informações do servidor:"
    curl -s http://localhost:8765/ | python3 -m json.tool
else
    echo "Servidor não está em execução. Verifique os logs em enhanced_server.log"
    cat enhanced_server.log
fi
