#!/bin/bash

# 🚨 CORREÇÃO CRÍTICA: HOOKS FORA DE COMPONENTES
# Corrige erros "Invalid hook call" causados por hooks mal posicionados

echo "🚨 CORRIGINDO HOOKS INCORRETOS"
echo "🎯 Problema: useColors() fora das funções dos componentes"

COMPONENTS_DIR="/Users/lucascardoso/apps/MCP/luaraujo-livro-app copy/src/components"
BACKUP_DIR="/Users/lucascardoso/apps/MCP/CONTINUITY/hook-errors-backup-$(date +%Y%m%d_%H%M%S)"

mkdir -p "$BACKUP_DIR"
echo "💾 Backup: $BACKUP_DIR"

# Componentes com hooks incorretos identificados
BROKEN_COMPONENTS=(
    "TaxCalculator.js"
    "HistoryViewer.js" 
    "CompoundInterestCalculator.js"
    "InvestorProfileQuiz.js"
    "ProductComparison.js"
)

echo ""
echo "🔧 CORRIGINDO HOOKS INCORRETOS:"

for component in "${BROKEN_COMPONENTS[@]}"; do
    file="$COMPONENTS_DIR/$component"
    
    if [[ -f "$file" ]]; then
        echo "  🎯 Processando: $component"
        
        # Backup
        cp "$file" "$BACKUP_DIR/"
        
        # Remover linhas problemáticas de hooks fora de componentes
        # Pattern: "  const colors = useColors" (hook fora do componente)
        sed -i '' '/^  const colors = useColors/d' "$file"
        sed -i '' '/^const colors = useColors/d' "$file"
        
        echo "    ✅ Hooks incorretos removidos"
        
    else
        echo "    ❌ Arquivo não encontrado: $component"
    fi
done

echo ""
echo "✅ CORREÇÃO CONCLUÍDA!"
echo "🎯 RESULTADO:"
echo "   - Hooks incorretos removidos"
echo "   - Erros 'Invalid hook call' devem parar"
echo "   - App deve voltar a funcionar"
echo ""
echo "📋 PRÓXIMO PASSO:"
echo "   - Implementar hooks CORRETAMENTE dentro dos componentes"
echo "   - Usar apenas Chapter1Screen.js como referência"
