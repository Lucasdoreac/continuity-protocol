# API Reference

O Protocolo de Continuidade de Projetos (PCP) fornece uma API RESTful para integração com diferentes ferramentas e ambientes de desenvolvimento.

## Servidor API

O servidor API é implementado usando FastAPI e fornece os seguintes endpoints:

### Endpoints Principais

#### `GET /`

Retorna informações básicas sobre o servidor.

**Resposta:**
```json
{
  "name": "Continuity Protocol Server",
  "version": "1.0.0",
  "status": "running",
  "timestamp": "2025-06-03T18:00:00.000Z"
}
```

#### `GET /health`

Verifica a saúde do servidor.

**Resposta:**
```json
{
  "status": "healthy",
  "timestamp": "2025-06-03T18:00:00.000Z"
}
```

#### `POST /consciousness`

Obtém a consciência para uma sessão.

**Requisição:**
```json
{
  "session_id": "my-session",
  "project_path": "/path/to/project"
}
```

**Resposta:**
```json
{
  "session": {
    "session_id": "my-session",
    "current_focus": "Implementando autenticação",
    "history": [...]
  },
  "projects": [...],
  "system": {
    "platform": "darwin",
    "timestamp": "2025-06-03T18:00:00.000Z",
    "hostname": "macbook-pro"
  },
  "extracted_at": "2025-06-03T18:00:00.000Z"
}
```

#### `POST /project/symbiosis`

Estabelece simbiose com um projeto.

**Requisição:**
```json
{
  "project_path": "/path/to/project",
  "project_name": "My Project"
}
```

**Resposta:**
```json
{
  "name": "My Project",
  "path": "/path/to/project",
  "symbiosis_established": "2025-06-03T18:00:00.000Z",
  "dna": {
    "structure": {
      "file_count": 120,
      "directory_count": 15
    },
    "git_info": {
      "branch": "main",
      "last_commit": "abc123 - Fix authentication bug (user, 2 hours ago)"
    }
  }
}
```

#### `POST /project/update`

Atualiza o estado de um projeto.

**Requisição:**
```json
{
  "project_path": "/path/to/project",
  "current_file": "src/auth/login.js",
  "current_focus": "Corrigindo bug de autenticação"
}
```

**Resposta:**
```json
{
  "name": "My Project",
  "path": "/path/to/project",
  "current_file": "src/auth/login.js",
  "current_focus": "Corrigindo bug de autenticação",
  "last_updated": "2025-06-03T18:00:00.000Z"
}
```

#### `GET /projects`

Lista todos os projetos ativos.

**Resposta:**
```json
[
  {
    "name": "Project 1",
    "path": "/path/to/project1",
    "symbiosis_established": "2025-06-03T17:00:00.000Z"
  },
  {
    "name": "Project 2",
    "path": "/path/to/project2",
    "symbiosis_established": "2025-06-03T18:00:00.000Z"
  }
]
```

#### `POST /session/create`

Cria uma nova sessão.

**Requisição:**
```json
{
  "session_id": "my-session",
  "description": "Sessão para desenvolvimento de autenticação"
}
```

**Resposta:**
```json
{
  "session_id": "my-session",
  "description": "Sessão para desenvolvimento de autenticação",
  "created": "2025-06-03T18:00:00.000Z",
  "history": []
}
```

#### `GET /session/{session_id}`

Obtém o contexto de uma sessão.

**Resposta:**
```json
{
  "session_id": "my-session",
  "description": "Sessão para desenvolvimento de autenticação",
  "created": "2025-06-03T18:00:00.000Z",
  "current_focus": "Implementando autenticação",
  "history": [...]
}
```

#### `POST /session/update`

Atualiza o contexto de uma sessão.

**Requisição:**
```json
{
  "session_id": "my-session",
  "context_update": {
    "current_focus": "Implementando autenticação com OAuth",
    "next_steps": ["Integrar com Google", "Adicionar testes"]
  }
}
```

**Resposta:**
```json
{
  "session_id": "my-session",
  "description": "Sessão para desenvolvimento de autenticação",
  "created": "2025-06-03T18:00:00.000Z",
  "current_focus": "Implementando autenticação com OAuth",
  "next_steps": ["Integrar com Google", "Adicionar testes"],
  "history": [...]
}
```

#### `POST /continuity/check`

Verifica se um texto é uma pergunta de continuidade.

**Requisição:**
```json
{
  "text": "onde paramos?",
  "session_id": "my-session",
  "languages": ["pt", "en"]
}
```

**Resposta:**
```json
{
  "is_continuity_question": true,
  "matching_pattern": "onde paramos",
  "session_id": "my-session"
}
```

#### `POST /continuity/response`

Obtém uma resposta para uma pergunta de continuidade.

**Requisição:**
```json
{
  "session_id": "my-session"
}
```

**Resposta:**
```json
{
  "response": "# Continuidade da Sessão: my-session\n\n## Foco Atual\nImplementando autenticação com OAuth\n\n## Projetos Ativos\n- **My Project**: /path/to/project\n  - Arquivo atual: `src/auth/login.js`\n  - Branch: `main`\n\n## Próximos Passos\n- Integrar com Google\n- Adicionar testes",
  "session_id": "my-session",
  "timestamp": "2025-06-03T18:00:00.000Z"
}
```

#### `POST /process`

Processa entrada do usuário, lidando com perguntas de continuidade e injetando consciência.

**Requisição:**
```json
{
  "input_text": "onde paramos?",
  "session_id": "my-session",
  "llm_type": "claude"
}
```

**Resposta (para pergunta de continuidade):**
```json
{
  "type": "continuity_response",
  "response": "# Continuidade da Sessão: my-session\n\n## Foco Atual\nImplementando autenticação com OAuth\n\n## Projetos Ativos\n- **My Project**: /path/to/project\n  - Arquivo atual: `src/auth/login.js`\n  - Branch: `main`\n\n## Próximos Passos\n- Integrar com Google\n- Adicionar testes",
  "session_id": "my-session",
  "timestamp": "2025-06-03T18:00:00.000Z"
}
```

**Resposta (para entrada normal):**
```json
{
  "type": "modified_input",
  "modified_input": "<context>\n<current_focus>Implementando autenticação com OAuth</current_focus>\n<projects>\n<project>\n  <name>My Project</name>\n  <path>/path/to/project</path>\n  <current_file>src/auth/login.js</current_file>\n  <git_branch>main</git_branch>\n</project>\n</projects>\n</context>\n\nComo implementar autenticação OAuth com Google?",
  "session_id": "my-session",
  "timestamp": "2025-06-03T18:00:00.000Z"
}
```

### WebSocket

#### `WebSocket /ws/consciousness/{session_id}`

Stream de atualizações de consciência em tempo real para uma sessão.

**Mensagens enviadas pelo servidor:**
```json
{
  "session": {
    "session_id": "my-session",
    "current_focus": "Implementando autenticação",
    "history": [...]
  },
  "projects": [...],
  "system": {
    "platform": "darwin",
    "timestamp": "2025-06-03T18:00:00.000Z",
    "hostname": "macbook-pro"
  },
  "extracted_at": "2025-06-03T18:00:00.000Z"
}
```

## Integração com Clientes

### Python

```python
import requests

# Configuração
BASE_URL = "http://localhost:8765"

# Criar sessão
response = requests.post(f"{BASE_URL}/session/create", json={
    "session_id": "my-session",
    "description": "Sessão para desenvolvimento de autenticação"
})
print(response.json())

# Estabelecer simbiose com projeto
response = requests.post(f"{BASE_URL}/project/symbiosis", json={
    "project_path": "/path/to/project",
    "project_name": "My Project"
})
print(response.json())

# Processar entrada do usuário
response = requests.post(f"{BASE_URL}/process", json={
    "input_text": "onde paramos?",
    "session_id": "my-session",
    "llm_type": "claude"
})
print(response.json())
```

### JavaScript

```javascript
// Configuração
const BASE_URL = "http://localhost:8765";

// Criar sessão
fetch(`${BASE_URL}/session/create`, {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    session_id: "my-session",
    description: "Sessão para desenvolvimento de autenticação"
  })
})
.then(response => response.json())
.then(data => console.log(data));

// Estabelecer simbiose com projeto
fetch(`${BASE_URL}/project/symbiosis`, {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    project_path: "/path/to/project",
    project_name: "My Project"
  })
})
.then(response => response.json())
.then(data => console.log(data));

// Processar entrada do usuário
fetch(`${BASE_URL}/process`, {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    input_text: "onde paramos?",
    session_id: "my-session",
    llm_type: "claude"
  })
})
.then(response => response.json())
.then(data => console.log(data));

// WebSocket para atualizações em tempo real
const ws = new WebSocket(`ws://localhost:8765/ws/consciousness/my-session`);
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log("Consciousness update:", data);
};
```

### Curl

```bash
# Criar sessão
curl -X POST http://localhost:8765/session/create \
  -H "Content-Type: application/json" \
  -d '{"session_id": "my-session", "description": "Sessão para desenvolvimento de autenticação"}'

# Estabelecer simbiose com projeto
curl -X POST http://localhost:8765/project/symbiosis \
  -H "Content-Type: application/json" \
  -d '{"project_path": "/path/to/project", "project_name": "My Project"}'

# Processar entrada do usuário
curl -X POST http://localhost:8765/process \
  -H "Content-Type: application/json" \
  -d '{"input_text": "onde paramos?", "session_id": "my-session", "llm_type": "claude"}'
```
