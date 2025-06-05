"""
Unit tests for session management tools.
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

from continuity_protocol.tools.session import (
    session_create, session_save, session_restore, 
    session_list, session_delete, SESSIONS_DIR
)

class TestSessionTools(unittest.TestCase):
    """Test cases for session management tools."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create temporary directory for test sessions
        self.test_sessions_dir = tempfile.mkdtemp()
        
        # Save original sessions directory and replace with test directory
        self.original_sessions_dir = SESSIONS_DIR
        import continuity_protocol.tools.session as session_module
        session_module.SESSIONS_DIR = self.test_sessions_dir
    
    def tearDown(self):
        """Tear down test fixtures."""
        # Restore original sessions directory
        import continuity_protocol.tools.session as session_module
        session_module.SESSIONS_DIR = self.original_sessions_dir
        
        # Remove test directory
        shutil.rmtree(self.test_sessions_dir)
    
    def test_session_create(self):
        """Test creating a session."""
        result = session_create("Test Session", {"key": "value"})
        
        # Check result
        self.assertIn("session_id", result)
        self.assertIn("created_at", result)
        
        # Check that session directory was created
        session_id = result["session_id"]
        session_dir = os.path.join(self.test_sessions_dir, session_id)
        self.assertTrue(os.path.isdir(session_dir), f"Session directory not created: {session_dir}")
        
        # Check metadata file
        metadata_path = os.path.join(session_dir, "metadata.json")
        self.assertTrue(os.path.isfile(metadata_path), f"Metadata file not created: {metadata_path}")
        
        # Verify metadata content
        with open(metadata_path, 'r') as f:
            metadata = json.load(f)
        
        self.assertEqual(metadata["name"], "Test Session")
        self.assertEqual(metadata["metadata"]["key"], "value")
        self.assertEqual(metadata["session_id"], session_id)
        self.assertEqual(len(metadata["versions"]), 0)
    
    def test_session_save_restore(self):
        """Test saving and restoring session state."""
        # Create a session
        create_result = session_create("Test Session")
        session_id = create_result["session_id"]
        
        # Test content to save
        test_content = {
            "conversation": [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Hello!"},
                {"role": "assistant", "content": "Hi there! How can I help you today?"}
            ],
            "state": {
                "conversation_id": "12345",
                "current_topic": "greeting"
            }
        }
        
        # Save session state
        save_result = session_save(session_id, test_content, compression_level=0)
        
        # Check save result
        self.assertTrue(save_result["success"])
        self.assertEqual(save_result["version"], 1)
        self.assertIn("saved_at", save_result)
        
        # Check version file
        session_dir = os.path.join(self.test_sessions_dir, session_id)
        version_path = os.path.join(session_dir, f"version_1.json")
        self.assertTrue(os.path.isfile(version_path), f"Version file not created: {version_path}")
        
        # Restore session state
        restore_result = session_restore(session_id)
        
        # Check restore result
        self.assertTrue(restore_result["success"])
        self.assertEqual(restore_result["version"], 1)
        self.assertEqual(restore_result["content"], test_content)
    
    def test_session_list_delete(self):
        """Test listing and deleting sessions."""
        # Create two sessions
        session1 = session_create("Session 1")
        session2 = session_create("Session 2")
        
        # Clear any other sessions that might exist from other tests
        for item in os.listdir(self.test_sessions_dir):
            if item not in [session1["session_id"], session2["session_id"]]:
                item_path = os.path.join(self.test_sessions_dir, item)
                if os.path.isdir(item_path):
                    shutil.rmtree(item_path)
        
        # List sessions
        list_result = session_list()
        
        # Check list result
        self.assertTrue(list_result["success"])
        self.assertEqual(list_result["count"], 2, f"Expected 2 sessions, got {list_result['count']}. Sessions: {list_result['sessions']}")
        
        # Find session IDs in list
        session_ids = [s["session_id"] for s in list_result["sessions"]]
        self.assertIn(session1["session_id"], session_ids)
        self.assertIn(session2["session_id"], session_ids)
        
        # Delete first session
        delete_result = session_delete(session1["session_id"])
        
        # Check delete result
        self.assertTrue(delete_result["success"])
        self.assertEqual(delete_result["session_id"], session1["session_id"])
        
        # List sessions again
        list_result = session_list()
        
        # Check that only one session remains
        self.assertTrue(list_result["success"])
        self.assertEqual(list_result["count"], 1)
        self.assertEqual(list_result["sessions"][0]["session_id"], session2["session_id"])
    
    def test_nonexistent_session(self):
        """Test operations on non-existent sessions."""
        nonexistent_id = "nonexistent-session-id"
        
        # Try to save to non-existent session
        save_result = session_save(nonexistent_id, {"test": "data"})
        self.assertFalse(save_result["success"])
        
        # Try to restore non-existent session
        restore_result = session_restore(nonexistent_id)
        self.assertFalse(restore_result["success"])
        
        # Try to delete non-existent session
        delete_result = session_delete(nonexistent_id)
        self.assertFalse(delete_result["success"])
    
    def test_multiple_versions(self):
        """Test saving multiple versions of a session."""
        # Create a session
        create_result = session_create("Multi-Version Test")
        session_id = create_result["session_id"]
        
        # Save first version
        content1 = {"version": 1, "data": "Initial data"}
        session_save(session_id, content1)
        
        # Save second version
        content2 = {"version": 2, "data": "Updated data"}
        session_save(session_id, content2)
        
        # Save third version
        content3 = {"version": 3, "data": "Final data"}
        session_save(session_id, content3)
        
        # Restore latest version (no version specified)
        restore_result = session_restore(session_id)
        self.assertEqual(restore_result["content"], content3)
        
        # Restore specific version
        restore_result = session_restore(session_id, version=2)
        self.assertEqual(restore_result["content"], content2)

if __name__ == "__main__":
    unittest.main()