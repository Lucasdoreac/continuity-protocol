"""
Example usage of MCP Continuity Service
"""

import asyncio
from src.core.continuity_manager import ContinuityManager

async def main():
    # Initialize the continuity manager
    manager = ContinuityManager()
    
    print("🔄 MCP Continuity Service Example")
    print("=" * 40)
    
    # Example session ID
    session_id = "example-session-001"
    
    # Simulate normal input first
    print("\n1. Normal input processing:")
    result = await manager.process_user_input(
        user_input="I'm working on a Python project",
        session_id=session_id
    )
    print(f"Response: {result['type']}")
    
    # Now try a continuity question
    print("\n2. Continuity question:")
    result = await manager.process_user_input(
        user_input="onde paramos?",
        session_id=session_id
    )
    
    if result['type'] == 'continuity_response':
        print("✅ Continuity question detected!")
        print(f"Summary: {result.get('summary', 'No summary')}")
        print(f"Projects: {result.get('projects', [])}")
        print(f"Critical missions: {result.get('critical_missions', [])}")
        print(f"Next actions: {result.get('next_actions', [])}")
    
    # Try English continuity question  
    print("\n3. English continuity question:")
    result = await manager.process_user_input(
        user_input="where did we leave off?",
        session_id=session_id
    )
    
    if result['type'] == 'continuity_response':
        print("✅ English continuity question detected!")
    
    print("\n🎉 Example completed!")

if __name__ == "__main__":
    asyncio.run(main())
