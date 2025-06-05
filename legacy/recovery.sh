#!/bin/bash

# RECOVERY SCRIPT INTEGRADO - Script de recuperação pós-interrupção
# Usa o novo sistema auto-continuity integrado

set -e

CONTINUITY_DIR="/Users/lucascardoso/apps/MCP/CONTINUITY"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")

echo "🔄 RECOVERY MODE INTEGRADO - $TIMESTAMP"
echo "🎯 MISSÃO: Consolidação app luaraujo com PDF real"
echo ""

# Verificar se há projetos para recuperação
echo "📂 Projetos disponíveis para recuperação:"
for project_file in "$CONTINUITY_DIR/project-states"/*.json; do
    if [ -f "$project_file" ]; then
        project_name=$(basename "$project_file" .json)
        if [ "$project_name" != "project-template" ]; then
            echo "  🎯 $project_name"
            
            # Verificar se há estado crítico
            critical_files=("$CONTINUITY_DIR/project-states"/${project_name}_critical_*.json)
            if [ -f "${critical_files[0]}" ]; then
                echo "    🚨 MISSÃO CRÍTICA PENDENTE"
            fi
        fi
    fi
done

echo ""
echo "🚨 MISSÃO CRÍTICA IDENTIFICADA:"
echo "  📚 Consolidar estrutura do app com PDF do livro"
echo "  🎯 Reestruturação Opção 3 - Manter valor + Correção"
echo "  📂 PDF: /Users/lucascardoso/apps/MCP/luaraujo-livro-app copy/"

# Verificar se PDF foi colocado no local correto
PDF_PATH="/Users/lucascardoso/apps/MCP/luaraujo-livro-app copy/Investindo com Sabedoria - Luciana Araujo.pdf"
if [ -f "$PDF_PATH" ]; then
    echo "✅ PDF encontrado no local correto"
else
    echo "❌ PDF NÃO encontrado em: $PDF_PATH"
    echo "⚠️  AÇÃO NECESSÁRIA: Colocar PDF no local correto antes de continuar"
fi

echo ""
echo "🔧 PRÓXIMAS AÇÕES RECOMENDADAS:"
echo "1. $CONTINUITY_DIR/auto-continuity.sh luaraujo recovery"
echo "2. Verificar estado atual do app (estrutura vs PDF)"
echo "3. Executar reestruturação Opção 3:"
echo "   - Reorganizar Caps 1-6 para corresponder ao PDF"
echo "   - Manter Caps 7-9 como 'MÓDULOS EXTRAS'"
echo "   - Mover Triângulo Impossível para Chapter2Screen seção 2.7"
echo "   - Adicionar '20 Dicas Práticas' no Cap 6"
echo "4. Testar e validar estrutura corrigida"
echo "5. Preparar para marketplace como produto pago"

echo ""
echo "💡 SISTEMA DE CONTINUIDADE INTEGRADO:"
echo "  📥 Estados salvos automaticamente"
echo "  🧠 Memória MCP integrada"
echo "  ⚡ Recuperação robusta implementada"
echo "  🔄 Auto-detecção de inconsistências"

echo ""
echo "🎉 RECOVERY SCRIPT EXECUTADO COM SUCESSO"
echo "📋 Execute: $CONTINUITY_DIR/auto-continuity.sh luaraujo recovery"
