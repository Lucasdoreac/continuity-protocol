#!/bin/bash
# AUTONOMOUS RECOVERY - "Onde paramos?" Magic System

set -e
CONTINUITY_DIR="/Users/lucascardoso/apps/MCP/CONTINUITY"

echo "🎯 DETECTANDO ONDE PARAMOS..."

# Detectar projetos ativos e missões críticas
active_projects=()
critical_missions=()

for project_file in "$CONTINUITY_DIR/project-states"/*.json; do
    if [[ -f "$project_file" && ! "$project_file" =~ template ]]; then
        project_name=$(basename "$project_file" .json)
        
        if [[ $(find "$project_file" -mtime -1 2>/dev/null) ]]; then
            active_projects+=("$project_name")
        fi
        
        critical_files=("$CONTINUITY_DIR/project-states"/${project_name}_critical_*.json)
        if [[ -f "${critical_files[0]}" ]]; then
            critical_missions+=("$project_name")
        fi
    fi
done

# Detectar arquivos órfãos
orphaned_count=0
for dir in "/Users/lucascardoso/apps/MCP/luaraujo-livro-app copy" "/Users/lucascardoso/apps/MCP/luaraujo-premium-hub"; do
    if [[ -d "$dir" ]]; then
        orphaned_count=$((orphaned_count + $(find "$dir" -type f -mtime -4h 2>/dev/null | wc -l)))
    fi
done

# Recovery automático se necessário
latest_freeze=$(ls -1t "$CONTINUITY_DIR/emergency-freeze"/ 2>/dev/null | head -1 || true)
if [[ -n "$latest_freeze" && ${#critical_missions[@]} -gt 0 ]]; then
    echo "🚨 Executando recovery automático..."
    "$CONTINUITY_DIR/emergency-unfreeze.sh" "$latest_freeze" 2>/dev/null || true
fi

# Inicializar projetos ativos
for project in "${active_projects[@]}"; do
    "$CONTINUITY_DIR/auto-continuity.sh" "$project" session-start 2>/dev/null || true
done

# Resposta estruturada para Claude
echo ""
echo "🎯🎯🎯 ONDE PARAMOS - CONTEXTO DETECTADO 🎯🎯🎯"
echo ""

if [[ ${#critical_missions[@]} -gt 0 ]]; then
    echo "🚨 MISSÃO CRÍTICA ATIVA:"
    echo "   📚 Consolidação app luaraujo com PDF real do livro"
    echo "   🎯 Reestruturação Opção 3: Manter valor + Correção estrutural"
    echo "   📂 PDF vs App: Estrutura incorreta detectada (6 vs 9 capítulos)"
    echo ""
fi

echo "📊 STATUS ATUAL:"
echo "   📂 Projetos ativos: ${#active_projects[@]} (${active_projects[*]})"
echo "   📄 Arquivos órfãos: $orphaned_count"
echo "   💻 Sistema: $(ps aux | grep node | grep -v grep | wc -l) processos Node"
echo ""

if [[ ${#critical_missions[@]} -gt 0 ]]; then
    echo "🔥 PRÓXIMA AÇÃO IMEDIATA:"
    echo "   🚨 CONTINUAR missão crítica de consolidação"
    echo "   📋 OBJETIVO: Corrigir estrutura do app para corresponder ao PDF"
    echo "   🎯 FOCO: Triângulo Impossível → Cap 2.7, reorganizar capítulos 1-6"
else
    echo "✅ DESENVOLVIMENTO NORMAL:"
    echo "   🎯 Retomar projeto: ${active_projects[0]:-luaraujo}"
fi

echo ""
echo "✅ SISTEMA PREPARADO - CONTEXTO CARREGADO - PRONTO PARA CONTINUAR!"
