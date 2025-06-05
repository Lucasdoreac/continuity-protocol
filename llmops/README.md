# LLM Timesheet - Sistema de "Bater o Ponto" para LLMs

Um sistema que registra e organiza automaticamente as contribuições de diferentes LLMs em um projeto, permitindo rastrear quem fez o quê, quando e por quê.

## Visão Geral

O LLM Timesheet fornece uma maneira estruturada de:

1. Registrar o início e fim de tarefas realizadas por LLMs
2. Detectar automaticamente arquivos modificados durante uma tarefa
3. Organizar contribuições por sprint
4. Gerar relatórios detalhados sobre o trabalho realizado
5. Integrar com servidores MCP para uso em fluxos de trabalho baseados em protocolo

Este sistema resolve o problema de desorganização em projetos onde múltiplos LLMs colaboram, permitindo um registro claro e estruturado de todas as contribuições.

## Estrutura do Sistema

```
llmops/
├── timesheets/     # Registros detalhados de cada tarefa
├── sprints/        # Dados de sprints
├── reports/        # Relatórios gerados
├── config.json     # Configurações do sistema
├── llm_timesheet.py # Sistema principal
├── llm-timesheet-mcp.py # Adaptador para MCP
└── install-llm-timesheet.sh # Script de instalação
```

## Instalação

Para instalar o LLM Timesheet em qualquer projeto:

```bash
# Uso básico (instala no diretório atual)
./llmops/install-llm-timesheet.sh

# Instalar em um diretório específico
./llmops/install-llm-timesheet.sh /caminho/para/seu/projeto
```

Isso criará toda a estrutura necessária e um script auxiliar `llm-punch.sh` para uso rápido.

## Uso Básico (CLI)

### Iniciar uma tarefa (punch in)

```bash
./llm-timesheet punch-in --llm "claude" --task "Implementar feature X" --context "Contexto opcional"
```

Ou usando o script auxiliar:

```bash
./llm-punch.sh in claude "Implementar feature X"
```

### Finalizar uma tarefa (punch out)

```bash
./llm-timesheet punch-out --task-id "UUID-da-tarefa" --summary "Implementei a feature X com testes" --detect-files
```

Ou usando o script auxiliar (que detecta a tarefa atual automaticamente):

```bash
./llm-punch.sh out "Implementei a feature X com testes"
```

### Gerar relatório do sprint atual

```bash
./llm-timesheet report
```

Ou:

```bash
./llm-punch.sh report
```

### Finalizar o sprint atual

```bash
./llm-timesheet finish-sprint --summary "Sprint focado em implementar features X, Y e Z"
```

Ou:

```bash
./llm-punch.sh finish "Sprint focado em implementar features X, Y e Z"
```

## Integração com MCP

O sistema inclui uma integração completa com o protocolo MCP (Model Context Protocol), permitindo que servidores MCP ofereçam ferramentas para gerenciar o timesheet.

### Ferramentas MCP Disponíveis

- `llm_punch_in` - Registra o início de uma tarefa
- `llm_punch_out` - Registra o fim de uma tarefa
- `llm_sprint_report` - Gera relatório do sprint atual
- `llm_finish_sprint` - Finaliza o sprint atual
- `llm_active_tasks` - Lista tarefas ativas
- `llm_task_details` - Obtém detalhes de uma tarefa
- `llm_auto_punch_in` - Inicia uma tarefa com detecção automática de contexto
- `llm_auto_punch_out` - Finaliza uma tarefa com detecção automática de arquivos
- `llm_auto_session` - Executa uma sessão completa em uma única chamada

### Exemplo de Uso com FastMCP

```python
from mcp.server.fastmcp import FastMCP
from llmops.llm_timesheet_mcp import LLMTimesheetMCP

mcp = FastMCP("MeuServidor")
timesheet_mcp = LLMTimesheetMCP()

@mcp.tool()
def punch_in_tool(llm_name: str, task_description: str) -> dict:
    """Registra o início de uma tarefa"""
    return timesheet_mcp.punch_in(llm_name, task_description)

# Executar servidor
mcp.run(transport="stdio")
```

Um exemplo completo está disponível em `/Users/lucascardoso/apps/MCP/CONTINUITY/mcp-continuity-server-integrated.py`.

## Configuração

O sistema é configurado através do arquivo `config.json`:

```json
{
  "project_name": "nome-do-projeto",
  "current_sprint": "sprint-1",
  "sprint_duration_days": 7,
  "known_llms": ["claude", "gpt-4", "gemini", "llama"],
  "timesheet_format": "json",
  "auto_organize": true,
  "organization_rules": {
    "code": ["*.py", "*.js", "*.html", "*.css", "*.sh"],
    "documentation": ["*.md", "README*", "*.txt"],
    "configuration": ["*.json", "*.yml", "*.yaml", "*.toml"],
    "data": ["*.csv", "*.json", "*.xml"]
  }
}
```

## Relatórios

Os relatórios de sprint incluem:

- Estatísticas de tarefas (total, concluídas, em andamento)
- Lista de contribuidores com tempo total e tarefas realizadas
- Arquivos modificados, organizados por categoria
- Resumo de todas as tarefas do sprint

Os relatórios são gerados em formato JSON e salvos no diretório `reports/`.

## Casos de Uso

1. **Rastreamento de Contribuições**: Entenda quais LLMs trabalharam em quais partes do projeto
2. **Métricas de Produtividade**: Analise quanto tempo cada LLM gasta em diferentes tipos de tarefas
3. **Documentação Automática**: Gere registros detalhados de todas as mudanças no projeto
4. **Continuidade entre Sessões**: Permita que um LLM continue o trabalho de outro com contexto completo
5. **Integração DevOps/LLMOps**: Conecte o trabalho dos LLMs a pipelines de CI/CD

---

Desenvolvido como parte do sistema MCP Continuity para fornecer rastreabilidade e organização para contribuições de LLMs.
EOL < /dev/null