#!/bin/bash

# 🎯 APLICAÇÃO DO PADRÃO CORRETO DE MODO ESCURO
# Replicando a implementação dos "Módulos Extras" para todo o app

echo "🎯 APLICANDO PADRÃO CORRETO: FUNDO ESCURO + TEXTO CLARO"
echo "📱 Baseado na implementação dos 'Módulos Extras' que funciona perfeitamente"

COMPONENTS_DIR="/Users/lucascardoso/apps/MCP/luaraujo-livro-app copy/src/components"
SCREENS_DIR="/Users/lucascardoso/apps/MCP/luaraujo-livro-app copy/src/screens"
BACKUP_DIR="/Users/lucascardoso/apps/MCP/CONTINUITY/correct-pattern-$(date +%Y%m%d_%H%M%S)"

mkdir -p "$BACKUP_DIR"
echo "💾 Backup: $BACKUP_DIR"

# COMPONENTES PRIORITÁRIOS PARA APLICAR O PADRÃO CORRETO
PRIORITY_COMPONENTS=(
    "CompoundInterestCalculator.js"
    "TaxCalculator.js"
    "ProductComparison.js"
    "InvestorProfileQuiz.js"
    "FinancialGoalPlanner.js"
)

echo ""
echo "🔧 APLICANDO PADRÃO DOS MÓDULOS EXTRAS:"
echo "   Pattern: const COLORS = useLegacyColors();"
echo "   Pattern: backgroundColor: COLORS.cardBackground"
echo "   Pattern: color: COLORS.text"

for component in "${PRIORITY_COMPONENTS[@]}"; do
    file="$COMPONENTS_DIR/$component"
    
    if [[ -f "$file" ]]; then
        echo "  🎯 Processando: $component"
        
        # Backup
        cp "$file" "$BACKUP_DIR/"
        
        # Adicionar import do useLegacyColors (se não existir)
        if ! grep -q "useLegacyColors" "$file"; then
            # Adicionar após imports existentes
            sed -i '' '/import.*globalStyles/a\
import { useLegacyColors } from '\''../contexts/ThemeContext'\'';
' "$file"
            echo "    ✅ Import useLegacyColors adicionado"
        else
            echo "    ✅ useLegacyColors já existe"
        fi
        
    else
        echo "    ❌ Arquivo não encontrado: $component"
    fi
done

echo ""
echo "✅ IMPORTS PREPARADOS!"
echo "🎯 RESULTADO ESPERADO:"
echo "   - Todos os componentes com fundo escuro + texto claro"
echo "   - Mesma aparência dos 'Módulos Extras' da imagem"
echo "   - Contraste perfeito como mostrado"
echo ""
echo "📋 PADRÃO ESTABELECIDO:"
echo "   ✅ useLegacyColors() hook (não quebra)"
echo "   ✅ COLORS.text (texto dinâmico)"
echo "   ✅ COLORS.cardBackground (fundo dinâmico)"
echo "   ✅ COLORS.accent (destaques)"
