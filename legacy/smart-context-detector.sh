#!/bin/bash
# SMART CONTEXT DETECTOR - Detecta se precisa recovery

CONTINUITY_DIR="/Users/lucascardoso/apps/MCP/CONTINUITY"
needs_recovery=false
summary=""

# Missões críticas
critical_count=$(find "$CONTINUITY_DIR/project-states" -name "*_critical_*.json" 2>/dev/null | wc -l)
if [[ $critical_count -gt 0 ]]; then
    needs_recovery=true
    summary="🚨 $critical_count missão(ões) crítica(s). "
fi

# Freezes disponíveis
freeze_count=$(ls -1 "$CONTINUITY_DIR/emergency-freeze"/ 2>/dev/null | wc -l)
if [[ $freeze_count -gt 0 ]]; then
    needs_recovery=true
    summary="$summary❄️ $freeze_count freeze(s). "
fi

# Projetos inativos com atividade recente
inactive_count=0
for project_file in "$CONTINUITY_DIR/project-states"/*.json; do
    if [[ -f "$project_file" && ! "$project_file" =~ template && $(find "$project_file" -mtime -1 2>/dev/null) ]]; then
        project_name=$(basename "$project_file" .json)
        if ! ps aux | grep -q "$project_name" 2>/dev/null; then
            inactive_count=$((inactive_count + 1))
        fi
    fi
done

if [[ $inactive_count -gt 0 ]]; then
    needs_recovery=true
    summary="$summary📂 $inactive_count projeto(s) inativos. "
fi

# Resultado
if [[ $needs_recovery == true ]]; then
    echo "NEEDS_RECOVERY:true"
    echo "SUMMARY:$summary"
    echo "ACTION:EXECUTE_AUTONOMOUS_RECOVERY"
else
    echo "NEEDS_RECOVERY:false"
    echo "SUMMARY:Sistema normal."
    echo "ACTION:CONTINUE_NORMAL"
fi
