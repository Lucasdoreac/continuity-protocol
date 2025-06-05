"""
Complete Example: MCP Continuity with Local LLMs and AppleScript
"""

import asyncio
import json
from src.core.continuity_manager import ContinuityManager

async def demo_local_llm_continuity():
    """Demonstrate continuity with local LLMs and AppleScript integration"""
    
    print("🤖 MCP Continuity Service - Complete Local Demo")
    print("=" * 60)
    
    # Configuration for local LLM
    config = {
        "llm": {
            "default_provider": "ollama",
            "ollama": {
                "enabled": True,
                "host": "localhost:11434",
                "model": "llama2"
            }
        },
        "applescript": {
            "enabled": True,
            "capture_system_context": True,
            "save_to_notes": True
        }
    }
    
    # Initialize continuity manager
    manager = ContinuityManager(config)
    session_id = "local-demo-session"
    
    print("1. 🔍 Checking available LLM providers:")
    providers = await manager.get_llm_providers()
    print(f"   Available: {providers}")
    
    print("\n2. 🏥 Health check of LLM services:")
    health = await manager.health_check_llm()
    for provider, status in health.items():
        print(f"   {provider}: {status['status']}")
    
    print("\n3. 🍎 Capturing macOS context with AppleScript:")
    if manager.applescript_service.available:
        context = await manager.applescript_service.capture_system_context()
        print(f"   - Running apps: {len(context.get('applications', []))}")
        print(f"   - Frontmost app: {context.get('frontmost_app', {}).get('name', 'Unknown')}")
        print(f"   - Open documents: {len(context.get('open_documents', []))}")
        print(f"   - Recent notes: {len(context.get('notes', []))}")
    else:
        print("   AppleScript not available (not on macOS)")
    
    print("\n4. 💬 Simulating conversation with continuity:")
    
    # Simulate some work context
    await manager.session_manager.save_input(
        "I'm working on the MCP Continuity Service project. "
        "I just implemented local LLM support and AppleScript integration.",
        session_id
    )
    
    # Add a project to the session
    await manager.session_manager.add_project(session_id, {
        "name": "MCP Continuity Service",
        "status": "in_progress",
        "last_action": "Added local LLM support",
        "next_steps": ["Test Ollama integration", "Document AppleScript features"]
    })
    
    print("\n   User: onde paramos?")
    print("   🤖 Processing with local LLM...")
    
    # Process continuity question
    result = await manager.process_user_input("onde paramos?", session_id)
    
    if result['type'] == 'continuity_response':
        print(f"\n   Assistant Response:")
        print(f"   {result.get('content', 'No content generated')}")
        
        print(f"\n   📊 Context Summary: {result.get('summary', 'No summary')}")
        
        if result.get('projects'):
            print(f"   📁 Active Projects: {len(result['projects'])}")
        
        if result.get('system_context'):
            sys_ctx = result['system_context']
            if sys_ctx.get('applications'):
                print(f"   🖥️  System Apps: {len(sys_ctx['applications'])} running")
    
    print("\n5. 📝 Note saved to Apple Notes (if enabled)")
    
    print("\n6. 🧪 Testing different continuity questions:")
    
    questions = [
        "what were we doing?",
        "continue from where we stopped",
        "qual o status do projeto?"
    ]
    
    for question in questions:
        is_continuity = await manager.context_detector.is_continuity_question(question)
        print(f"   '{question}' → {'✅ Detected' if is_continuity else '❌ Not detected'}")
    
    print("\n🎉 Local LLM + AppleScript demo completed!")
    print("\nKey features demonstrated:")
    print("✅ Local LLM integration (no Claude Desktop needed)")
    print("✅ AppleScript system context capture")
    print("✅ Automatic continuity detection")
    print("✅ Multi-language support (PT/EN)")
    print("✅ Context preservation and recovery")
    print("✅ Apple Notes integration")

if __name__ == "__main__":
    asyncio.run(demo_local_llm_continuity())
