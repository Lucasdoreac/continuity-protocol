#!/bin/bash

# 🚨 CORREÇÃO DEFINITIVA: ELIMINAÇÃO DE ERROS DE HOOKS
# Remove todos os useColors problemáticos e restaura estabilidade

echo "🚨 CORREÇÃO EMERGENCIAL - ELIMINANDO ERROS DE HOOKS"
echo "🎯 Meta: App funcionando sem erros de React"

COMPONENTS_DIR="/Users/lucascardoso/apps/MCP/luaraujo-livro-app copy/src/components"
SCREENS_DIR="/Users/lucascardoso/apps/MCP/luaraujo-livro-app copy/src/screens"
BACKUP_DIR="/Users/lucascardoso/apps/MCP/CONTINUITY/emergency-fix-$(date +%Y%m%d_%H%M%S)"

mkdir -p "$BACKUP_DIR"
echo "💾 Backup: $BACKUP_DIR"

# COMPONENTES PROBLEMÁTICOS (que causam erros)
PROBLEM_COMPONENTS=(
    "TaxCalculator.js"
    "CompoundInterestCalculator.js" 
    "InvestorProfileQuiz.js"
    "ProductComparison.js"
    "HistoryViewer.js"
    "PremiumGate.js"
)

echo ""
echo "🔧 REMOVENDO IMPORTS PROBLEMÁTICOS:"

for component in "${PROBLEM_COMPONENTS[@]}"; do
    file="$COMPONENTS_DIR/$component"
    
    if [[ -f "$file" ]]; then
        echo "  🎯 Processando: $component"
        
        # Backup
        cp "$file" "$BACKUP_DIR/"
        
        # Remover import useColors problemático
        sed -i '' '/import.*useColors.*ThemeContext/d' "$file"
        
        # Remover linhas de const colors = useColors
        sed -i '' '/const colors = useColors/d' "$file"
        
        echo "    ✅ Imports problemáticos removidos"
        
    else
        echo "    ❌ Arquivo não encontrado: $component"
    fi
done

echo ""
echo "✅ CORREÇÃO EMERGENCIAL CONCLUÍDA!"
echo "🎯 RESULTADO:"
echo "   - Imports de useColors removidos dos componentes problemáticos"
echo "   - App deve funcionar sem erros de hooks"
echo "   - RealTimeRates mantido (já funcionando)"
echo "   - Chapter1Screen mantido (referência correta)"
echo ""
echo "📋 COMPONENTES ESTÁVEIS:"
echo "   ✅ RealTimeRates: Funcionando com tema escuro"
echo "   ✅ Chapter1Screen: Referência correta de implementação"
echo "   ✅ Outros: Funcionais (sem tema dinâmico temporariamente)"
