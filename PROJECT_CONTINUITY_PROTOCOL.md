# Protocolo de Continuidade de Projetos (PCP)

## Visão Geral

O Protocolo de Continuidade de Projetos (PCP) é uma implementação inspirada no protocolo A2A (Agent-to-Agent) do Google, mas focada na persistência de contexto de projetos entre sessões e na comunicação entre diferentes agentes de IA.

## Objetivos

1. **Persistência de Contexto**: Manter o contexto de projetos entre diferentes sessões de trabalho
2. **Descoberta de Projetos**: Permitir que agentes descubram projetos existentes e seus contextos
3. **Comunicação Inter-Agentes**: Facilitar a comunicação entre diferentes agentes de IA
4. **Rápida Contextualização**: Permitir que agentes sejam rapidamente contextualizados sobre um projeto

## Componentes Principais

### 1. Project Cards

Similar aos Agent Cards do A2A, os Project Cards são metadados que descrevem um projeto:

```json
{
  "project_id": "unique-project-id",
  "name": "Nome do Projeto",
  "description": "Descrição detalhada do projeto",
  "domain": "Domínio do projeto (ex: desenvolvimento web, análise de dados)",
  "created_at": "2025-06-05T12:00:00Z",
  "updated_at": "2025-06-05T15:30:00Z",
  "status": "active | paused | completed",
  "endpoints": {
    "context": "/api/projects/unique-project-id/context",
    "artifacts": "/api/projects/unique-project-id/artifacts",
    "sessions": "/api/projects/unique-project-id/sessions"
  },
  "metadata": {
    "technology_stack": ["python", "react", "postgresql"],
    "team_members": ["user1", "user2"],
    "repository": "https://github.com/org/repo"
  }
}
```

### 2. Context Store

Um repositório centralizado para armazenar e recuperar o contexto completo de um projeto:

- **Estado atual**: Onde o projeto está atualmente
- **Histórico**: Evolução do projeto ao longo do tempo
- **Artefatos**: Documentos, código, imagens e outros artefatos gerados
- **Sessões**: Registro de sessões de trabalho anteriores

### 3. Protocolo de Comunicação

Definição de como agentes podem interagir com o contexto de um projeto:

#### Operações de Contexto

- `GET /projects`: Lista todos os projetos disponíveis
- `GET /projects/{id}`: Recupera o card de um projeto específico
- `GET /projects/{id}/context`: Recupera o contexto completo de um projeto
- `POST /projects/{id}/context`: Adiciona novo contexto a um projeto
- `PUT /projects/{id}/context`: Atualiza o contexto de um projeto

#### Operações de Artefatos

- `GET /projects/{id}/artifacts`: Lista todos os artefatos de um projeto
- `GET /projects/{id}/artifacts/{artifact_id}`: Recupera um artefato específico
- `POST /projects/{id}/artifacts`: Adiciona um novo artefato ao projeto

#### Operações de Sessão

- `POST /projects/{id}/sessions/start`: Inicia uma nova sessão de trabalho
- `PUT /projects/{id}/sessions/{session_id}/end`: Finaliza uma sessão de trabalho
- `GET /projects/{id}/sessions/{session_id}`: Recupera dados de uma sessão específica

### 4. Continuity Manager

Um componente que gerencia a continuidade de projetos:

- **Inicialização de Projetos**: Cria novos projetos e seus contextos iniciais
- **Recuperação de Contexto**: Recupera o contexto completo de um projeto
- **Atualização de Contexto**: Atualiza o contexto de um projeto após uma sessão
- **Sincronização**: Sincroniza o contexto entre diferentes agentes

## Implementação Técnica

### Servidor MCP Unificado

O servidor MCP unificado deve implementar os seguintes recursos:

1. **Registro de Projetos**: API para registrar novos projetos
2. **Armazenamento de Contexto**: Sistema de armazenamento persistente para contexto
3. **Descoberta de Projetos**: Mecanismo para listar e buscar projetos
4. **Autenticação e Autorização**: Controle de acesso aos projetos

### Adaptadores para LLMs

Adaptadores específicos para diferentes LLMs:

- **Claude Adapter**: Para integração com Claude Desktop
- **GPT Adapter**: Para integração com OpenAI GPT
- **Gemini Adapter**: Para integração com Google Gemini

### Ferramentas MCP

Ferramentas MCP para interagir com o protocolo:

- `project_list`: Lista todos os projetos disponíveis
- `project_get`: Recupera detalhes de um projeto específico
- `project_create`: Cria um novo projeto
- `project_update`: Atualiza um projeto existente
- `context_add`: Adiciona novo contexto a um projeto
- `context_get`: Recupera o contexto de um projeto
- `session_start`: Inicia uma nova sessão de trabalho
- `session_end`: Finaliza uma sessão de trabalho

## Fluxo de Trabalho

1. **Início de Sessão**:
   - O agente chama `session_start` com o ID do projeto
   - O sistema recupera o contexto completo do projeto
   - O sistema inicializa o agente com o contexto recuperado

2. **Durante a Sessão**:
   - O agente trabalha no projeto usando o contexto fornecido
   - O agente pode adicionar novos artefatos ao projeto
   - O agente pode atualizar o contexto conforme necessário

3. **Fim de Sessão**:
   - O agente chama `session_end`
   - O sistema salva o contexto atualizado
   - O sistema registra a sessão no histórico do projeto

4. **Colaboração Entre Agentes**:
   - Agentes podem descobrir projetos existentes
   - Agentes podem acessar o mesmo contexto de projeto
   - Agentes podem colaborar adicionando e atualizando artefatos

## Próximos Passos

1. **Implementação do Servidor**: Criar um servidor MCP completo que implemente o protocolo
2. **Desenvolvimento dos Adaptadores**: Criar adaptadores para diferentes LLMs
3. **Ferramentas CLI**: Desenvolver ferramentas de linha de comando para interagir com o protocolo
4. **Documentação**: Criar documentação detalhada do protocolo e sua implementação
5. **Exemplos de Uso**: Desenvolver exemplos práticos de uso do protocolo