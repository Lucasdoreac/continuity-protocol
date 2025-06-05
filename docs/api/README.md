# Continuity Protocol API Documentation

This document provides an overview of the Continuity Protocol API, including the server, tools, and integration methods.

## Table of Contents

- [Server API](#server-api)
- [Session Management Tools](#session-management-tools)
- [Context Management Tools](#context-management-tools)
- [System Tools](#system-tools)
- [LLM Timesheet Tools](#llm-timesheet-tools)
- [Integration Methods](#integration-methods)

## Server API

The Continuity Protocol is based on a JSON-RPC 2.0 server that exposes tools for context preservation and management.

### `MCPServer`

The main server class that handles JSON-RPC requests and manages tools.

```python
from continuity_protocol.server import MCPServer

# Create server instance
server = MCPServer(name="My-Server")

# Register default tools
server.register_default_tools()

# Run server with stdio transport
server.run(transport="stdio")
```

#### Methods

- `__init__(name: str = "Continuity-Protocol")`: Initialize a new server
- `register_tool(name: str, func: Callable, description: Dict[str, Any] = None)`: Register a tool
- `register_default_tools()`: Register all default continuity tools
- `register_llm_timesheet_tools()`: Register LLM Timesheet tools
- `get_tool_descriptions()`: Get descriptions of all registered tools
- `handle_request(request: Dict[str, Any])`: Handle a JSON-RPC request
- `run(transport: str = "stdio")`: Run the server with the specified transport

#### JSON-RPC Protocol

The server implements the JSON-RPC 2.0 protocol. Requests should have the following format:

```json
{
  "jsonrpc": "2.0",
  "id": "request-id",
  "method": "execute",
  "params": {
    "tool": "tool_name",
    "parameters": {
      "param1": "value1",
      "param2": "value2"
    }
  }
}
```

Responses will have the following format:

```json
{
  "jsonrpc": "2.0",
  "id": "request-id",
  "result": {
    // Tool-specific result
  }
}
```

Or in case of an error:

```json
{
  "jsonrpc": "2.0",
  "id": "request-id",
  "error": {
    "code": -32601,
    "message": "Method not found: invalid_method"
  }
}
```

## Session Management Tools

Tools for creating, saving, and restoring session state.

### `session_create`

Create a new session.

**Parameters:**
- `name`: Name of the session
- `metadata` (optional): Additional metadata for the session

**Returns:**
```json
{
  "session_id": "uuid-string",
  "created_at": "ISO-timestamp"
}
```

### `session_save`

Save the current state of a session.

**Parameters:**
- `session_id`: Session identifier
- `content`: Content to save
- `compression_level` (optional): Compression level (0-3)

**Returns:**
```json
{
  "success": true,
  "version": 1,
  "saved_at": "ISO-timestamp"
}
```

### `session_restore`

Restore a previously saved session.

**Parameters:**
- `session_id`: Session identifier
- `version` (optional): Version to restore

**Returns:**
```json
{
  "success": true,
  "content": { /* Session content */ },
  "metadata": { /* Session metadata */ },
  "version": 1
}
```

### `session_list`

List all available sessions.

**Parameters:** None

**Returns:**
```json
{
  "success": true,
  "sessions": [
    {
      "session_id": "uuid-string",
      "name": "Session Name",
      "created_at": "ISO-timestamp",
      "updated_at": "ISO-timestamp",
      "versions": 3
    },
    // ...
  ],
  "count": 1
}
```

### `session_delete`

Delete a session.

**Parameters:**
- `session_id`: Session identifier

**Returns:**
```json
{
  "success": true,
  "session_id": "uuid-string"
}
```

## Context Management Tools

Tools for storing, retrieving, and manipulating context.

### `context_store`

Store context information.

**Parameters:**
- `key`: Context identifier
- `value`: Context value to store
- `ttl` (optional): Time to live in seconds
- `namespace` (optional): Context namespace

**Returns:**
```json
{
  "success": true,
  "expires_at": "ISO-timestamp" // Only if TTL is specified
}
```

### `context_retrieve`

Retrieve stored context information.

**Parameters:**
- `key`: Context identifier
- `namespace` (optional): Context namespace

**Returns:**
```json
{
  "success": true,
  "value": { /* Context value */ },
  "stored_at": "ISO-timestamp",
  "expires_at": "ISO-timestamp" // If TTL was specified
}
```

### `context_switch`

Switch between different contexts.

**Parameters:**
- `target_context`: Target context identifier
- `preserve_current` (optional): Whether to preserve current context

**Returns:**
```json
{
  "success": true,
  "previous_context": "previous-context-id",
  "context_loaded": true
}
```

### `context_delete`

Delete stored context.

**Parameters:**
- `key`: Context identifier
- `namespace` (optional): Context namespace

**Returns:**
```json
{
  "success": true,
  "key": "context-key",
  "namespace": "namespace"
}
```

### `context_list`

List available contexts.

**Parameters:**
- `namespace` (optional): Context namespace
- `include_expired` (optional): Whether to include expired contexts

**Returns:**
```json
{
  "success": true,
  "contexts": [
    {
      "key": "context-key",
      "stored_at": "ISO-timestamp",
      "expires_at": "ISO-timestamp" // If TTL was specified
    },
    // ...
  ],
  "count": 1
}
```

## System Tools

Tools for system management and status.

### `system_status`

Get system status.

**Parameters:**
- `include_sessions` (optional): Whether to include active sessions
- `include_metrics` (optional): Whether to include system metrics

**Returns:**
```json
{
  "status": "healthy",
  "version": "0.1.0",
  "uptime_seconds": 3600,
  "platform": "platform-info",
  "python_version": "3.8.10",
  "active_sessions": [ /* If include_sessions is true */ ],
  "metrics": { /* If include_metrics is true */ }
}
```

### `memory_optimize`

Optimize memory usage.

**Parameters:**
- `target_session` (optional): Target session to optimize
- `level`: Optimization level (light, medium, aggressive)

**Returns:**
```json
{
  "success": true,
  "bytes_saved": 1024,
  "memory_reduced_bytes": 2048,
  "memory_reduced_mb": 2.0,
  "optimization_level": "medium",
  "optimization_details": { /* Details about the optimization */ }
}
```

## LLM Timesheet Tools

Tools for tracking LLM contributions.

### `llm_punch_in`

Register the start of a task.

**Parameters:**
- `llm_name`: Name of the LLM
- `task_description`: Description of the task
- `context` (optional): Additional context

**Returns:**
```json
{
  "success": true,
  "task_id": "uuid-string",
  "llm_name": "claude",
  "task_description": "Task description",
  "start_time": "ISO-timestamp"
}
```

### `llm_punch_out`

Register the end of a task.

**Parameters:**
- `task_id`: Task identifier
- `summary`: Summary of work done
- `detect_files` (optional): Whether to detect modified files

**Returns:**
```json
{
  "success": true,
  "task_id": "uuid-string",
  "duration_seconds": 3600,
  "end_time": "ISO-timestamp",
  "files_modified": 5,
  "summary": "Task summary"
}
```

### `llm_sprint_report`

Generate a sprint report.

**Parameters:** None

**Returns:**
```json
{
  "success": true,
  "sprint_id": "sprint-1",
  "project_name": "Project Name",
  "status": "active",
  "statistics": {
    "total_tasks": 10,
    "completed_tasks": 8,
    "in_progress_tasks": 2,
    "completion_rate": 0.8,
    "total_files_modified": 20
  },
  "contributors": {
    "claude": {
      "tasks_completed": 5,
      "tasks_in_progress": 1,
      "total_time": 7200
    },
    // ...
  }
}
```

### `llm_finish_sprint`

Finish the current sprint and start a new one.

**Parameters:**
- `summary`: Sprint summary

**Returns:**
```json
{
  "success": true,
  "sprint_id": "sprint-1",
  "completion_rate": 0.8,
  "next_sprint": "sprint-2"
}
```

### `llm_active_tasks`

List active tasks in the current sprint.

**Parameters:** None

**Returns:**
```json
{
  "success": true,
  "sprint_id": "sprint-1",
  "active_tasks": [
    {
      "task_id": "uuid-string",
      "llm_name": "claude",
      "description": "Task description",
      "start_time": "ISO-timestamp"
    },
    // ...
  ],
  "count": 2
}
```

### `llm_task_details`

Get details of a specific task.

**Parameters:**
- `task_id`: Task identifier

**Returns:**
```json
{
  "success": true,
  "task_id": "uuid-string",
  "llm_name": "claude",
  "description": "Task description",
  "status": "completed",
  "start_time": "ISO-timestamp",
  "end_time": "ISO-timestamp",
  "summary": "Task summary",
  "files_modified": 5
}
```

## Integration Methods

The Continuity Protocol can be integrated with various systems.

### Stdio Integration

The simplest integration method is using stdio transport:

```python
from continuity_protocol.server import run_server

# Run server with stdio transport
run_server(name="My-Server", transport="stdio")
```

This allows the server to be used with systems that communicate via standard input/output, such as Claude Desktop.

### Client Integration

A Python client can be used to communicate with the server:

```python
import json
import subprocess

# Start server process
server_process = subprocess.Popen(
    ["./start-server.sh"],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    universal_newlines=True,
    bufsize=1
)

# Create a session
request = {
    "jsonrpc": "2.0",
    "id": "1",
    "method": "execute",
    "params": {
        "tool": "session_create",
        "parameters": {
            "name": "Example Session"
        }
    }
}

# Send request
server_process.stdin.write(json.dumps(request) + "\n")
server_process.stdin.flush()

# Read response
response = json.loads(server_process.stdout.readline())
print(response)
```