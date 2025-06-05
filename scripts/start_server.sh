#!/bin/bash
# Script para iniciar o servidor de continuidade em segundo plano

echo "Iniciando servidor de continuidade em segundo plano..."
continuity server > continuity_server.log 2>&1 &
SERVER_PID=$!
echo "Servidor iniciado com PID: $SERVER_PID"
echo $SERVER_PID > server.pid
echo "Aguardando 3 segundos para o servidor inicializar..."
sleep 3
echo "Verificando se o servidor está em execução..."
if ps -p $SERVER_PID > /dev/null; then
    echo "Servidor em execução!"
    echo "Para parar o servidor: kill $(cat server.pid)"
    echo "Para ver os logs: tail -f continuity_server.log"
else
    echo "Servidor não está em execução. Verifique os logs em continuity_server.log"
fi
