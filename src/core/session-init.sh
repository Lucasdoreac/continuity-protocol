#!/bin/bash

# SESSION INITIALIZER INTEGRADO
# Detecta automaticamente o melhor projeto para continuar

CONTINUITY_DIR="/Users/lucascardoso/apps/MCP/CONTINUITY"
AUTO_CONTINUITY="$CONTINUITY_DIR/auto-continuity.sh"

echo "🚀 SISTEMA DE CONTINUIDADE INTEGRADO"
echo "====================================="

# Verificar se há missões críticas pendentes
echo "🔍 Verificando missões críticas..."
critical_found=false

for critical_file in "$CONTINUITY_DIR/project-states"/*_critical_*.json; do
    if [ -f "$critical_file" ]; then
        project_name=$(echo "$(basename "$critical_file")" | cut -d'_' -f1)
        echo "🚨 MISSÃO CRÍTICA PENDENTE: $project_name"
        critical_found=true
    fi
done

if [ "$critical_found" = true ]; then
    echo ""
    echo "⚡ RECOMENDAÇÃO: Execute recovery automático:"
    echo "   $CONTINUITY_DIR/recovery.sh"
    echo ""
fi

# Listar projetos com sistema integrado
echo "📂 PROJETOS DISPONÍVEIS:"
$AUTO_CONTINUITY 2>/dev/null || echo "Sistema auto-continuity disponível"

echo ""
echo "💡 COMANDOS RECOMENDADOS:"
echo "   🔄 Recovery automático:    $CONTINUITY_DIR/recovery.sh"
echo "   🎯 Sessão específica:      $AUTO_CONTINUITY [projeto] session-start"
echo "   🆕 Novo projeto:           $AUTO_CONTINUITY [projeto] init"
echo "   🚨 Emergência:             $AUTO_CONTINUITY [projeto] emergency-save"
echo ""
