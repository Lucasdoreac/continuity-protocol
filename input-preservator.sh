#!/bin/bash
# INPUT PRESERVATOR - Preserva inputs críticos antes de qualquer processamento

CONTINUITY_DIR="/Users/lucascardoso/apps/MCP/CONTINUITY"
INPUT_LOG="$CONTINUITY_DIR/input-preservation.log"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")

preserve_input() {
    local user_input="$1"
    
    echo "[$TIMESTAMP] USER_INPUT_RAW:" >> "$INPUT_LOG"
    echo "$user_input" >> "$INPUT_LOG"
    echo "--- END_INPUT ---" >> "$INPUT_LOG"
    echo "" >> "$INPUT_LOG"
    
    echo "✅ Input preservado: $INPUT_LOG"
}

# Uso: ./input-preservator.sh "texto do usuário"
if [[ $# -gt 0 ]]; then
    preserve_input "$*"
fi
