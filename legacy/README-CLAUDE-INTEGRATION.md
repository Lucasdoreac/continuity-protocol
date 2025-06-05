# Integração CONTINUITY com Claude Desktop

Este documento descreve como integrar o sistema CONTINUITY com o Claude Desktop através do arquivo `claude_desktop_config.json`.

## Visão Geral

O adaptador Claude MCP (`claude-mcp-adapter.sh`) permite que o sistema CONTINUITY seja utilizado como um servidor MCP (Model Context Protocol) diretamente no Claude Desktop. Isso proporciona:

1. **Continuidade de contexto** entre sessões do Claude
2. **Gerenciamento de estado** de projetos
3. **Recuperação de emergência** e backups automáticos
4. **Monitoramento de segurança** integrado

## Requisitos

- Node.js instalado
- jq instalado (`brew install jq` no macOS)
- Claude Desktop instalado
- Sistema CONTINUITY configurado

## Instalação

Para instalar o adaptador Claude MCP:

```bash
/Users/lucascardoso/apps/MCP/CONTINUITY/claude-mcp-adapter.sh install
```

Este comando:
1. Inicia o servidor MCP na porta 3457
2. Modifica o arquivo `~/.config/claude/claude_desktop_config.json` para incluir o servidor MCP
3. Configura o servidor com o nome "CONTINUITY" no Claude Desktop

## Verificação

Para verificar se a instalação foi bem-sucedida:

```bash
/Users/lucascardoso/apps/MCP/CONTINUITY/claude-mcp-adapter.sh status
```

Você também pode testar a integração com:

```bash
/Users/lucascardoso/apps/MCP/CONTINUITY/claude-mcp-adapter.sh test
```

## Uso no Claude Desktop

Após a instalação, o servidor MCP "CONTINUITY" estará disponível no Claude Desktop. Para utilizá-lo:

1. Abra o Claude Desktop
2. Verifique se o servidor MCP "CONTINUITY" está habilitado nas configurações
3. Inicie uma nova conversa
4. O Claude agora terá acesso às ferramentas MCP do sistema CONTINUITY:
   - `CONTINUITY___project-state`: Gerencia o estado do projeto
   - `CONTINUITY___continuity-prompt`: Gera prompts de continuidade
   - `CONTINUITY___initialize-project`: Inicializa novos projetos

## Comandos Disponíveis

- `install`: Instala e configura o adaptador no Claude Desktop
- `uninstall`: Remove a integração do Claude Desktop
- `start`: Inicia apenas o servidor MCP
- `stop`: Para o servidor MCP
- `restart`: Reinicia o servidor MCP
- `status`: Exibe o status atual do servidor e integração
- `test`: Testa a integração MCP-Claude

## Estrutura do arquivo claude_desktop_config.json

Após a instalação, o arquivo `claude_desktop_config.json` terá uma entrada semelhante a:

```json
{
  "theme": "system",
  "mcpServers": [
    {
      "name": "CONTINUITY",
      "url": "http://localhost:3457",
      "description": "MCP Continuity Tool para integração com Claude Desktop",
      "enabled": true
    }
  ]
}
```

## Desinstalação

Para remover a integração:

```bash
/Users/lucascardoso/apps/MCP/CONTINUITY/claude-mcp-adapter.sh uninstall
```

## Solução de Problemas

Se encontrar problemas com a integração:

1. Verifique o status do servidor:
   ```bash
   /Users/lucascardoso/apps/MCP/CONTINUITY/claude-mcp-adapter.sh status
   ```

2. Consulte os logs:
   ```bash
   tail -f /Users/lucascardoso/apps/MCP/CONTINUITY/logs/claude-mcp-adapter.log
   ```

3. Reinicie o servidor:
   ```bash
   /Users/lucascardoso/apps/MCP/CONTINUITY/claude-mcp-adapter.sh restart
   ```

4. Verifique se o arquivo de configuração do Claude é válido:
   ```bash
   jq empty ~/.config/claude/claude_desktop_config.json
   ```

## Integração com Outros Sistemas

O adaptador Claude MCP pode ser usado em conjunto com o adaptador AWS MCP (`aws-mcp-server.sh`), permitindo uma integração completa entre Claude Desktop, Amazon Q CLI e o sistema CONTINUITY.
