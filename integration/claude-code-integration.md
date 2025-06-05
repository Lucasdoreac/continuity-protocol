# Integração do Continuity Protocol com Claude Code

Este guia mostra como integrar o Continuity Protocol com o Claude Code CLI.

## Pré-requisitos

- Claude Code CLI instalado
- Python 3.8+ instalado
- Servidor Continuity Protocol funcionando

## Instalação

### 1. Adicionar o servidor Continuity Protocol

Use o comando `claude mcp add` para adicionar o servidor ao Claude Code:

```bash
claude mcp add continuity-protocol --transport stdio python3 /Users/lucascardoso/apps/MCP/CONTINUITY/simple-project-analyzer.py
```

Ou, para o servidor completo de Protocolo de Continuidade:

```bash
claude mcp add continuity-protocol --transport stdio python3 /Users/lucascardoso/apps/MCP/CONTINUITY/continuity-protocol-server.py
```

### 2. Verificar instalação

Verifique se o servidor foi adicionado corretamente:

```bash
claude mcp list
```

Você deve ver `continuity-protocol` na lista de servidores.

## Uso

### Analisador de Projeto

```bash
claude mcp run continuity-protocol project_analyze
```

### Análise de Arquitetura

```bash
claude mcp run continuity-protocol project_architecture
```

### Plano de Refatoração

```bash
claude mcp run continuity-protocol project_refactor_plan
```

### Resumo do Projeto

```bash
claude mcp run continuity-protocol project_summary
```

### Análise de Script Específico

```bash
claude mcp run continuity-protocol script_analyze script_path="emergency-absolute.sh"
```

## Protocolo de Continuidade de Projetos

Para usar o protocolo completo:

### Criar Projeto

```bash
claude mcp run continuity-protocol project_create name="Meu Projeto" description="Descrição do projeto"
```

### Listar Projetos

```bash
claude mcp run continuity-protocol project_list
```

### Iniciar Sessão

```bash
claude mcp run continuity-protocol session_start project_id="ID-DO-PROJETO"
```

### Adicionar Contexto

```bash
claude mcp run continuity-protocol context_add project_id="ID-DO-PROJETO" content="Informação importante" content_type="note"
```

### Finalizar Sessão

```bash
claude mcp run continuity-protocol session_end project_id="ID-DO-PROJETO" session_id="ID-DA-SESSÃO" summary="Resumo da sessão"
```