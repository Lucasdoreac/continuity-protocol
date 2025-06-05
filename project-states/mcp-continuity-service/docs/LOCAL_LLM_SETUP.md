# 🤖 Local LLM Setup Guide

## Why Local LLMs?

The MCP Continuity Service supports multiple LLM providers, so users don't need Claude Desktop.

## 🚀 Option 1: Ollama (Recommended)

### Installation
```bash
# macOS/Linux
curl -fsSL https://ollama.ai/install.sh | sh

# Start service
ollama serve
```

### Download Models
```bash
ollama pull llama2        # 7B model
ollama pull codellama     # Code-specialized
ollama pull mistral       # Lightweight
```

### Test
```bash
ollama run llama2
>>> onde paramos?
```

## ⚙️ Configuration

Edit `config/default.json`:
```json
{
  "llm": {
    "default_provider": "ollama",
    "ollama": {
      "enabled": true,
      "model": "llama2"
    }
  }
}
```

## 🍎 AppleScript Integration

Automatically captures:
- Running applications
- Open documents  
- Finder location
- Notes & calendar
- System status

## 🔄 How It Works

1. User: "onde paramos?"
2. Service detects continuity question
3. AppleScript captures macOS context
4. LLM processes with full context
5. Complete response with continuation

**No Claude Desktop needed!** 🎉
