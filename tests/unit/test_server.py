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

try:
    from continuity_protocol.server import MCPServer
except ImportError:
    from src.continuity_protocol.server import MCPServer

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

    def test_register_tool_with_auto_description(self):
        """Test registering a tool with auto-generated description."""
        def sample_tool(arg1: str, arg2: int = 42) -> Dict[str, Any]:
            """A sample tool for testing auto-description generation."""
            return {"arg1": arg1, "arg2": arg2}

        self.server.register_tool("sample_tool", sample_tool)

        # Verify tool was registered
        self.assertIn("sample_tool", self.server.tools)
        self.assertIn("sample_tool", self.server.descriptions)

        # Verify description was auto-generated
        description = self.server.descriptions["sample_tool"]
        self.assertEqual(description["name"], "sample_tool")
        self.assertIn("A sample tool", description["description"])

        # Verify parameters were extracted correctly
        self.assertIn("arg1", description["parameters"]["properties"])
        self.assertIn("arg2", description["parameters"]["properties"])
        self.assertEqual(description["parameters"]["properties"]["arg1"]["type"], "string")
        self.assertEqual(description["parameters"]["properties"]["arg2"]["type"], "integer")
        self.assertIn("arg1", description["parameters"]["required"])
        self.assertNotIn("arg2", description["parameters"]["required"])  # arg2 has default value

    def test_register_default_tools(self):
        """Test registering default tools."""
        # Create a fresh server
        fresh_server = MCPServer("Fresh-Server")

        # Mock the tools module
        with patch("continuity_protocol.tools.session.session_create") as mock_session_create, \
             patch("continuity_protocol.tools.context.context_store") as mock_context_store, \
             patch("continuity_protocol.tools.system.system_status") as mock_system_status:

            # Register default tools
            try:
                fresh_server.register_default_tools()

                # Verify tools were registered
                self.assertIn("session_create", fresh_server.tools)
                self.assertIn("context_store", fresh_server.tools)
                self.assertIn("system_status", fresh_server.tools)
            except ImportError:
                # If imports fail, test is skipped
                self.skipTest("Default tools not available")

    def test_full_request_response_cycle(self):
        """Test a complete request-response cycle with a real tool."""
        # Register a real tool
        def add_numbers(a: int, b: int) -> Dict[str, Any]:
            """Add two numbers and return the result."""
            return {"sum": a + b}

        self.server.register_tool("add_numbers", add_numbers)

        # Create a request
        request = {
            "jsonrpc": "2.0",
            "id": "test-add",
            "method": "execute",
            "params": {
                "tool": "add_numbers",
                "parameters": {
                    "a": 5,
                    "b": 7
                }
            }
        }

        # Handle the request
        response = self.server.handle_request(request)

        # Verify response
        self.assertEqual(response["jsonrpc"], "2.0")
        self.assertEqual(response["id"], "test-add")
        self.assertEqual(response["result"]["sum"], 12)

if __name__ == "__main__":
    unittest.main()