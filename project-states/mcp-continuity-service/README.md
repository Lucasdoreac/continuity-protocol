# 🔄 MCP Continuity Service

**Professional continuity service for LLMs with MCP integration**

Transform your AI development workflow with intelligent context preservation, automatic recovery, and seamless session continuity.

## 🎯 Features

- **Automatic Context Detection**: Smart detection of "onde paramos?" questions
- **Intelligent Recovery**: Auto-recovery of interrupted sessions and critical missions
- **MCP Integration**: Full integration with Model Context Protocol servers
- **Streamlit Dashboard**: Professional web interface for project management
- **Custom Agents**: Support for specialized AI agents with persistent memory
- **Emergency System**: Bulletproof backup and recovery mechanisms
- **Multi-Model Support**: Works with OpenAI, custom models, and fine-tuned LLMs

## 🚀 Quick Start

### Installation via pip
```bash
pip install mcp-continuity-service
mcp-continuity init
mcp-continuity start & mcp-continuity ui
```

### Installation via Docker
```bash
git clone https://github.com/mcp-continuity/mcp-continuity-service
cd mcp-continuity-service
docker-compose up -d
```

## 📊 Architecture

```
┌─ Frontend (Streamlit) ─────────────────┐
│  • Dashboard de projetos               │
│  • Chat interface integrado           │
│  • Visualização de contexto           │
└────────────────────────────────────────┘
            ↕ REST API
┌─ Core Service (FastAPI) ──────────────┐
│  • Gerenciamento de sessões           │
│  • Sistema de continuidade            │
│  • Integração com LLMs                │
└────────────────────────────────────────┘
            ↕ MCP Protocol
┌─ MCP Servers ─────────────────────────┐
│  • Desktop Commander                  │
│  • Memory Server                      │
│  • Custom Agents                      │
└────────────────────────────────────────┘
```

## 🛠️ Usage

### Command Line Interface
```bash
# Initialize service
mcp-continuity init

# Start API server
mcp-continuity start --host 0.0.0.0 --port 8000

# Launch UI
mcp-continuity ui --port 8501

# Process input directly
mcp-continuity process "onde paramos?"
```

### Programmatic Usage
```python
from mcp_continuity import ContinuityManager, AgentService

# Initialize services
manager = ContinuityManager()
result = await manager.process_user_input("onde paramos?", "session-id")

# Create specialized agent
agents = AgentService()
session = await agents.create_agent_session("developer", "dev-session")
```

## 🤖 Custom Agents

Create specialized AI agents with built-in continuity:

```python
from mcp_continuity.services import CustomModelService

# Load your trained model
model_service = CustomModelService()
await model_service.load_custom_model("my-model", "/path/to/model")

# Chat with automatic continuity
async for response in model_service.chat_with_continuity(
    model_name="my-model",
    messages=[{"role": "user", "content": "onde paramos?"}],
    session_id="session-123",
    continuity_enabled=True
):
    print(response, end="")
```

## 📁 Project Structure

```
mcp-continuity-service/
├── src/
│   ├── core/           # Core continuity logic
│   ├── api/            # FastAPI endpoints
│   ├── models/         # Data models
│   ├── services/       # Business services
│   └── utils/          # Utilities
├── frontend/           # Streamlit UI
├── mcp_servers/        # Custom MCP servers
├── config/             # Configuration files
├── tests/              # Test suite
└── docker/             # Docker configuration
```

## 🔧 Development

```bash
# Clone repository
git clone https://github.com/mcp-continuity/mcp-continuity-service
cd mcp-continuity-service

# Install in development mode
pip install -e .

# Run tests
pytest

# Format code
black src/ frontend/ tests/
```

## 📚 Documentation

- [Installation Guide](docs/installation.md)
- [API Reference](docs/api.md)
- [Agent Development](docs/agents.md)
- [MCP Integration](docs/mcp.md)
- [Deployment Guide](docs/deployment.md)

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## 📄 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file for details.

## 🆘 Support

- 📧 Email: support@mcp-continuity.dev
- 💬 Discord: [Join our community](https://discord.gg/mcp-continuity)
- 📖 Docs: [docs.mcp-continuity.dev](https://docs.mcp-continuity.dev)
- 🐛 Issues: [GitHub Issues](https://github.com/mcp-continuity/mcp-continuity-service/issues)
