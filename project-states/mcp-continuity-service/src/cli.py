"""
MCP Continuity Service CLI
"""

import click
import uvicorn
import subprocess
import os
import asyncio
import json
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.json import JSON

console = Console()

@click.group()
def main():
    """MCP Continuity Service CLI"""
    pass

@main.command()
@click.option("--host", default="127.0.0.1")
@click.option("--port", default=8000)
def start(host: str, port: int):
    """Start the continuity service API"""
    console.print(Panel("🚀 Starting MCP Continuity Service"))
    uvicorn.run("src.api.main:app", host=host, port=port, reload=True)

@main.command()
@click.option("--port", default=8501)
def ui(port: int):
    """Launch Streamlit UI"""
    console.print(Panel("🎨 Launching Streamlit UI"))
    subprocess.run(["streamlit", "run", "frontend/streamlit_app.py", "--server.port", str(port)])

@main.command()
def init():
    """Initialize continuity service"""
    console.print(Panel("🔧 Initializing MCP Continuity Service"))
    
    directories = ["data", "logs", "backups", "data/sessions", "data/states"]
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        console.print(f"✅ Created: {directory}")
    
    console.print("🎉 Initialized successfully!")

@main.command()
@click.argument("input_text", required=True)
@click.option("--session-id", default="cli-session")
@click.option("--format", default="pretty", type=click.Choice(["pretty", "json"]))
def process(input_text: str, session_id: str, format: str):
    """Process user input through the continuity system"""
    console.print(Panel(f"🎯 Processing: {input_text}"))
    
    # Import here to avoid circular imports
    from .core.continuity_manager import ContinuityManager
    
    async def run_process():
        manager = ContinuityManager()
        result = await manager.process_user_input(
            user_input=input_text,
            session_id=session_id
        )
        return result
    
    try:
        # Run async function
        result = asyncio.run(run_process())
        
        if format == "json":
            console.print(JSON(json.dumps(result, indent=2)))
        else:
            # Pretty format
            console.print(Panel(f"📋 Type: {result.get('type', 'unknown')}", title="Result"))
            
            if result.get('content'):
                console.print(Panel(result['content'], title="Content"))
            
            if result.get('projects'):
                console.print(Panel(f"Projects: {len(result['projects'])}", title="Projects"))
                
            if result.get('critical_missions'):
                console.print(Panel(f"Critical Missions: {len(result['critical_missions'])}", title="Missions"))
                
            if result.get('next_actions'):
                console.print(Panel(str(result['next_actions']), title="Next Actions"))
    
    except Exception as e:
        console.print(f"❌ Error: {e}")
        raise click.ClickException(str(e))

if __name__ == "__main__":
    main()
