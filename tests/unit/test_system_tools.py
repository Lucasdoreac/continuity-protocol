"""
Unit tests for system management tools.
"""

import unittest
from unittest.mock import patch, MagicMock
import json
import sys
import os
import tempfile
from datetime import datetime

# Add src directory to path for imports
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__)))), "src"))

# Import system tools
try:
    from continuity_protocol.tools.system import (
        system_status, memory_optimize
    )
    SYSTEM_TOOLS_AVAILABLE = True
except ImportError:
    SYSTEM_TOOLS_AVAILABLE = False


@unittest.skipIf(not SYSTEM_TOOLS_AVAILABLE, "System tools not available")
class TestSystemTools(unittest.TestCase):
    """Test cases for system management tools."""
    
    def test_system_status(self):
        """Test getting system status."""
        # Test basic status (no sessions or metrics)
        status = system_status()
        
        # Basic assertions
        self.assertIn("status", status)
        self.assertIn("version", status)
        self.assertIn("uptime_seconds", status)
        
        # Status should be one of the valid values
        self.assertIn(status["status"], ["healthy", "degraded", "error"])
        
        # Test with sessions
        status_with_sessions = system_status(include_sessions=True)
        self.assertIn("active_sessions", status_with_sessions)
        
        # Test with metrics
        with patch('psutil.cpu_percent', return_value=50.0):
            with patch('psutil.virtual_memory', return_value=MagicMock(percent=60.0)):
                with patch('psutil.disk_usage', return_value=MagicMock(percent=70.0)):
                    status_with_metrics = system_status(include_metrics=True)
                    
                    self.assertIn("metrics", status_with_metrics)
                    self.assertIn("cpu_percent", status_with_metrics["metrics"])
                    self.assertIn("memory_percent", status_with_metrics["metrics"])
                    self.assertIn("disk_percent", status_with_metrics["metrics"])
                    
                    self.assertEqual(status_with_metrics["metrics"]["cpu_percent"], 50.0)
                    self.assertEqual(status_with_metrics["metrics"]["memory_percent"], 60.0)
                    self.assertEqual(status_with_metrics["metrics"]["disk_percent"], 70.0)
    
    def test_memory_optimize(self):
        """Test memory optimization."""
        # Create a temporary directory for test
        with tempfile.TemporaryDirectory() as temp_dir:
            # Mock session directory
            session_dir = os.path.join(temp_dir, "sessions")
            os.makedirs(session_dir)
            
            # Mock context directory with some expired contexts
            contexts_dir = os.path.join(temp_dir, "contexts")
            os.makedirs(os.path.join(contexts_dir, "default"))
            
            # Create an expired context file
            expired_context = {
                "key": "expired-key",
                "value": {"data": "test-value"},
                "stored_at": "2020-01-01T00:00:00",
                "expires_at": "2020-01-01T01:00:00",
                "namespace": "default"
            }
            
            with open(os.path.join(contexts_dir, "default", "expired.json"), 'w') as f:
                json.dump(expired_context, f)
            
            # Mock the memory usage before and after
            memory_before = 1000000  # 1MB
            memory_after = 900000    # 0.9MB
            
            with patch('psutil.Process') as mock_process:
                # Mock memory_info method
                mock_memory_info = MagicMock()
                mock_memory_info.rss = memory_before
                mock_process.return_value.memory_info.return_value = mock_memory_info
                
                # Patch directories
                patch_path = 'continuity_protocol.tools.system.BASE_DIR'
                try:
                    import continuity_protocol.tools.system
                except ImportError:
                    patch_path = 'src.continuity_protocol.tools.system.BASE_DIR'
                with patch(patch_path, temp_dir):
                    # First memory_info call returns memory_before, second call returns memory_after
                    mock_process.return_value.memory_info.side_effect = [
                        MagicMock(rss=memory_before),
                        MagicMock(rss=memory_after)
                    ]
                    
                    # Test memory optimization
                    result = memory_optimize(level="light")
                    
                    # Assertions
                    self.assertTrue(result["success"])
                    self.assertEqual(result["memory_reduced_bytes"], memory_before - memory_after)
                    self.assertEqual(result["memory_reduced_mb"], (memory_before - memory_after) / (1024 * 1024))
                    self.assertEqual(result["optimization_level"], "light")
                    self.assertIn("optimization_details", result)
    
    def test_memory_optimize_with_session(self):
        """Test memory optimization for a specific session."""
        # Create a temporary directory for test
        with tempfile.TemporaryDirectory() as temp_dir:
            # Mock session directory
            session_dir = os.path.join(temp_dir, "sessions", "test-session")
            os.makedirs(session_dir)
            
            # Create a session metadata file
            session_metadata = {
                "session_id": "test-session",
                "name": "Test Session",
                "created_at": "2023-01-01T00:00:00",
                "updated_at": "2023-01-01T01:00:00",
                "metadata": {},
                "versions": [
                    {
                        "version": 1,
                        "saved_at": "2023-01-01T00:30:00",
                        "compression_level": 0,
                        "size": 1000
                    },
                    {
                        "version": 2,
                        "saved_at": "2023-01-01T01:00:00",
                        "compression_level": 0,
                        "size": 2000
                    }
                ]
            }
            
            with open(os.path.join(session_dir, "metadata.json"), 'w') as f:
                json.dump(session_metadata, f)
            
            # Create version files
            with open(os.path.join(session_dir, "version_1.json"), 'w') as f:
                json.dump({"data": "version 1"}, f)
            
            with open(os.path.join(session_dir, "version_2.json"), 'w') as f:
                json.dump({"data": "version 2"}, f)
            
            # Mock the memory usage before and after
            memory_before = 1000000  # 1MB
            memory_after = 900000    # 0.9MB
            
            with patch('psutil.Process') as mock_process:
                # Mock memory_info method
                mock_process.return_value.memory_info.side_effect = [
                    MagicMock(rss=memory_before),
                    MagicMock(rss=memory_after)
                ]
                
                # Patch directories and session methods
                patch_path = 'continuity_protocol.tools.system.BASE_DIR'
                try:
                    import continuity_protocol.tools.system
                except ImportError:
                    patch_path = 'src.continuity_protocol.tools.system.BASE_DIR'
                with patch(patch_path, temp_dir):
                    # Test memory optimization for the session
                    result = memory_optimize(target_session="test-session", level="aggressive")
                    
                    # Assertions
                    self.assertTrue(result["success"])
                    self.assertEqual(result["memory_reduced_bytes"], memory_before - memory_after)
                    self.assertEqual(result["memory_reduced_mb"], (memory_before - memory_after) / (1024 * 1024))
                    self.assertEqual(result["optimization_level"], "aggressive")
                    self.assertIn("optimization_details", result)
                    self.assertIn("session", result["optimization_details"])
                    self.assertEqual(result["optimization_details"]["session"]["session_id"], "test-session")

if __name__ == "__main__":
    unittest.main()