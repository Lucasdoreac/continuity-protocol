"""
Unit tests for context management tools.
"""

import unittest
from unittest.mock import patch, MagicMock
import json
import sys
import os
import shutil
import tempfile
from pathlib import Path

# Add src directory to path for imports
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__)))), "src"))

try:
    from continuity_protocol.tools.context import (
        context_store, context_retrieve, context_switch,
        context_delete, context_list, DEFAULT_NAMESPACE,
        _get_context_path
    )
except ImportError:
    from src.continuity_protocol.tools.context import (
        context_store, context_retrieve, context_switch,
        context_delete, context_list, DEFAULT_NAMESPACE,
        _get_context_path
    )

class TestContextTools(unittest.TestCase):
    """Test cases for context management tools."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create temporary directory for test contexts
        self.test_contexts_dir = tempfile.mkdtemp()
        
        # Save original contexts directory and replace with test directory
        self.original_contexts_dir = os.path.join(os.path.dirname(os.path.dirname(
            os.path.dirname(os.path.abspath(__file__)))), "data", "contexts")
        
        # Patch the CONTEXTS_DIR in the context module
        try:
            import continuity_protocol.tools.context as context_module
        except ImportError:
            import src.continuity_protocol.tools.context as context_module
        self.original_contexts_dir_value = context_module.CONTEXTS_DIR
        context_module.CONTEXTS_DIR = self.test_contexts_dir
    
    def tearDown(self):
        """Tear down test fixtures."""
        # Restore original contexts directory
        try:
            import continuity_protocol.tools.context as context_module
        except ImportError:
            import src.continuity_protocol.tools.context as context_module
        context_module.CONTEXTS_DIR = self.original_contexts_dir_value
        
        # Remove test directory
        shutil.rmtree(self.test_contexts_dir)
    
    def test_context_store_retrieve(self):
        """Test storing and retrieving context."""
        # Store context
        test_key = "test-key"
        test_value = {"data": "test-value"}
        
        store_result = context_store(test_key, test_value)
        
        # Check store result
        self.assertTrue(store_result["success"])
        
        # Check context file exists
        context_path = _get_context_path(test_key)
        self.assertTrue(os.path.isfile(context_path))
        
        # Retrieve context
        retrieve_result = context_retrieve(test_key)
        
        # Check retrieve result
        self.assertTrue(retrieve_result["success"])
        self.assertEqual(retrieve_result["value"], test_value)
    
    def test_context_namespace(self):
        """Test context namespaces."""
        # Store context in custom namespace
        test_key = "test-key"
        test_value = {"data": "test-value"}
        test_namespace = "test-namespace"
        
        store_result = context_store(test_key, test_value, namespace=test_namespace)
        
        # Check store result
        self.assertTrue(store_result["success"])
        
        # Check context file exists in namespace directory
        context_path = _get_context_path(test_key, test_namespace)
        self.assertTrue(os.path.isfile(context_path))
        
        # Retrieve context from namespace
        retrieve_result = context_retrieve(test_key, namespace=test_namespace)
        
        # Check retrieve result
        self.assertTrue(retrieve_result["success"])
        self.assertEqual(retrieve_result["value"], test_value)
        
        # Try to retrieve from default namespace (should fail)
        default_retrieve_result = context_retrieve(test_key)
        self.assertFalse(default_retrieve_result["success"])
    
    def test_context_ttl(self):
        """Test context time-to-live."""
        # Store context with TTL
        test_key = "test-ttl-key"
        test_value = {"data": "test-value"}
        
        # Mock datetime.now() to return a fixed time
        from datetime import datetime, timedelta
        fixed_now = datetime(2023, 1, 1, 12, 0, 0)
        
        patch_path = 'continuity_protocol.tools.context.datetime'
        try:
            import continuity_protocol.tools.context
        except ImportError:
            patch_path = 'src.continuity_protocol.tools.context.datetime'
        with patch(patch_path) as mock_datetime:
            mock_datetime.now.return_value = fixed_now
            mock_datetime.fromisoformat = datetime.fromisoformat  # Keep the real fromisoformat
            
            # Store with 1 hour TTL
            store_result = context_store(test_key, test_value, ttl=3600)
            
            # Check expires_at is set
            self.assertTrue(store_result["success"])
            self.assertIsNotNone(store_result["expires_at"])
            
            # Check we can retrieve it
            retrieve_result = context_retrieve(test_key)
            self.assertTrue(retrieve_result["success"])
            
            # Move time forward 2 hours
            mock_datetime.now.return_value = fixed_now + timedelta(hours=2)
            
            # Check it's expired
            expired_retrieve_result = context_retrieve(test_key)
            self.assertFalse(expired_retrieve_result["success"])
            self.assertIn("expired", expired_retrieve_result["error"].lower())
    
    def test_context_delete(self):
        """Test deleting context."""
        # Store context
        test_key = "test-delete-key"
        test_value = {"data": "test-value"}
        
        store_result = context_store(test_key, test_value)
        self.assertTrue(store_result["success"])
        
        # Delete context
        delete_result = context_delete(test_key)
        self.assertTrue(delete_result["success"])
        
        # Check it's deleted
        retrieve_result = context_retrieve(test_key)
        self.assertFalse(retrieve_result["success"])
    
    def test_context_list(self):
        """Test listing contexts."""
        # Store multiple contexts
        context_store("key1", {"data": "value1"})
        context_store("key2", {"data": "value2"})
        context_store("key3", {"data": "value3"})
        
        # List contexts
        list_result = context_list()
        
        # Check list result
        self.assertTrue(list_result["success"])
        self.assertEqual(list_result["count"], 3)
        
        # Check keys are in list
        context_keys = [context["key"] for context in list_result["contexts"]]
        self.assertIn("key1", context_keys)
        self.assertIn("key2", context_keys)
        self.assertIn("key3", context_keys)
    
    def test_context_switch(self):
        """Test switching contexts."""
        # Mock the active context file
        active_context_path = os.path.join(self.test_contexts_dir, "active_context.json")
        
        # Set initial active context
        initial_context = {
            "context_id": "initial-context",
            "switched_at": datetime.now().isoformat(),
            "previous_context": None
        }
        
        with open(active_context_path, 'w') as f:
            json.dump(initial_context, f)
        
        # Switch to new context
        switch_result = context_switch("new-context")
        
        # Check switch result
        self.assertTrue(switch_result["success"])
        self.assertEqual(switch_result["previous_context"], "initial-context")
        
        # Check active context was updated
        with open(active_context_path, 'r') as f:
            active_context = json.load(f)
        
        self.assertEqual(active_context["context_id"], "new-context")
        self.assertEqual(active_context["previous_context"], "initial-context")

if __name__ == "__main__":
    unittest.main()