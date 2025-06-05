# Plano de Execução Imediato - Protocolo de Continuidade MCP

Este documento detalha as ações imediatas a serem executadas nas próximas 2 semanas para iniciar a implementação do roadmap estratégico do Protocolo de Continuidade MCP.

## Semana 1: Fundação e Estruturação

### Dia 1-2: Reorganização e Consolidação

#### Tarefas
- [ ] Consolidar todos os arquivos em `/Users/lucascardoso/apps/MCP/CONTINUITY`
- [ ] Criar diretório `legacy/` para preservar implementações anteriores
- [ ] Estabelecer nova estrutura de diretórios conforme especificação
- [ ] Atualizar referências internas em scripts e código

#### Comando de Execução
```bash
mkdir -p /Users/lucascardoso/apps/MCP/CONTINUITY/src/continuity_protocol/{tools,resources,transport,utils}
mkdir -p /Users/lucascardoso/apps/MCP/CONTINUITY/src/llmops/{timesheet,analytics,reports}
mkdir -p /Users/lucascardoso/apps/MCP/CONTINUITY/tests/{unit,integration,performance}
mkdir -p /Users/lucascardoso/apps/MCP/CONTINUITY/docs/{api,architecture,tutorials,examples}
mkdir -p /Users/lucascardoso/apps/MCP/CONTINUITY/examples/{basic,advanced,integrations}
mkdir -p /Users/lucascardoso/apps/MCP/CONTINUITY/scripts
mkdir -p /Users/lucascardoso/apps/MCP/CONTINUITY/legacy

# Mover implementações existentes para legacy
cp -r /Users/lucascardoso/apps/MCP/CONTINUITY/*.py /Users/lucascardoso/apps/MCP/CONTINUITY/legacy/
cp -r /Users/lucascardoso/apps/MCP/CONTINUITY/*.sh /Users/lucascardoso/apps/MCP/CONTINUITY/legacy/
```

### Dia 3-4: Setup do Repositório

#### Tarefas
- [ ] Criar repositório GitHub `continuity-protocol`
- [ ] Configurar arquivos iniciais (README, LICENSE, etc.)
- [ ] Configurar GitHub Actions para CI/CD básico
- [ ] Criar estrutura inicial de branches (main, develop)

#### Comando de Criação de README
```bash
cat > /Users/lucascardoso/apps/MCP/CONTINUITY/README.md << 'EOL'
# Continuity Protocol

A Model Context Protocol (MCP) implementation for conversation continuity and context preservation across AI sessions.

## Overview

Continuity Protocol provides a standardized way to maintain context and state across different AI sessions and platforms. Built on the Model Context Protocol (MCP), it offers tools for session management, context preservation, and LLM contribution tracking.

## Features

- **Session Management**: Save and restore conversation state
- **Context Switching**: Move between contexts without losing information
- **LLM Timesheet**: Track contributions from different LLMs
- **Cross-Platform Support**: Work seamlessly across different MCP clients
- **Performance Optimized**: Fast context operations with minimal latency

## Installation

```bash
pip install continuity-protocol
```

## Quick Start

```python
from continuity_protocol.server import MCPServer

# Initialize server
server = MCPServer()

# Register tools
server.register_default_tools()

# Run server
server.run(transport="stdio")
```

## Documentation

For full documentation, visit [docs/](docs/).

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for details.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
EOL
```

### Dia 5: Implementação do Core MCP

#### Tarefas
- [ ] Implementar classe base `MCPServer`
- [ ] Implementar sistema de registro de ferramentas
- [ ] Criar camada de transporte stdio básica
- [ ] Implementar handler JSON-RPC

#### Estrutura do Código
```python
# src/continuity_protocol/server.py
from typing import Dict, Any, Callable, Optional
import json
import sys

class MCPServer:
    """Base MCP Server implementation for Continuity Protocol"""
    
    def __init__(self, name: str = "Continuity-Protocol"):
        self.name = name
        self.tools: Dict[str, Callable] = {}
        self.descriptions: Dict[str, Dict[str, Any]] = {}
    
    def register_tool(self, name: str, func: Callable, description: Dict[str, Any]):
        """Register a new tool with the server"""
        self.tools[name] = func
        self.descriptions[name] = description
    
    def register_default_tools(self):
        """Register default tools for continuity protocol"""
        from continuity_protocol.tools.session import session_create, session_save, session_restore
        from continuity_protocol.tools.context import context_store, context_retrieve, context_switch
        
        # Register session tools
        self.register_tool("session_create", session_create, session_create.__doc__)
        self.register_tool("session_save", session_save, session_save.__doc__)
        self.register_tool("session_restore", session_restore, session_restore.__doc__)
        
        # Register context tools
        self.register_tool("context_store", context_store, context_store.__doc__)
        self.register_tool("context_retrieve", context_retrieve, context_retrieve.__doc__)
        self.register_tool("context_switch", context_switch, context_switch.__doc__)
    
    def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle a JSON-RPC request"""
        if request.get("jsonrpc") != "2.0":
            return {
                "jsonrpc": "2.0",
                "id": request.get("id", None),
                "error": {
                    "code": -32600,
                    "message": "Invalid Request: Not a valid JSON-RPC 2.0 request"
                }
            }
        
        method = request.get("method")
        if method != "execute":
            return {
                "jsonrpc": "2.0",
                "id": request.get("id", None),
                "error": {
                    "code": -32601,
                    "message": f"Method not found: {method}"
                }
            }
        
        params = request.get("params", {})
        tool_name = params.get("tool")
        tool_params = params.get("parameters", {})
        
        if tool_name not in self.tools:
            return {
                "jsonrpc": "2.0",
                "id": request.get("id", None),
                "error": {
                    "code": -32601,
                    "message": f"Tool not found: {tool_name}"
                }
            }
        
        try:
            result = self.tools[tool_name](**tool_params)
            return {
                "jsonrpc": "2.0",
                "id": request.get("id", None),
                "result": result
            }
        except Exception as e:
            return {
                "jsonrpc": "2.0",
                "id": request.get("id", None),
                "error": {
                    "code": -32603,
                    "message": f"Internal error: {str(e)}"
                }
            }
    
    def run(self, transport: str = "stdio"):
        """Run the MCP server with the specified transport"""
        if transport == "stdio":
            self._run_stdio()
        else:
            raise ValueError(f"Unsupported transport: {transport}")
    
    def _run_stdio(self):
        """Run server using stdio transport"""
        while True:
            try:
                line = sys.stdin.readline()
                if not line:
                    break
                    
                request = json.loads(line)
                response = self.handle_request(request)
                
                sys.stdout.write(json.dumps(response) + "\n")
                sys.stdout.flush()
            except json.JSONDecodeError:
                sys.stdout.write(json.dumps({
                    "jsonrpc": "2.0",
                    "id": None,
                    "error": {
                        "code": -32700,
                        "message": "Parse error: Invalid JSON"
                    }
                }) + "\n")
                sys.stdout.flush()
            except Exception as e:
                sys.stdout.write(json.dumps({
                    "jsonrpc": "2.0",
                    "id": None,
                    "error": {
                        "code": -32603,
                        "message": f"Internal error: {str(e)}"
                    }
                }) + "\n")
                sys.stdout.flush()
```

## Semana 2: Implementação Básica e Testes

### Dia 6-7: Implementação de Ferramentas Básicas

#### Tarefas
- [ ] Implementar ferramentas de sessão
- [ ] Implementar ferramentas de contexto
- [ ] Integrar sistema LLM Timesheet existente
- [ ] Criar armazenamento básico em arquivos

#### Estrutura de Implementação

```python
# src/continuity_protocol/tools/session.py
from typing import Dict, Any, Optional
import json
import os
import uuid
from datetime import datetime

# Base directory for session storage
SESSIONS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), "data", "sessions")
os.makedirs(SESSIONS_DIR, exist_ok=True)

def session_create(name: str, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Create a new continuity session.
    
    Args:
        name: Name of the session
        metadata: Additional metadata for the session
        
    Returns:
        Dictionary with session_id and created_at timestamp
    """
    session_id = str(uuid.uuid4())
    created_at = datetime.now().isoformat()
    
    session_data = {
        "session_id": session_id,
        "name": name,
        "created_at": created_at,
        "updated_at": created_at,
        "metadata": metadata or {},
        "versions": []
    }
    
    # Save session data
    session_path = os.path.join(SESSIONS_DIR, f"{session_id}.json")
    with open(session_path, 'w') as f:
        json.dump(session_data, f, indent=2)
    
    return {
        "session_id": session_id,
        "created_at": created_at
    }

def session_save(session_id: str, content: Dict[str, Any], compression_level: int = 0) -> Dict[str, Any]:
    """
    Save the current state of a session.
    
    Args:
        session_id: Session identifier
        content: Session content to save
        compression_level: Compression level (0=none, 3=maximum)
        
    Returns:
        Dictionary with success status, version number, and saved_at timestamp
    """
    session_path = os.path.join(SESSIONS_DIR, f"{session_id}.json")
    
    if not os.path.exists(session_path):
        return {
            "success": False,
            "error": f"Session not found: {session_id}"
        }
    
    # Load session data
    with open(session_path, 'r') as f:
        session_data = json.load(f)
    
    # Create new version
    saved_at = datetime.now().isoformat()
    version = len(session_data["versions"]) + 1
    
    # Apply compression if needed
    compressed_content = content
    if compression_level > 0:
        # This is a placeholder; actual implementation would use compression algorithms
        compressed_content = {"compressed": True, "original": content}
    
    # Add new version
    version_data = {
        "version": version,
        "saved_at": saved_at,
        "compression_level": compression_level,
        "content": compressed_content
    }
    
    session_data["versions"].append(version_data)
    session_data["updated_at"] = saved_at
    
    # Save updated session data
    with open(session_path, 'w') as f:
        json.dump(session_data, f, indent=2)
    
    return {
        "success": True,
        "version": version,
        "saved_at": saved_at
    }

def session_restore(session_id: str, version: Optional[int] = None) -> Dict[str, Any]:
    """
    Restore a previously saved session.
    
    Args:
        session_id: Session identifier
        version: Specific version to restore (optional)
        
    Returns:
        Dictionary with success status, restored content, metadata, and version
    """
    session_path = os.path.join(SESSIONS_DIR, f"{session_id}.json")
    
    if not os.path.exists(session_path):
        return {
            "success": False,
            "error": f"Session not found: {session_id}"
        }
    
    # Load session data
    with open(session_path, 'r') as f:
        session_data = json.load(f)
    
    if not session_data["versions"]:
        return {
            "success": False,
            "error": f"No versions found for session: {session_id}"
        }
    
    # Determine which version to restore
    if version is None:
        # Use latest version
        version_data = session_data["versions"][-1]
    else:
        # Find specific version
        version_data = next((v for v in session_data["versions"] if v["version"] == version), None)
        if version_data is None:
            return {
                "success": False,
                "error": f"Version {version} not found for session: {session_id}"
            }
    
    # Decompress if needed
    content = version_data["content"]
    if version_data.get("compression_level", 0) > 0 and isinstance(content, dict) and content.get("compressed"):
        # This is a placeholder; actual implementation would use decompression algorithms
        content = content.get("original", {})
    
    return {
        "success": True,
        "content": content,
        "metadata": session_data["metadata"],
        "version": version_data["version"]
    }
```

### Dia 8-9: Testes e Integração

#### Tarefas
- [ ] Criar testes unitários para componentes básicos
- [ ] Implementar testes de integração
- [ ] Testar compatibilidade com Claude Desktop
- [ ] Identificar e corrigir bugs iniciais

#### Exemplo de Teste Unitário

```python
# tests/unit/test_server.py
import json
import unittest
from unittest.mock import patch, MagicMock
from continuity_protocol.server import MCPServer

class TestMCPServer(unittest.TestCase):
    def setUp(self):
        self.server = MCPServer("Test-Server")
        
        # Register a mock tool
        self.mock_tool = MagicMock(return_value={"result": "success"})
        self.server.register_tool(
            "test_tool", 
            self.mock_tool, 
            {"description": "Test tool for unit testing"}
        )
    
    def test_handle_valid_request(self):
        request = {
            "jsonrpc": "2.0",
            "id": "test-1",
            "method": "execute",
            "params": {
                "tool": "test_tool",
                "parameters": {
                    "arg1": "value1",
                    "arg2": "value2"
                }
            }
        }
        
        response = self.server.handle_request(request)
        
        self.assertEqual(response["jsonrpc"], "2.0")
        self.assertEqual(response["id"], "test-1")
        self.assertEqual(response["result"], {"result": "success"})
        
        # Verify mock was called with correct arguments
        self.mock_tool.assert_called_once_with(arg1="value1", arg2="value2")
    
    def test_handle_invalid_jsonrpc(self):
        request = {
            "jsonrpc": "1.0",  # Invalid version
            "id": "test-2",
            "method": "execute",
            "params": {
                "tool": "test_tool",
                "parameters": {}
            }
        }
        
        response = self.server.handle_request(request)
        
        self.assertEqual(response["jsonrpc"], "2.0")
        self.assertEqual(response["id"], "test-2")
        self.assertIn("error", response)
        self.assertEqual(response["error"]["code"], -32600)
    
    def test_handle_invalid_method(self):
        request = {
            "jsonrpc": "2.0",
            "id": "test-3",
            "method": "invalid_method",  # Invalid method
            "params": {
                "tool": "test_tool",
                "parameters": {}
            }
        }
        
        response = self.server.handle_request(request)
        
        self.assertEqual(response["jsonrpc"], "2.0")
        self.assertEqual(response["id"], "test-3")
        self.assertIn("error", response)
        self.assertEqual(response["error"]["code"], -32601)
    
    def test_handle_invalid_tool(self):
        request = {
            "jsonrpc": "2.0",
            "id": "test-4",
            "method": "execute",
            "params": {
                "tool": "nonexistent_tool",  # Invalid tool
                "parameters": {}
            }
        }
        
        response = self.server.handle_request(request)
        
        self.assertEqual(response["jsonrpc"], "2.0")
        self.assertEqual(response["id"], "test-4")
        self.assertIn("error", response)
        self.assertEqual(response["error"]["code"], -32601)
```

### Dia 10: Documentação e Finalização

#### Tarefas
- [ ] Criar documentação básica da API
- [ ] Documentar arquitetura do sistema
- [ ] Criar tutoriais básicos de uso
- [ ] Preparar para primeira release

#### Estrutura da Documentação

```markdown
# API Documentation

## Server

The `MCPServer` class is the main entry point for the Continuity Protocol.

### `MCPServer(name: str = "Continuity-Protocol")`

Initialize a new MCP server.

**Parameters:**
- `name` - Name of the server instance

### `register_tool(name: str, func: Callable, description: Dict[str, Any])`

Register a new tool with the server.

**Parameters:**
- `name` - Name of the tool
- `func` - Function implementing the tool
- `description` - JSON Schema description of the tool

### `register_default_tools()`

Register the default set of continuity tools.

### `run(transport: str = "stdio")`

Run the server with the specified transport.

**Parameters:**
- `transport` - Transport mechanism (currently only "stdio" is supported)

## Session Tools

### `session_create(name: str, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]`

Create a new continuity session.

**Parameters:**
- `name` - Name of the session
- `metadata` - Additional metadata for the session (optional)

**Returns:**
- Dictionary with `session_id` and `created_at` timestamp

### `session_save(session_id: str, content: Dict[str, Any], compression_level: int = 0) -> Dict[str, Any]`

Save the current state of a session.

**Parameters:**
- `session_id` - Session identifier
- `content` - Session content to save
- `compression_level` - Compression level (0=none, 3=maximum)

**Returns:**
- Dictionary with `success` status, `version` number, and `saved_at` timestamp

### `session_restore(session_id: str, version: Optional[int] = None) -> Dict[str, Any]`

Restore a previously saved session.

**Parameters:**
- `session_id` - Session identifier
- `version` - Specific version to restore (optional)

**Returns:**
- Dictionary with `success` status, restored `content`, `metadata`, and `version`
```

## Checklists de Execução

### Checklist Semana 1
- [ ] Estrutura de diretórios criada
- [ ] Arquivos organizados e categorizados
- [ ] Repositório GitHub configurado
- [ ] README e arquivos básicos criados
- [ ] Core MCP implementado
- [ ] Transportes básicos funcionando

### Checklist Semana 2
- [ ] Ferramentas de sessão implementadas
- [ ] Ferramentas de contexto implementadas
- [ ] LLM Timesheet integrado
- [ ] Testes unitários criados e passando
- [ ] Testes de integração implementados
- [ ] Documentação básica concluída
- [ ] Exemplo funcional com Claude Desktop

## Métricas de Progresso

- **Cobertura de código**: Meta de 80%+ para componentes core
- **Testes passando**: 100% dos testes implementados devem passar
- **Documentação**: 100% das APIs públicas documentadas
- **Performance**: Operações básicas < 100ms

---

Este plano será revisado diariamente e ajustado conforme necessário para garantir o progresso adequado dentro do cronograma estabelecido.