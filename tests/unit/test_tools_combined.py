"""
Combined unit tests for all tools.

This file tests the integration between different tool modules to ensure
they work correctly together.
"""

import unittest
from unittest.mock import patch, MagicMock
import json
import sys
import os
import tempfile
import shutil
from datetime import datetime, timedelta
from pathlib import Path

# Add src directory to path for imports
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__)))), "src"))

# Try to import tool modules
try:
    from continuity_protocol.tools.context import (
        context_store, context_retrieve, context_switch,
        context_delete, context_list, DEFAULT_NAMESPACE
    )
    from continuity_protocol.tools.session import (
        session_create, session_save, session_restore,
        session_list, session_delete
    )
    from continuity_protocol.tools.system import (
        system_status, memory_optimize
    )
    TOOLS_AVAILABLE = True
except ImportError:
    try:
        from src.continuity_protocol.tools.context import (
            context_store, context_retrieve, context_switch,
            context_delete, context_list, DEFAULT_NAMESPACE
        )
        from src.continuity_protocol.tools.session import (
            session_create, session_save, session_restore,
            session_list, session_delete
        )
        from src.continuity_protocol.tools.system import (
            system_status, memory_optimize
        )
        TOOLS_AVAILABLE = True
    except ImportError:
        TOOLS_AVAILABLE = False

@unittest.skipIf(not TOOLS_AVAILABLE, "Tool modules not available")
class TestToolsIntegration(unittest.TestCase):
    """Test the integration between different tool modules."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create temporary test directory
        self.test_dir = tempfile.mkdtemp()
        
        # Create subdirectories
        self.contexts_dir = os.path.join(self.test_dir, "contexts")
        self.sessions_dir = os.path.join(self.test_dir, "sessions")
        
        os.makedirs(os.path.join(self.contexts_dir, "default"), exist_ok=True)
        os.makedirs(os.path.join(self.contexts_dir, "_context_history"), exist_ok=True)
        os.makedirs(self.sessions_dir, exist_ok=True)
        
        # Patch directories in modules
        try:
            import continuity_protocol.tools.context as context_module
            import continuity_protocol.tools.session as session_module
            import continuity_protocol.tools.system as system_module
        except ImportError:
            import src.continuity_protocol.tools.context as context_module
            import src.continuity_protocol.tools.session as session_module
            import src.continuity_protocol.tools.system as system_module
        
        # Save original values
        self.original_context_dir = context_module.CONTEXTS_DIR
        self.original_session_dir = session_module.SESSIONS_DIR
        self.original_base_dir = getattr(system_module, "BASE_DIR", self.test_dir)
        
        # Patch with test directories
        context_module.CONTEXTS_DIR = self.contexts_dir
        session_module.SESSIONS_DIR = self.sessions_dir
        system_module.BASE_DIR = self.test_dir
    
    def tearDown(self):
        """Tear down test fixtures."""
        # Restore original values
        try:
            import continuity_protocol.tools.context as context_module
            import continuity_protocol.tools.session as session_module
            import continuity_protocol.tools.system as system_module
        except ImportError:
            import src.continuity_protocol.tools.context as context_module
            import src.continuity_protocol.tools.session as session_module
            import src.continuity_protocol.tools.system as system_module
        
        context_module.CONTEXTS_DIR = self.original_context_dir
        session_module.SESSIONS_DIR = self.original_session_dir
        if hasattr(system_module, "BASE_DIR"):
            system_module.BASE_DIR = self.original_base_dir
        
        # Remove test directory
        shutil.rmtree(self.test_dir)
    
    def test_session_with_context(self):
        """Test creating a session and storing its state in context."""
        # Create a session
        session_result = session_create("Test Session", {"purpose": "testing"})
        self.assertIn("session_id", session_result)
        session_id = session_result["session_id"]
        
        # Create a sample state
        session_state = {
            "conversation": [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Hello!"},
                {"role": "assistant", "content": "Hi there! How can I help you today?"}
            ],
            "metadata": {"topic": "greeting"}
        }
        
        # Save session state
        save_result = session_save(session_id, session_state)
        self.assertTrue(save_result["success"])
        
        # Store session ID in context
        context_result = context_store("current_session", {"session_id": session_id})
        self.assertTrue(context_result["success"])
        
        # Retrieve session ID from context
        retrieve_result = context_retrieve("current_session")
        self.assertTrue(retrieve_result["success"])
        self.assertEqual(retrieve_result["value"]["session_id"], session_id)
        
        # Use retrieved session ID to get session state
        retrieved_session_id = retrieve_result["value"]["session_id"]
        restore_result = session_restore(retrieved_session_id)
        
        # Verify restored state matches original
        self.assertTrue(restore_result["success"])
        self.assertEqual(restore_result["content"], session_state)
    
    def test_system_status_with_session_info(self):
        """Test getting system status with session information."""
        # Create a session
        session_create("System Status Test")
        
        # Get system status with sessions
        status_result = system_status(include_sessions=True)
        
        # Verify system status includes sessions
        self.assertIn("status", status_result)
        self.assertIn("active_sessions", status_result)
        self.assertGreaterEqual(len(status_result["active_sessions"]), 1)
    
    def test_context_namespaces_with_session(self):
        """Test using context namespaces with session IDs."""
        # Create a session
        session_result = session_create("Namespace Test")
        session_id = session_result["session_id"]
        
        # Use session ID as namespace
        context_store("user_preference", {"theme": "dark"}, namespace=session_id)
        context_store("user_preference", {"theme": "light"}, namespace="default")
        
        # Retrieve from both namespaces
        session_theme = context_retrieve("user_preference", namespace=session_id)
        default_theme = context_retrieve("user_preference")
        
        # Verify different values from different namespaces
        self.assertEqual(session_theme["value"]["theme"], "dark")
        self.assertEqual(default_theme["value"]["theme"], "light")
    
    def test_memory_optimization_with_context_cleanup(self):
        """Test memory optimization with context cleanup."""
        # Store some test contexts with different expiry times
        now = datetime.now()
        
        # Mock datetime.now to control the time
        patch_path = 'continuity_protocol.tools.context.datetime'
        try:
            import continuity_protocol.tools.context
        except ImportError:
            patch_path = 'src.continuity_protocol.tools.context.datetime'
        
        with patch(patch_path) as mock_datetime:
            # Fix the current time
            mock_datetime.now.return_value = now
            mock_datetime.fromisoformat = datetime.fromisoformat
            
            # Store a context that expires in 1 hour
            context_store("short_lived", {"data": "expires_soon"}, ttl=3600)
            
            # Store a context that expires in 1 day
            context_store("long_lived", {"data": "expires_later"}, ttl=86400)
            
            # Store a context with no expiry
            context_store("permanent", {"data": "never_expires"})
            
            # Advance time by 2 hours
            mock_datetime.now.return_value = now + timedelta(hours=2)
            
            # Check context list contains the expected contexts
            list_result = context_list()
            context_keys = [ctx["key"] for ctx in list_result["contexts"]]
            self.assertIn("long_lived", context_keys)
            self.assertIn("permanent", context_keys)
            self.assertNotIn("short_lived", context_keys)  # Should be expired
    
    def test_full_workflow(self):
        """Test a complete workflow using multiple tools together."""
        # 1. Create a session
        session_result = session_create("Full Workflow Test")
        session_id = session_result["session_id"]
        
        # 2. Store some context data
        context_store("session_context", {
            "session_id": session_id,
            "user_preferences": {"language": "en", "theme": "dark"},
            "history_enabled": True
        })
        
        # 3. Save some state in the session
        session_state = {
            "conversation": [{"role": "system", "content": "You are an assistant."}],
            "metadata": {"started_at": datetime.now().isoformat()}
        }
        session_save(session_id, session_state)
        
        # 4. Update the session state
        session_state["conversation"].append(
            {"role": "user", "content": "What's the weather?"}
        )
        session_state["conversation"].append(
            {"role": "assistant", "content": "I don't have access to weather data."}
        )
        session_save(session_id, session_state)
        
        # 5. Retrieve session context
        context_result = context_retrieve("session_context")
        self.assertTrue(context_result["success"])
        retrieved_session_id = context_result["value"]["session_id"]
        self.assertEqual(retrieved_session_id, session_id)
        
        # 6. Restore session using retrieved ID
        restore_result = session_restore(retrieved_session_id)
        self.assertTrue(restore_result["success"])
        
        # Verify the restored conversation has all messages
        self.assertEqual(len(restore_result["content"]["conversation"]), 3)
        
        # 7. Check system status
        status_result = system_status(include_sessions=True)
        self.assertIn(session_id, [s["id"] for s in status_result["active_sessions"]])
        
        # 8. Clean up
        session_delete(session_id)
        context_delete("session_context")
        
        # Verify session is gone
        list_result = session_list()
        self.assertEqual(list_result["count"], 0)

if __name__ == "__main__":
    unittest.main()