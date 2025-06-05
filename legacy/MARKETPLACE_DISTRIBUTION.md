# Distribuição do Continuity Protocol em Marketplaces

Este documento explica como o Continuity Protocol pode ser distribuído por meio de marketplaces como Smithery e instalado via ferramentas como `uvx`.

## Visão Geral

O Continuity Protocol foi preparado para ser distribuído por vários canais:

1. **npm** - Como pacote Node.js global
2. **Smithery** - Marketplace para ferramentas MCP
3. **uvx** - Gerenciador de ferramentas universal

## Estrutura de Distribuição

Os arquivos para distribuição estão organizados no diretório `/dist`:

```
/dist/
├── bin/                      # Executáveis
│   └── continuity-protocol.js # Ponto de entrada principal
├── python/                   # Implementação Python
│   └── continuity_server.py  # Servidor Python
├── scripts/                  # Scripts auxiliares
│   └── postinstall.js        # Script pós-instalação
├── package.json              # Metadados npm
├── smithery.json             # Metadados Smithery
├── uvx-meta.json             # Metadados uvx
├── README.md                 # Documentação
└── prepare-publish.sh        # Script de preparação para publicação
```

## Instalação por Usuários Finais

### Via npm

```bash
npm install -g continuity-protocol
```

### Via uvx

```bash
uvx continuity-protocol
```

### Via Smithery

```bash
npx @smithery/cli@latest run continuity-protocol
```

## Integração com Claude Desktop

Os usuários podem integrar o Continuity Protocol ao Claude Desktop de duas formas:

### 1. Instalação via URL

No Claude Desktop:
1. Vá em Configurações > Integrações
2. Clique em "Adicionar integração personalizada"
3. Insira a URL: `mcp://continuity-protocol`
4. Clique em "Salvar"

### 2. Configuração Manual

Também é possível configurar manualmente editando o arquivo de configuração do Claude Desktop:

```json
{
  "mcpServers": {
    "continuity-protocol": {
      "command": "continuity-protocol",
      "args": [],
      "description": "Protocolo de Continuidade de Projetos"
    }
  }
}
```

## Publicação

Para publicar o pacote:

```bash
cd /Users/lucascardoso/apps/MCP/CONTINUITY/dist
./prepare-publish.sh
```

Isso criará um diretório `build` com todos os arquivos necessários para publicação.

### Publicar no npm

```bash
cd build
npm publish
```

### Publicar no Smithery

```bash
cd build
npx @smithery/cli@latest publish
```

### Criar pacote uvx

```bash
cd build
npm pack
uvx add ./continuity-protocol-1.0.0.tgz
```

## Benefícios da Distribuição via Marketplace

1. **Instalação com um comando** - Os usuários podem instalar o Continuity Protocol com um único comando
2. **Atualizações automáticas** - Os usuários recebem atualizações quando disponíveis
3. **Descoberta** - Outros usuários podem descobrir o Continuity Protocol facilmente
4. **Integração transparente** - Funciona automaticamente com ferramentas MCP como Claude Desktop

## Próximos Passos

1. Finalizar a documentação de usuário
2. Preparar materiais promocionais para marketplaces
3. Implementar testes automatizados
4. Configurar pipeline de CI/CD para publicação automatizada