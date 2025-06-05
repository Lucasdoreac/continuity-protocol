# Getting Started with Continuity Protocol

This tutorial will guide you through the basic setup and usage of the Continuity Protocol.

## Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- Git (optional, for cloning the repository)

## Installation

### Option 1: Install from GitHub

```bash
# Clone the repository
git clone https://github.com/continuity-protocol/continuity-protocol.git
cd continuity-protocol

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install the package
pip install -e .
```

### Option 2: Install from PyPI (Not yet available)

```bash
# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install the package
pip install continuity-protocol
```

## Starting the Server

The Continuity Protocol includes scripts for starting the server in different modes:

### Using stdio Transport (for Claude Desktop)

```bash
./run-claude-server.sh
```

### Using HTTP Transport (for RESTful API)

```bash
./run-http-server.sh
```

### Using Python Directly

```python
from continuity_protocol.server import run_server

# Run with stdio transport
run_server(name="My-Server", transport="stdio")

# Run with HTTP transport
run_server(name="My-Server", transport="http", host="127.0.0.1", port=8000)
```

## Configuring Claude Desktop

To use the Continuity Protocol with Claude Desktop:

1. Run the configuration script:

```bash
./configure-claude-desktop.sh
```

2. Restart Claude Desktop

3. Verify that the MCP icon is active in Claude Desktop

4. Use the tools with the `/tools` command, for example:

```
/tools system_status{"include_sessions": true}
```

## Basic Usage Examples

### Using stdio Transport with Claude Desktop

In Claude Desktop, you can use the Continuity Protocol tools directly:

1. Creating a session:

```
/tools session_create{"name": "My First Session"}
```

2. Saving session state:

```
/tools session_save{"session_id": "your-session-id", "content": {"conversation": "Your conversation state"}}
```

3. Restoring a session:

```
/tools session_restore{"session_id": "your-session-id"}
```

### Using HTTP Transport with curl

1. Creating a session:

```bash
curl -X POST http://localhost:8000/execute -H "Content-Type: application/json" -d '{
  "jsonrpc": "2.0",
  "id": "1",
  "method": "execute",
  "params": {
    "tool": "session_create",
    "parameters": {
      "name": "My First Session"
    }
  }
}'
```

2. Listing available tools:

```bash
curl -X GET http://localhost:8000/tools
```

3. Checking server health:

```bash
curl -X GET http://localhost:8000/health
```

### Using the Python Client

The package includes a simple HTTP client for testing:

```bash
# List available tools
python examples/basic/http_client.py --url http://localhost:8000 list-tools

# Create a session
python examples/basic/http_client.py --url http://localhost:8000 session create --name "My Session"

# Get system status
python examples/basic/http_client.py --url http://localhost:8000 system status --include-metrics
```

## Using LLM Timesheet

The Continuity Protocol includes a system for tracking LLM contributions:

1. Register the start of a task:

```
/tools llm_punch_in{"llm_name": "claude", "task_description": "Implement feature X"}
```

2. Register the end of a task:

```
/tools llm_punch_out{"task_id": "your-task-id", "summary": "Implemented feature X with tests"}
```

3. Generate a sprint report:

```
/tools llm_sprint_report{}
```

## Next Steps

Now that you have the basics, you can:

1. Explore the [API Documentation](../api/README.md) for detailed information about available tools
2. Check the [Architecture Documentation](../architecture/README.md) to understand the system design
3. Try the [Examples](../../examples/) to see more complex usage patterns
4. Read the [Contributing Guide](../../CONTRIBUTING.md) if you want to contribute to the project

## Troubleshooting

### Server won't start

Make sure you have the required dependencies installed:

```bash
pip install -r requirements.txt
```

For HTTP transport, make sure FastAPI and uvicorn are installed:

```bash
pip install fastapi uvicorn
```

### Claude Desktop can't connect to the server

1. Make sure the server is running with stdio transport
2. Check that the configuration script ran successfully
3. Verify that the MCP icon is active in Claude Desktop
4. Check the server logs for any errors

### HTTP client can't connect to the server

1. Make sure the server is running with HTTP transport
2. Check that the server is listening on the correct host and port
3. Verify that there are no firewalls blocking the connection
4. Check the server logs for any errors

### Import errors

If you get import errors, make sure you have activated the virtual environment and installed the package:

```bash
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -e .
```