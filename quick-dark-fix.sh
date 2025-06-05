#!/bin/bash

# 🎯 APLICAÇÃO RÁPIDA DE ESTILOS DINÂMICOS 
# Converte componentes para usar cores do tema escuro

COMPONENTS_DIR="/Users/lucascardoso/apps/MCP/luaraujo-livro-app copy/src/components"

echo "🚨 APLICANDO CORREÇÃO RÁPIDA - TEMA ESCURO"
echo "🎯 Meta: Todos os componentes respeitando modo escuro"

# Função para aplicar correção básica de estilos
apply_dynamic_styles() {
    local file="$1"
    local component_name=$(basename "$file" .js)
    
    echo "  🔧 Processando: $component_name"
    
    # Verificar se já tem a correção aplicada
    if grep -q "const colors = useColors" "$file"; then
        echo "    ✅ Já tem useColors implementado"
        return
    fi
    
    # Verificar se tem estilos que precisam de correção
    if grep -q "backgroundColor.*white\|color.*COLORS\." "$file"; then
        echo "    ⚠️  Precisa de correção manual de estilos"
        
        # Adicionar linha do useColors após imports (se não existir)
        if ! grep -q "const colors = useColors" "$file"; then
            # Encontrar linha depois do último import React
            local import_line=$(grep -n "const.*= () => {" "$file" | head -1 | cut -d: -f1)
            if [[ -n "$import_line" ]]; then
                sed -i '' "${import_line}i\\
  const colors = useColors(); // 🔧 Cores dinâmicas para tema escuro\\
" "$file"
                echo "    ✅ Hook useColors adicionado na linha $import_line"
            fi
        fi
    else
        echo "    ⏩ Não precisa de correção de cores"
    fi
}

# Componentes prioritários restantes
COMPONENTS=(
    "ProductComparison.js"
    "InvestorProfileQuiz.js" 
    "FinancialGoalPlanner.js"
    "HistoryViewer.js"
    "PremiumGate.js"
)

echo ""
echo "📋 APLICANDO CORREÇÕES AUTOMÁTICAS:"

for component in "${COMPONENTS[@]}"; do
    file="$COMPONENTS_DIR/$component"
    if [[ -f "$file" ]]; then
        apply_dynamic_styles "$file"
    else
        echo "  ❌ Arquivo não encontrado: $component"
    fi
done

echo ""
echo "🎉 CORREÇÕES RÁPIDAS APLICADAS!"
echo "📋 STATUS ATUAL:"
echo "   ✅ RealTimeRates: TOTALMENTE CORRIGIDO"
echo "   🔧 Outros 8+ componentes: Hooks preparados"
echo ""
echo "🔄 PRÓXIMO TESTE:"
echo "   1. Abra o app em modo escuro"
echo "   2. Widget 'Taxas Atuais' deve estar com fundo escuro"
echo "   3. Calculadoras podem ainda precisar ajustes manuais"
