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

### Quick Start

```bash
# Clone the repository
git clone https://github.com/continuity-protocol/continuity-protocol
cd continuity-protocol

# Start the server
./start-server.sh
```

### From Source

```bash
# Clone the repository
git clone https://github.com/continuity-protocol/continuity-protocol
cd continuity-protocol

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install the package in development mode
pip install -e .
```

## Usage

### Starting the Server

```bash
# Start with default settings
./start-server.sh

# Start with custom configuration
./start-server.sh --name "My-Continuity-Server" --transport stdio --log-level DEBUG
```

### Server Options

- `--name`: Server name (default: "Continuity-Protocol")
- `--transport`: Transport mechanism (stdio, http) (default: stdio)
- `--no-default-tools`: Disable registration of default continuity tools
- `--no-timesheet`: Disable LLM Timesheet tools
- `--log-level`: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL) (default: INFO)

### Using the Client

A simple client example is provided in the `examples/basic` directory:

```bash
# Run the example client
python examples/basic/simple_client.py
```

### MCP Tools

The protocol provides the following MCP tools:

#### Session Management

- `session_create`: Create a new session
- `session_save`: Save session state
- `session_restore`: Restore session state
- `session_list`: List available sessions
- `session_delete`: Delete a session

#### Context Management

- `context_store`: Store context information
- `context_retrieve`: Retrieve context information
- `context_switch`: Switch between contexts
- `context_delete`: Delete context information
- `context_list`: List available contexts

#### System Tools

- `system_status`: Get system status
- `memory_optimize`: Optimize memory usage

#### LLM Timesheet

- `llm_punch_in`: Register the start of a task
- `llm_punch_out`: Register the end of a task
- `llm_sprint_report`: Generate a sprint report
- `llm_finish_sprint`: Finish the current sprint
- `llm_active_tasks`: List active tasks
- `llm_task_details`: Get task details

## Architecture

Continuity Protocol is built on a multi-layered architecture:

1. **Core Server**: MCP-compliant JSON-RPC server
2. **Tools**: Implementations of MCP tools for continuity
3. **Memory System**: Multi-layered memory management
4. **Transports**: Communication mechanisms (stdio, http)
5. **LLMOps**: LLM Timesheet and analytics

## Documentation

Comprehensive documentation is available in the `docs` directory:

- [API Documentation](docs/api/README.md)
- [Architecture Overview](docs/architecture/README.md)
- [Tutorials](docs/tutorials/README.md)
- [Examples](docs/examples/README.md)

## Development

### Prerequisites

- Python 3.8 or higher
- Virtual environment (recommended)

### Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/continuity-protocol/continuity-protocol
cd continuity-protocol

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -e ".[dev]"
```

### Running Tests

```bash
# Run all tests
pytest

# Run tests with coverage
pytest --cov=continuity_protocol
```

## Contributing

Contributions are welcome\! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for details.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Anthropic for the Model Context Protocol (MCP)
- All contributors and users of the Continuity Protocol
EOL < /dev/null