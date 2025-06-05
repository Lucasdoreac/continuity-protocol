# Continuity Protocol (MCP)

A comprehensive implementation of the Model Context Protocol (MCP) for maintaining continuity in large language model interactions.

## About

The Continuity Protocol is a framework designed to enable persistent context and session management for AI assistants. It allows for:

- Seamless resumption of conversations
- Context awareness across multiple sessions
- Tool management with JSON-RPC 2.0
- Data persistence and recovery
- Context detection and management

## Features

- **Server Component**: Implements the JSON-RPC 2.0 protocol for tool registration and execution
- **Transport Layer**: HTTP server for handling requests
- **Tool Management**: System for registering, describing and executing tools
- **Context Tools**: Store and retrieve contextual information
- **Session Tools**: Manage conversation sessions with versioning
- **System Tools**: Monitor system health and perform optimization

## Getting Started

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/continuity-protocol.git
cd continuity-protocol

# Install dependencies
pip install -e .
```

### Basic Usage

```python
from continuity_protocol.server import MCPServer
from continuity_protocol.transport.http import start_server

# Create a server
server = MCPServer("My-MCP-Server")

# Register a tool
def add(a, b):
    return {"result": a + b}

server.register_tool("add", add, {
    "description": "Add two numbers",
    "parameters": {
        "type": "object",
        "properties": {
            "a": {"type": "number"},
            "b": {"type": "number"}
        },
        "required": ["a", "b"]
    }
})

# Register default tools (context, session, system)
server.register_default_tools()

# Start the server (default port: 8000)
start_server(server)
```

### Client Example

```python
import requests
import json

# Create a request
request = {
    "jsonrpc": "2.0",
    "id": "test-1",
    "method": "execute",
    "params": {
        "tool": "add",
        "parameters": {
            "a": 5,
            "b": 7
        }
    }
}

# Send the request
response = requests.post(
    "http://localhost:8000/mcp",
    json=request,
    headers={"Content-Type": "application/json"}
)

# Parse response
result = response.json()
print(result)  # {"jsonrpc": "2.0", "id": "test-1", "result": {"result": 12}}
```

## Testing

Run tests using the provided test runner:

```bash
# Run all tests
./run_tests.sh --all

# Run specific test types
./run_tests.sh --unit
./run_tests.sh --integration

# Generate coverage report
./run_tests.sh --all --coverage
```

## License

MIT

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.