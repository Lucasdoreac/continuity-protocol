#!/bin/bash

# EMERGENCY SAVE INTEGRADO - Script de salvamento de emergência
# Usa o novo sistema auto-continuity integrado

set -e

CONTINUITY_DIR="/Users/lucascardoso/apps/MCP/CONTINUITY"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")

echo "🚨 EMERGENCY SAVE INTEGRADO - $TIMESTAMP"

# Identificar projetos ativos
echo "📥 Identificando projetos ativos..."

for project_file in "$CONTINUITY_DIR/project-states"/*.json; do
    if [ -f "$project_file" ]; then
        project_name=$(basename "$project_file" .json)
        echo "📥 Salvando estado: $project_name"
        
        # Executar emergency-save para o projeto
        if [ "$project_name" != "project-template" ]; then
            "$CONTINUITY_DIR/auto-continuity.sh" "$project_name" emergency-save 2>/dev/null || echo "⚠️  Aviso: Não foi possível salvar $project_name"
        fi
    fi
done

echo ""
echo "✅ EMERGENCY SAVE INTEGRADO COMPLETO - $TIMESTAMP"
echo "📂 Todos os projetos salvos com sistema integrado"
echo "🔧 Use auto-continuity.sh [projeto] recovery para recuperar"
