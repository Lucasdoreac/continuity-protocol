"""
Unit tests for the MCP server.
"""

import unittest
from unittest.mock import patch, MagicMock
import json
import sys
import os

# Add src directory to path for imports
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__)))), "src"))

from continuity_protocol.server import MCPServer

class TestMCPServer(unittest.TestCase):
    """Test cases for the MCPServer class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.server = MCPServer("Test-Server")
        
        # Register a mock tool
        self.mock_tool = MagicMock(return_value={"result": "success"})
        self.server.register_tool(
            "test_tool", 
            self.mock_tool, 
            {"description": "Test tool for unit testing"}
        )
    
    def test_initialization(self):
        """Test server initialization."""
        self.assertEqual(self.server.name, "Test-Server")
        self.assertIn("test_tool", self.server.tools)
        self.assertIn("test_tool", self.server.descriptions)
    
    def test_handle_valid_request(self):
        """Test handling a valid request."""
        request = {
            "jsonrpc": "2.0",
            "id": "test-1",
            "method": "execute",
            "params": {
                "tool": "test_tool",
                "parameters": {
                    "arg1": "value1",
                    "arg2": "value2"
                }
            }
        }
        
        response = self.server.handle_request(request)
        
        self.assertEqual(response["jsonrpc"], "2.0")
        self.assertEqual(response["id"], "test-1")
        self.assertEqual(response["result"], {"result": "success"})
        
        # Verify mock was called with correct arguments
        self.mock_tool.assert_called_once_with(arg1="value1", arg2="value2")
    
    def test_handle_invalid_jsonrpc(self):
        """Test handling a request with invalid JSON-RPC version."""
        request = {
            "jsonrpc": "1.0",  # Invalid version
            "id": "test-2",
            "method": "execute",
            "params": {
                "tool": "test_tool",
                "parameters": {}
            }
        }
        
        response = self.server.handle_request(request)
        
        self.assertEqual(response["jsonrpc"], "2.0")
        self.assertEqual(response["id"], "test-2")
        self.assertIn("error", response)
        self.assertEqual(response["error"]["code"], -32600)
    
    def test_handle_invalid_method(self):
        """Test handling a request with invalid method."""
        request = {
            "jsonrpc": "2.0",
            "id": "test-3",
            "method": "invalid_method",  # Invalid method
            "params": {
                "tool": "test_tool",
                "parameters": {}
            }
        }
        
        response = self.server.handle_request(request)
        
        self.assertEqual(response["jsonrpc"], "2.0")
        self.assertEqual(response["id"], "test-3")
        self.assertIn("error", response)
        self.assertEqual(response["error"]["code"], -32601)
    
    def test_handle_invalid_tool(self):
        """Test handling a request with invalid tool."""
        request = {
            "jsonrpc": "2.0",
            "id": "test-4",
            "method": "execute",
            "params": {
                "tool": "nonexistent_tool",  # Invalid tool
                "parameters": {}
            }
        }
        
        response = self.server.handle_request(request)
        
        self.assertEqual(response["jsonrpc"], "2.0")
        self.assertEqual(response["id"], "test-4")
        self.assertIn("error", response)
        self.assertEqual(response["error"]["code"], -32601)
    
    def test_tool_exception(self):
        """Test handling an exception thrown by a tool."""
        # Register a tool that raises an exception
        def exception_tool():
            raise ValueError("Test exception")
        
        self.server.register_tool("exception_tool", exception_tool)
        
        request = {
            "jsonrpc": "2.0",
            "id": "test-5",
            "method": "execute",
            "params": {
                "tool": "exception_tool",
                "parameters": {}
            }
        }
        
        response = self.server.handle_request(request)
        
        self.assertEqual(response["jsonrpc"], "2.0")
        self.assertEqual(response["id"], "test-5")
        self.assertIn("error", response)
        self.assertEqual(response["error"]["code"], -32603)
        self.assertIn("Test exception", response["error"]["message"])
    
    def test_get_tool_descriptions(self):
        """Test getting tool descriptions."""
        descriptions = self.server.get_tool_descriptions()
        
        self.assertEqual(len(descriptions), 1)
        self.assertEqual(descriptions[0]["description"], "Test tool for unit testing")

if __name__ == "__main__":
    unittest.main()