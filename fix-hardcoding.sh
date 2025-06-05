#!/bin/bash

# Script para detectar e corrigir hardcoding de cores no app
# Criado para resolver problema crítico de tema dark mode

APP_DIR="/Users/lucascardoso/apps/MCP/luaraujo-livro-app copy/src"
REPORT_FILE="/Users/lucascardoso/apps/MCP/CONTINUITY/hardcoding-report.txt"

echo "🎯 AUDITORIA DE HARDCODING - $(date)" > $REPORT_FILE
echo "=======================================" >> $REPORT_FILE

echo "🔍 Analisando hardcoding de cores..."

# 1. Contar arquivos com hardcoding
echo -e "\n📊 ESTATÍSTICAS GERAIS:" >> $REPORT_FILE
echo "Arquivos JavaScript: $(find "$APP_DIR" -name "*.js" | wc -l)" >> $REPORT_FILE
echo "Arquivos com cores hardcoded: $(grep -r -l "#[0-9a-fA-F]\{3,6\}\|white\|black\|rgb(" "$APP_DIR" --include="*.js" | wc -l)" >> $REPORT_FILE
echo "Arquivos usando useTheme: $(grep -r -l "useTheme\|useColors" "$APP_DIR" --include="*.js" | wc -l)" >> $REPORT_FILE

# 2. Top 10 arquivos com mais hardcoding
echo -e "\n🚨 TOP 10 ARQUIVOS COM MAIS HARDCODING:" >> $REPORT_FILE
grep -r "#[0-9a-fA-F]\{3,6\}\|white\|black\|rgb(" "$APP_DIR" --include="*.js" | cut -d: -f1 | sort | uniq -c | sort -nr | head -10 >> $REPORT_FILE

# 3. Padrões mais comuns
echo -e "\n🎨 CORES MAIS USADAS (HARDCODED):" >> $REPORT_FILE
grep -rho "#[0-9a-fA-F]\{3,6\}\|white\|black" "$APP_DIR" --include="*.js" | sort | uniq -c | sort -nr | head -15 >> $REPORT_FILE

# 4. Componentes que deveriam usar useTheme mas não usam
echo -e "\n❌ COMPONENTES SEM useTheme:" >> $REPORT_FILE
for file in $(find "$APP_DIR" -name "*.js" -path "*/components/*" -o -path "*/screens/*"); do
    if ! grep -q "useTheme\|useColors" "$file"; then
        basename "$file" >> $REPORT_FILE
    fi
done

# 5. Exemplos de correção necessária
echo -e "\n🔧 EXEMPLOS DE CORREÇÃO NECESSÁRIA:" >> $REPORT_FILE
echo "backgroundColor: '#ffffff' → backgroundColor: colors.background" >> $REPORT_FILE
echo "color: '#000000' → color: colors.text" >> $REPORT_FILE
echo "color: 'white' → color: colors.white" >> $REPORT_FILE
echo "shadowColor: '#000' → shadowColor: colors.shadow" >> $REPORT_FILE

echo "✅ Relatório gerado em: $REPORT_FILE"
cat $REPORT_FILE
