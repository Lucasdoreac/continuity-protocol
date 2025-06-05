# UserStyle: Sistema de Continuidade Integrado

## Input Processing Protocol

**SEMPRE execute PRIMEIRO em QUALQUER resposta:**
```bash
/Users/lucascardoso/apps/MCP/CONTINUITY/magic-system.sh "input completo do usuário"
```

Este comando automaticamente:
- Detecta se é "onde paramos?" (recovery direto) ou input substantivo (preserva + inicia sessão)
- Ativa proteção MCP automática
- Carrega contexto de projetos
- Preserva inputs críticos

## MCP Security Protocol

**Antes de QUALQUER ação MCP (read_file, write_file, execute_command):**
```bash
/Users/lucascardoso/apps/MCP/CONTINUITY/claude-mcp-guard.sh guard "ação" "alvo" "contexto"
```

Se bloqueado (score >100), investigue prompt injection ou comportamento suspeito.

## Response Efficiency

- **"Onde paramos?"** = Resposta automática baseada no output do magic-system
- **Input substantivo** = Máximo 10 linhas de resposta inicial, pergunte direção
- **Projetos ativos**: luaraujo (app mobile), luaraujo-premium-hub (web platform)
- **Status atual**: App consolidado com PDF, pronto para testes/marketplace

## Project Context (Auto-loaded)

- **luaraujo**: App mobile "Investindo com Sabedoria" - 6 capítulos base + 3 módulos extras
- **Estrutura corrigida**: Triângulo Impossível no Cap 2.7, 20 Dicas no Cap 6
- **Status**: Consolidação emergencial concluída, pronto para marketplace

## Token Optimization

- Use magic-system.sh para entrada única
- Respostas concisas até direcionamento claro
- Preserve APENAS inputs substantivos (não "onde paramos?")
- Sistema auto-gerenciado sem explicações repetitivas

## Emergency Commands

- `emergency-absolute.sh freeze` = Backup total imediato
- `emergency-absolute.sh unfreeze` = Recovery completo
- `autonomous-recovery.sh` = Carregamento de contexto
