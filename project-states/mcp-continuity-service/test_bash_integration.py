#!/usr/bin/env python3
"""
Teste direto da integração bash
"""

import sys
import asyncio
import os
sys.path.append('/Users/lucascardoso/apps/MCP/CONTINUITY/project-states/mcp-continuity-service/src')

from services.bash_scripts_service import BashScriptsService

async def test_bash_integration():
    print("🧪 Testando integração bash...")
    
    bash_service = BashScriptsService()
    
    # Teste 1: onde paramos?
    print("\n1. Testando recovery_where_stopped...")
    result = await bash_service.recovery_where_stopped()
    print(f"Success: {result['success']}")
    if result['success']:
        print(f"Output: {result['output'][:200]}...")
    else:
        print(f"Error: {result['error']}")
    
    # Teste 2: processamento de input
    print("\n2. Testando process_continuity_request...")
    result = await bash_service.process_continuity_request("onde paramos?")
    print(f"Success: {result['success']}")
    if result['success']:
        print(f"Output: {result['output'][:200]}...")
    else:
        print(f"Error: {result['error']}")
    
    # Teste 3: status do sistema
    print("\n3. Testando system_status...")
    result = await bash_service.system_status()
    print(f"Success: {result['success']}")
    if result['success']:
        print(f"Output: {result['output'][:200]}...")
    else:
        print(f"Error: {result['error']}")

if __name__ == "__main__":
    asyncio.run(test_bash_integration())
