# Especificação do Protocolo MCP para Continuidade

Este documento estabelece a especificação técnica para implementação do Protocolo de Continuidade baseado em MCP (Model Context Protocol), seguindo os padrões atuais do ecossistema MCP e otimizado para continuidade de conversas e preservação de contexto.

## 1. Fundamentos MCP

### 1.1 Arquitetura Cliente-Servidor

O MCP segue uma arquitetura cliente-servidor baseada em JSON-RPC 2.0:

```
+------------+                +------------+
|            |    JSON-RPC    |            |
|   Cliente  | <------------> |  Servidor  |
|            |                |            |
+------------+                +------------+
```

- **Cliente**: Aplicação que interage com o modelo de IA (Claude, GPT, etc.)
- **Servidor**: Implementação do protocolo que expõe ferramentas e recursos

### 1.2 Componentes Principais

O MCP define três componentes fundamentais:

1. **Ferramentas (Tools)**: Funções controladas pelo modelo
2. **Recursos (Resources)**: Fontes de dados controladas pela aplicação
3. **Prompts**: Templates controlados pelo usuário

### 1.3 Formato das Mensagens

As mensagens seguem o padrão JSON-RPC 2.0:

```json
// Requisição
{
  "jsonrpc": "2.0",
  "id": "uuid-1234",
  "method": "execute",
  "params": {
    "tool": "tool_name",
    "parameters": {
      "param1": "value1",
      "param2": "value2"
    }
  }
}

// Resposta
{
  "jsonrpc": "2.0",
  "id": "uuid-1234",
  "result": {
    "content": "Resultado da execução"
  }
}
```

## 2. Especificação de Ferramentas para Continuidade

### 2.1 Gestão de Sessão

#### 2.1.1 `session_create`

Cria uma nova sessão de continuidade.

```json
{
  "name": "session_create",
  "description": "Create a new continuity session",
  "parameters": {
    "type": "object",
    "properties": {
      "name": {
        "type": "string",
        "description": "Name of the session"
      },
      "metadata": {
        "type": "object",
        "description": "Additional metadata for the session"
      }
    },
    "required": ["name"]
  },
  "returns": {
    "type": "object",
    "properties": {
      "session_id": {
        "type": "string",
        "description": "Unique identifier for the created session"
      },
      "created_at": {
        "type": "string",
        "format": "date-time",
        "description": "Creation timestamp"
      }
    }
  }
}
```

#### 2.1.2 `session_save`

Salva o estado atual da sessão.

```json
{
  "name": "session_save",
  "description": "Save the current state of a session",
  "parameters": {
    "type": "object",
    "properties": {
      "session_id": {
        "type": "string",
        "description": "Session identifier"
      },
      "content": {
        "type": "object",
        "description": "Session content to save"
      },
      "compression_level": {
        "type": "integer",
        "enum": [0, 1, 2, 3],
        "description": "Compression level (0=none, 3=maximum)"
      }
    },
    "required": ["session_id", "content"]
  },
  "returns": {
    "type": "object",
    "properties": {
      "success": {
        "type": "boolean"
      },
      "version": {
        "type": "integer",
        "description": "Version number of the saved state"
      },
      "saved_at": {
        "type": "string",
        "format": "date-time"
      }
    }
  }
}
```

#### 2.1.3 `session_restore`

Restaura uma sessão salva anteriormente.

```json
{
  "name": "session_restore",
  "description": "Restore a previously saved session",
  "parameters": {
    "type": "object",
    "properties": {
      "session_id": {
        "type": "string",
        "description": "Session identifier"
      },
      "version": {
        "type": "integer",
        "description": "Specific version to restore (optional)"
      }
    },
    "required": ["session_id"]
  },
  "returns": {
    "type": "object",
    "properties": {
      "success": {
        "type": "boolean"
      },
      "content": {
        "type": "object",
        "description": "Restored session content"
      },
      "metadata": {
        "type": "object",
        "description": "Session metadata"
      },
      "version": {
        "type": "integer",
        "description": "Version of the restored state"
      }
    }
  }
}
```

### 2.2 Gestão de Contexto

#### 2.2.1 `context_store`

Armazena informações de contexto.

```json
{
  "name": "context_store",
  "description": "Store context information",
  "parameters": {
    "type": "object",
    "properties": {
      "key": {
        "type": "string",
        "description": "Context identifier key"
      },
      "value": {
        "type": "object",
        "description": "Context value to store"
      },
      "ttl": {
        "type": "integer",
        "description": "Time to live in seconds (optional)"
      },
      "namespace": {
        "type": "string",
        "description": "Context namespace (optional)"
      }
    },
    "required": ["key", "value"]
  },
  "returns": {
    "type": "object",
    "properties": {
      "success": {
        "type": "boolean"
      },
      "expires_at": {
        "type": "string",
        "format": "date-time",
        "description": "Expiration time if TTL was specified"
      }
    }
  }
}
```

#### 2.2.2 `context_retrieve`

Recupera informações de contexto armazenadas.

```json
{
  "name": "context_retrieve",
  "description": "Retrieve stored context information",
  "parameters": {
    "type": "object",
    "properties": {
      "key": {
        "type": "string",
        "description": "Context identifier key"
      },
      "namespace": {
        "type": "string",
        "description": "Context namespace (optional)"
      }
    },
    "required": ["key"]
  },
  "returns": {
    "type": "object",
    "properties": {
      "success": {
        "type": "boolean"
      },
      "value": {
        "type": "object",
        "description": "Retrieved context value"
      },
      "stored_at": {
        "type": "string",
        "format": "date-time"
      },
      "expires_at": {
        "type": "string",
        "format": "date-time"
      }
    }
  }
}
```

#### 2.2.3 `context_switch`

Alterna entre diferentes contextos.

```json
{
  "name": "context_switch",
  "description": "Switch between different contexts",
  "parameters": {
    "type": "object",
    "properties": {
      "target_context": {
        "type": "string",
        "description": "Target context identifier"
      },
      "preserve_current": {
        "type": "boolean",
        "description": "Whether to preserve current context for later restoration"
      }
    },
    "required": ["target_context"]
  },
  "returns": {
    "type": "object",
    "properties": {
      "success": {
        "type": "boolean"
      },
      "previous_context": {
        "type": "string",
        "description": "Identifier of the previous context"
      },
      "context_loaded": {
        "type": "boolean",
        "description": "Whether the target context was successfully loaded"
      }
    }
  }
}
```

### 2.3 LLM Timesheet

#### 2.3.1 `llm_punch_in`

Registra o início de uma tarefa para um LLM.

```json
{
  "name": "llm_punch_in",
  "description": "Register the start of a task for an LLM",
  "parameters": {
    "type": "object",
    "properties": {
      "llm_name": {
        "type": "string",
        "description": "Name of the LLM (e.g., 'claude', 'gpt-4')"
      },
      "task_description": {
        "type": "string",
        "description": "Description of the task"
      },
      "context": {
        "type": "string",
        "description": "Additional context information (optional)"
      }
    },
    "required": ["llm_name", "task_description"]
  },
  "returns": {
    "type": "object",
    "properties": {
      "success": {
        "type": "boolean"
      },
      "task_id": {
        "type": "string",
        "description": "Unique identifier for the task"
      },
      "start_time": {
        "type": "string",
        "format": "date-time"
      }
    }
  }
}
```

#### 2.3.2 `llm_punch_out`

Registra o fim de uma tarefa para um LLM.

```json
{
  "name": "llm_punch_out",
  "description": "Register the end of a task for an LLM",
  "parameters": {
    "type": "object",
    "properties": {
      "task_id": {
        "type": "string",
        "description": "Task identifier"
      },
      "summary": {
        "type": "string",
        "description": "Summary of the work done"
      },
      "detect_files": {
        "type": "boolean",
        "description": "Whether to automatically detect modified files"
      }
    },
    "required": ["task_id", "summary"]
  },
  "returns": {
    "type": "object",
    "properties": {
      "success": {
        "type": "boolean"
      },
      "duration_seconds": {
        "type": "number",
        "description": "Duration of the task in seconds"
      },
      "files_modified": {
        "type": "integer",
        "description": "Number of files modified"
      }
    }
  }
}
```

### 2.4 Sistema e Utilitários

#### 2.4.1 `system_status`

Obtém o status do sistema de continuidade.

```json
{
  "name": "system_status",
  "description": "Get the status of the continuity system",
  "parameters": {
    "type": "object",
    "properties": {
      "include_sessions": {
        "type": "boolean",
        "description": "Whether to include active sessions in the response"
      },
      "include_metrics": {
        "type": "boolean",
        "description": "Whether to include system metrics in the response"
      }
    }
  },
  "returns": {
    "type": "object",
    "properties": {
      "status": {
        "type": "string",
        "enum": ["healthy", "degraded", "error"]
      },
      "version": {
        "type": "string",
        "description": "Version of the continuity system"
      },
      "uptime_seconds": {
        "type": "number",
        "description": "System uptime in seconds"
      },
      "active_sessions": {
        "type": "array",
        "items": {
          "type": "object",
          "properties": {
            "session_id": {
              "type": "string"
            },
            "name": {
              "type": "string"
            },
            "created_at": {
              "type": "string",
              "format": "date-time"
            }
          }
        },
        "description": "List of active sessions (if requested)"
      },
      "metrics": {
        "type": "object",
        "description": "System metrics (if requested)"
      }
    }
  }
}
```

#### 2.4.2 `memory_optimize`

Otimiza a memória do sistema.

```json
{
  "name": "memory_optimize",
  "description": "Optimize system memory usage",
  "parameters": {
    "type": "object",
    "properties": {
      "target_session": {
        "type": "string",
        "description": "Target session to optimize (optional)"
      },
      "level": {
        "type": "string",
        "enum": ["light", "medium", "aggressive"],
        "description": "Optimization level"
      }
    }
  },
  "returns": {
    "type": "object",
    "properties": {
      "success": {
        "type": "boolean"
      },
      "bytes_saved": {
        "type": "integer",
        "description": "Amount of memory saved in bytes"
      },
      "optimization_details": {
        "type": "object",
        "description": "Details about the optimization performed"
      }
    }
  }
}
```

## 3. Sistema de Memória Multi-Camadas

### 3.1 Especificação de Interface

```typescript
interface MemorySystem {
  // Memória de Curto Prazo
  shortTerm: {
    store(key: string, value: any, ttl?: number): Promise<boolean>;
    retrieve(key: string): Promise<any>;
    forget(key: string): Promise<boolean>;
  };
  
  // Memória de Trabalho
  workingMemory: {
    focus(item: string): Promise<boolean>;
    getCurrentFocus(): Promise<string[]>;
    addToWorkspace(item: any): Promise<string>;
    getWorkspace(): Promise<any[]>;
  };
  
  // Memória Episódica
  episodic: {
    recordEpisode(episode: Episode): Promise<string>;
    retrieveEpisode(id: string): Promise<Episode>;
    searchEpisodes(query: string): Promise<Episode[]>;
    summarizeEpisodes(ids: string[]): Promise<string>;
  };
  
  // Memória Semântica
  semantic: {
    storeKnowledge(key: string, knowledge: any): Promise<boolean>;
    retrieveKnowledge(key: string): Promise<any>;
    queryKnowledge(query: string): Promise<any[]>;
    updateKnowledge(key: string, knowledge: any): Promise<boolean>;
  };
  
  // Memória Procedural
  procedural: {
    learnProcedure(name: string, steps: Step[]): Promise<boolean>;
    executeProcedure(name: string, params: any): Promise<any>;
    listProcedures(): Promise<string[]>;
    updateProcedure(name: string, steps: Step[]): Promise<boolean>;
  };
}
```

### 3.2 Estruturas de Dados

#### 3.2.1 Episódio

```typescript
interface Episode {
  id: string;
  timestamp: string; // ISO date
  summary: string;
  content: any;
  participants: string[];
  tags: string[];
  importance: number; // 1-10
}
```

#### 3.2.2 Passo de Procedimento

```typescript
interface Step {
  id: string;
  description: string;
  action: string;
  parameters: any;
  next?: string | ConditionalNext[];
}

interface ConditionalNext {
  condition: string;
  next: string;
}
```

## 4. Transporte e Comunicação

### 4.1 Transporte Stdio

Comunicação baseada em entrada/saída padrão, seguindo o padrão MCP:

```
STDIN: {"jsonrpc":"2.0","id":"1","method":"execute","params":{"tool":"session_create","parameters":{"name":"My Session"}}}
STDOUT: {"jsonrpc":"2.0","id":"1","result":{"session_id":"abc-123","created_at":"2025-06-05T12:00:00Z"}}
```

### 4.2 Transporte HTTP

Endpoint REST para comunicação via HTTP:

```
POST /mcp/v1/execute
Content-Type: application/json

{
  "jsonrpc": "2.0",
  "id": "1",
  "method": "execute",
  "params": {
    "tool": "session_create",
    "parameters": {
      "name": "My Session"
    }
  }
}
```

### 4.3 Transporte WebSocket

Comunicação bidirecional via WebSocket:

```
// Conectar em ws://server/mcp/ws
// Enviar
{
  "jsonrpc": "2.0",
  "id": "1",
  "method": "execute",
  "params": {
    "tool": "session_create",
    "parameters": {
      "name": "My Session"
    }
  }
}

// Receber
{
  "jsonrpc": "2.0",
  "id": "1",
  "result": {
    "session_id": "abc-123",
    "created_at": "2025-06-05T12:00:00Z"
  }
}
```

## 5. Segurança e Privacidade

### 5.1 Autenticação

- Suporte para API Keys
- Suporte para OAuth 2.0
- Suporte para JWT

### 5.2 Criptografia

- Comunicação via TLS/SSL
- Criptografia em repouso para dados sensíveis
- Hashing para identificadores

### 5.3 Controle de Acesso

- Permissões baseadas em roles
- Isolamento de namespaces
- Auditoria de acesso

## 6. Performance e Escalabilidade

### 6.1 Métricas Alvo

- Latência P95 < 100ms para operações de contexto
- Throughput: 1000+ operações/segundo por instância
- Escala horizontal para múltiplas instâncias

### 6.2 Estratégias de Escalabilidade

- Arquitetura stateless para facilitar escalabilidade horizontal
- Caching em múltiplas camadas
- Persistência assíncrona para operações não-críticas

### 6.3 Monitoramento

- Métricas de saúde do sistema
- Alertas para degradação de performance
- Logging estruturado para diagnóstico

## 7. Integração com Ecossistema MCP

### 7.1 Compatibilidade com Clientes

- Claude Desktop
- Claude Web
- OpenAI API (via adaptador)
- Antropic API

### 7.2 Extensibilidade

- Sistema de plugins para ferramentas adicionais
- Hooks para personalização de comportamento
- API para extensões de terceiros

---

Esta especificação serve como guia para a implementação do Protocolo de Continuidade baseado em MCP e pode evoluir conforme o desenvolvimento do projeto avança e o ecossistema MCP continua a se desenvolver.