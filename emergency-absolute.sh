#!/bin/bash

# 🚨 COMANDO DE EMERGÊNCIA ABSOLUTO
# Use IMEDIATAMENTE quando algo der errado

set -e
CONTINUITY_DIR="/Users/lucascardoso/apps/MCP/CONTINUITY"
COMMAND="$1"

echo "🚨🚨🚨 EMERGÊNCIA ABSOLUTA 🚨🚨🚨"

case "$COMMAND" in
    "freeze"|"")
        echo "❄️ EXECUTANDO FREEZE TOTAL..."
        "$CONTINUITY_DIR/emergency-freeze.sh"
        "$CONTINUITY_DIR/smart-cleanup.sh"
        echo "🎯 Se chat falhou, abra NOVO CHAT e execute:"
        echo "/Users/lucascardoso/apps/MCP/CONTINUITY/emergency-absolute.sh unfreeze"
        ;;
        
    "unfreeze")
        echo "🔄 EXECUTANDO UNFREEZE..."
        latest_freeze=$(ls -1t "$CONTINUITY_DIR/emergency-freeze"/ 2>/dev/null | head -1)
        
        if [[ -n "$latest_freeze" ]]; then
            echo "📂 Usando freeze: $latest_freeze"
            "$CONTINUITY_DIR/emergency-unfreeze.sh" "$latest_freeze"
            echo "✅ RECOVERY COMPLETO! Continue normalmente."
        else
            echo "❌ Nenhum freeze encontrado."
        fi
        ;;
        
    "status")
        echo "📊 STATUS:"
        echo "Projetos: $(ls -1 "$CONTINUITY_DIR/project-states"/*.json 2>/dev/null | wc -l)"
        echo "Freezes: $(ls -1 "$CONTINUITY_DIR/emergency-freeze"/ 2>/dev/null | wc -l)"
        echo "Espaço: $(du -sh "$CONTINUITY_DIR" | cut -f1)"
        ;;
        
    *)
        echo "USO: $0 [freeze|unfreeze|status]"
        echo "🚨 EMERGÊNCIA: $0 freeze"
        ;;
esac
