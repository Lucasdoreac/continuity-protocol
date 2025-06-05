# Sistema de Memória Compartilhada para MCP CONTINUITY

Este sistema permite que você mantenha o contexto de trabalho entre diferentes terminais e o Claude Desktop, respondendo automaticamente a perguntas como "onde paramos?" ou "em que estamos trabalhando?".

## Visão Geral

O sistema de memória compartilhada para MCP CONTINUITY consiste em:

1. **Gerenciador de Memória Compartilhada**: Armazena e gerencia o contexto de trabalho
2. **Integração com AWS CLI**: Permite usar o contexto no Amazon Q CLI
3. **Integração com Claude Desktop**: Permite usar o contexto no Claude Desktop
4. **Hooks de Continuidade**: Detectam automaticamente perguntas sobre continuidade

## Instalação

Para instalar o sistema completo:

```bash
/Users/lucascardoso/apps/MCP/CONTINUITY/mcp-continuity-integration.sh install
```

Este comando:
1. Inicializa o sistema de memória compartilhada
2. Configura hooks para detectar perguntas de continuidade
3. Cria configurações MCP para AWS CLI e Claude Desktop
4. Configura sessões iniciais para AWS CLI e Claude Desktop
5. Adiciona repositórios relevantes ao contexto

## Uso

### Iniciar os Servidores MCP

```bash
/Users/lucascardoso/apps/MCP/CONTINUITY/mcp-continuity-integration.sh start
```

### Verificar Status

```bash
/Users/lucascardoso/apps/MCP/CONTINUITY/mcp-continuity-integration.sh status
```

### Parar os Servidores MCP

```bash
/Users/lucascardoso/apps/MCP/CONTINUITY/mcp-continuity-integration.sh stop
```

### Testar a Integração

```bash
/Users/lucascardoso/apps/MCP/CONTINUITY/mcp-continuity-integration.sh test
```

## Usando com Amazon Q CLI

Após a instalação, você pode usar o Amazon Q CLI com o sistema de memória compartilhada:

```bash
q chat --mcp-server http://localhost:3456
```

Quando você perguntar "onde paramos?" ou "em que estamos trabalhando?", o sistema automaticamente fornecerá o contexto atual.

## Usando com Claude Desktop

Após a instalação, o Claude Desktop estará configurado para usar o sistema de memória compartilhada. Basta abrir o Claude Desktop e fazer perguntas como "onde paramos?" para obter o contexto atual.

## Gerenciando o Contexto Manualmente

Você pode gerenciar o contexto manualmente usando o script `shared-memory-manager.sh`:

### Criar uma Nova Sessão

```bash
/Users/lucascardoso/apps/MCP/CONTINUITY/shared-memory-manager.sh create-session "minha-sessao" "Descrição da sessão"
```

### Atualizar o Foco Atual

```bash
/Users/lucascardoso/apps/MCP/CONTINUITY/shared-memory-manager.sh focus "minha-sessao" "Trabalhando no recurso X"
```

### Adicionar um Projeto Ativo

```bash
/Users/lucascardoso/apps/MCP/CONTINUITY/shared-memory-manager.sh add-project "minha-sessao" "nome-do-projeto" "/caminho/do/projeto"
```

### Listar Sessões Disponíveis

```bash
/Users/lucascardoso/apps/MCP/CONTINUITY/shared-memory-manager.sh list-sessions
```

### Ver Detalhes de uma Sessão

```bash
/Users/lucascardoso/apps/MCP/CONTINUITY/shared-memory-manager.sh details "minha-sessao"
```

### Ver Contexto Atual

```bash
/Users/lucascardoso/apps/MCP/CONTINUITY/shared-memory-manager.sh current-context
```

## Estrutura de Diretórios

- `/Users/lucascardoso/apps/MCP/CONTINUITY/shared-memory`: Diretório principal da memória compartilhada
  - `/sessions`: Armazena contextos de sessões individuais
  - `current-context.json`: Contexto atual do sistema
  - `memory-manager.log`: Log do gerenciador de memória

## Repositórios Integrados

O sistema está configurado para trabalhar com os seguintes repositórios:

- https://github.com/Lucasdoreac/mcp-continuity-tool/

## Solução de Problemas

Se encontrar problemas com o sistema de memória compartilhada:

1. Verifique os logs:
   ```bash
   cat /Users/lucascardoso/apps/MCP/CONTINUITY/shared-memory/memory-manager.log
   ```

2. Reinicie os servidores MCP:
   ```bash
   /Users/lucascardoso/apps/MCP/CONTINUITY/mcp-continuity-integration.sh restart
   ```

3. Verifique se os hooks estão funcionando:
   ```bash
   /Users/lucascardoso/apps/MCP/CONTINUITY/hooks/aws-cli-hook.sh "onde paramos?"
   ```

4. Verifique as configurações MCP:
   ```bash
   cat ~/.aws/mcp/continuity.json
   cat ~/.config/claude/claude_desktop_config.json
   ```
