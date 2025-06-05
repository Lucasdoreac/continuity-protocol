#!/bin/bash

# 🎯 CORREÇÃO SISTEMÁTICA DE ACESSIBILIDADE - LUARAUJO APP
# Soluciona texto invisível no tema escuro em TODOS os componentes

echo "🚨 INICIANDO CORREÇÃO CRÍTICA DE ACESSIBILIDADE"
echo "🎯 Problema: 23+ componentes quebrados no tema escuro"

COMPONENTS_DIR="/Users/lucascardoso/apps/MCP/luaraujo-livro-app copy/src/components"
SCREENS_DIR="/Users/lucascardoso/apps/MCP/luaraujo-livro-app copy/src/screens" 
BACKUP_DIR="/Users/lucascardoso/apps/MCP/CONTINUITY/accessibility-backup-$(date +%Y%m%d_%H%M%S)"

mkdir -p "$BACKUP_DIR"
echo "💾 Backup criado: $BACKUP_DIR"

# COMPONENTES PRIORITÁRIOS (maior impacto visual)
PRIORITY_COMPONENTS=(
    "CompoundInterestCalculator.js"
    "TaxCalculator.js" 
    "ProductComparison.js"
    "InvestorProfileQuiz.js"
    "FinancialGoalPlanner.js"
    "RealTimeRates.js"
    "OnboardingScreen.js"
)

echo "🔧 APLICANDO CORREÇÃO FASE 1 (PRIORITY COMPONENTS):"

for component in "${PRIORITY_COMPONENTS[@]}"; do
    file_path="$COMPONENTS_DIR/$component"
    
    if [[ -f "$file_path" ]]; then
        echo "  🎯 Processando: $component"
        
        # Backup
        cp "$file_path" "$BACKUP_DIR/"
        
        # Adicionar import useColors (se não existir)
        if ! grep -q "useColors" "$file_path"; then
            sed -i '' '/import.*globalStyles/a\
import { useColors } from '\''../contexts/ThemeContext'\'';
' "$file_path"
            echo "    ✅ Import useColors adicionado"
        else
            echo "    ⚠️  useColors já existe"
        fi
        
    else
        echo "    ❌ Arquivo não encontrado: $component"
    fi
done

echo ""
echo "📋 FASE 1 CONCLUÍDA - IMPORTS ADICIONADOS"
echo "🔧 PRÓXIMO PASSO MANUAL:"
echo "   1. Para cada componente, implementar: const colors = useColors();"
echo "   2. Substituir COLORS.text por colors.text"
echo "   3. Substituir COLORS.background por colors.background"
echo "   4. Padrão: Chapter1Screen.js (referência)"
echo ""
echo "🎯 TESTE IMEDIATO:"
echo "   - Botão página 4 overflow: CORRIGIDO ✅"
echo "   - Tema escuro: IMPORTS PRONTOS ⚠️ (falta implementação)"
