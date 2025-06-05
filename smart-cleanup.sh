#!/bin/bash

# 🧹 SMART CLEANUP - Limpeza inteligente para economia de tokens
# Remove dados desnecessários mantendo apenas o essencial

set -e

CONTINUITY_DIR="/Users/lucascardoso/apps/MCP/CONTINUITY"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")

echo "🧹 SMART CLEANUP - Otimização de tokens"

# 1. LOGS ANTIGOS
echo "📝 Limpando logs antigos..."
find "$CONTINUITY_DIR/logs" -name "*.log" -mtime +2 -delete 2>/dev/null || true

# 2. BACKUPS EXCESSIVOS
echo "💾 Removendo backups excessivos..."
find "$CONTINUITY_DIR/backups" -name "*.json" | sort -r | tail -n +6 | xargs rm -f 2>/dev/null || true
find "$CONTINUITY_DIR/emergency-backups" -name "*_emergency_*" | sort -r | tail -n +4 | xargs rm -rf 2>/dev/null || true

# 3. FREEZE ANTIGOS
echo "❄️ Limpando freezes antigos..."
find "$CONTINUITY_DIR/emergency-freeze" -name "20*" -type d -mtime +7 | head -5 | xargs rm -rf 2>/dev/null || true

# 4. COMPACTAR ESTADOS JSON
echo "📦 Compactando estados JSON..."
for json_file in "$CONTINUITY_DIR/project-states"/*.json; do
    if [[ -f "$json_file" && ! "$json_file" =~ template ]]; then
        jq -c '.' "$json_file" > "${json_file}.tmp" && mv "${json_file}.tmp" "$json_file" 2>/dev/null || true
    fi
done

# 5. RELATÓRIO DE LIMPEZA
total_space_saved=$(du -sh "$CONTINUITY_DIR" | cut -f1)
echo "✅ Limpeza completa - Espaço total: $total_space_saved"
echo "🎯 Sistema otimizado para economia de tokens"
