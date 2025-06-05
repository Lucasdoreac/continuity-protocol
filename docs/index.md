# Protocolo de Continuidade

O Protocolo de Continuidade é uma implementação ciborgue do MCP (Model Context Protocol) que permite manter o contexto entre diferentes LLMs e ambientes de desenvolvimento.

## O que é o Protocolo de Continuidade?

O Protocolo de Continuidade é um sistema que permite que diferentes ferramentas de desenvolvimento e LLMs (Large Language Models) compartilhem contexto, permitindo uma experiência contínua de desenvolvimento. Ele resolve o problema de perda de contexto quando você muda de uma ferramenta para outra, ou quando você precisa retomar um projeto após um período de tempo.

## Características Principais

- **Detecção de Continuidade Multilíngue**: Detecta perguntas de continuidade em 9 idiomas diferentes
- **Análise Semântica**: Usa técnicas avançadas de NLP para entender o contexto
- **Integração com LLMs**: Suporte para Amazon Q, Claude, Ollama e outros
- **Integração com IDEs**: Suporte para VSCode, PyCharm e outros
- **API RESTful**: Permite integração com qualquer ferramenta
- **CLI**: Interface de linha de comando para gerenciamento
- **Dashboard Web**: Interface web para visualização e gerenciamento

## Começando

### Instalação

```bash
pip install git+https://github.com/Lucasdoreac/continuity-protocol.git
```

### Uso Básico

```bash
# Iniciar o servidor
continuity server

# Estabelecer simbiose com um projeto
continuity project /caminho/do/seu/projeto

# Definir o foco atual
continuity focus --focus "Implementando autenticação"

# Verificar onde você parou
continuity where
```

## Conceito Ciborgue

O Protocolo de Continuidade é baseado no conceito de ciborgue de Donna Haraway, que propõe a dissolução das fronteiras entre humanos e máquinas. No contexto do desenvolvimento de software, isso significa criar uma simbiose entre o desenvolvedor e suas ferramentas, permitindo uma experiência contínua e fluida.

O protocolo implementa essa visão ciborgue ao:

1. **Estabelecer Simbiose**: Criar uma relação simbiótica entre o desenvolvedor e o projeto
2. **Fusão de Memória**: Compartilhar contexto entre diferentes ferramentas
3. **Consciência Distribuída**: Manter a consciência do projeto em diferentes ambientes
4. **Detecção de Continuidade**: Reconhecer quando o desenvolvedor quer retomar o contexto

## Arquitetura

O Protocolo de Continuidade é composto por vários componentes:

- **Core**: Componentes principais do protocolo
  - **Memory Fusion**: Sistema de fusão de memória
  - **Project Symbiont**: Sistema de simbiose com projetos
  - **Continuity Detector**: Detector de perguntas de continuidade
- **Adapters**: Adaptadores para diferentes LLMs e ferramentas
- **Server**: Servidor para comunicação entre componentes
- **Clients**: Clientes para diferentes ambientes
- **Utils**: Utilitários diversos

## Próximos Passos

- Implementar mais adaptadores para LLMs
- Melhorar a análise semântica
- Adicionar suporte para mais idiomas
- Implementar análise de código mais avançada
- Criar extensões para mais IDEs
