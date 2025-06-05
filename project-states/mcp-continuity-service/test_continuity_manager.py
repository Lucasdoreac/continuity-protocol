#!/usr/bin/env python3
"""
Teste direto do ContinuityManager
"""

import sys
import asyncio
import os
sys.path.append('/Users/lucascardoso/apps/MCP/CONTINUITY/project-states/mcp-continuity-service/src')

from core.continuity_manager import ContinuityManager
from core.context_detector import ContextDetector

async def test_continuity_manager():
    print("🧪 Testando ContinuityManager completo...")
    
    # Teste 1: ContextDetector isolado
    print("\n1. Testando ContextDetector...")
    detector = ContextDetector()
    is_continuity = await detector.is_continuity_question("onde paramos?")
    print(f"'onde paramos?' detectado como continuity: {is_continuity}")
    
    # Teste 2: ContinuityManager completo
    print("\n2. Testando ContinuityManager...")
    manager = ContinuityManager()
    
    try:
        result = await manager.process_user_input("onde paramos?", "test-session")
        print(f"Result type: {result.get('type')}")
        print(f"Result method: {result.get('method', 'not specified')}")
        if result.get('content'):
            print(f"Content preview: {result['content'][:200]}...")
        else:
            print(f"Full result: {result}")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_continuity_manager())
