# Quick Start Guide

## Installation

### Option 1: Quick Install (Recommended)
```bash
# Clone the repository
git clone https://github.com/mcp-continuity/mcp-continuity-service
cd mcp-continuity-service

# Run quick install script
chmod +x install.sh
./install.sh
```

### Option 2: Manual Install
```bash
# Install dependencies
pip install -r requirements.txt

# Install package
pip install -e .

# Initialize service
mcp-continuity init
```

### Option 3: Docker
```bash
# Start all services
docker-compose up -d

# Access UI at http://localhost:8501
# API at http://localhost:8000
```

## Basic Usage

### 1. Start the Service
```bash
# Terminal 1: Start API
mcp-continuity start

# Terminal 2: Start UI
mcp-continuity ui
```

### 2. Use the Web Interface
1. Open http://localhost:8501
2. Go to "Chat Interface"
3. Try saying: "onde paramos?"
4. The system will automatically detect and provide context!

### 3. Programmatic Usage
```python
from mcp_continuity import ContinuityManager

# Initialize
manager = ContinuityManager()

# Process continuity question
result = await manager.process_user_input(
    user_input="onde paramos?",
    session_id="my-session"
)

print(result)
```

### 4. CLI Usage
```bash
# Process input directly
mcp-continuity process "onde paramos?"

# Check status
mcp-continuity status

# View help
mcp-continuity --help
```

## Key Features

- **Automatic Context Detection**: Recognizes continuity questions automatically
- **Smart Recovery**: Auto-recovers interrupted sessions
- **Emergency Backup**: Creates safety backups before risky operations
- **Web Interface**: Professional Streamlit dashboard
- **API Integration**: RESTful API for custom integrations
- **Multi-Language**: Supports English and Portuguese patterns

## Next Steps

1. Read the [Full Documentation](docs/)
2. Try the [Example Notebooks](examples/)
3. Configure [Custom Agents](docs/agents.md)
4. Set up [Production Deployment](docs/deployment.md)
