"""
Integration tests for the full server workflow.

These tests verify that the server, tools, and transport layers
work together correctly in a complete workflow.
"""

import unittest
import json
import sys
import os
import tempfile
import shutil
import threading
import time
import uuid
import requests
from pathlib import Path

# Add src directory to path for imports
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__)))), "src"))

try:
    from continuity_protocol.server import MCPServer
    from continuity_protocol.transport.http import start_server
except ImportError:
    from src.continuity_protocol.server import MCPServer
    from src.continuity_protocol.transport.http import start_server

class TestFullServerWorkflow(unittest.TestCase):
    """Integration tests for full server workflow."""
    
    @classmethod
    def setUpClass(cls):
        """Set up the test server."""
        # Create a unique test data directory
        cls.test_data_dir = tempfile.mkdtemp()
        
        # Setup data subdirectories
        os.makedirs(os.path.join(cls.test_data_dir, "contexts", "default"), exist_ok=True)
        os.makedirs(os.path.join(cls.test_data_dir, "contexts", "_context_history"), exist_ok=True)
        os.makedirs(os.path.join(cls.test_data_dir, "sessions"), exist_ok=True)
        
        # Create server instance
        cls.server = MCPServer("Integration-Test-Server")
        
        # Register tools
        def add(a, b):
            return {"result": a + b}
        
        def echo(message):
            return {"message": message}
        
        cls.server.register_tool("add", add, {
            "description": "Add two numbers",
            "parameters": {
                "type": "object",
                "properties": {
                    "a": {"type": "number"},
                    "b": {"type": "number"}
                },
                "required": ["a", "b"]
            }
        })
        
        cls.server.register_tool("echo", echo, {
            "description": "Echo a message",
            "parameters": {
                "type": "object",
                "properties": {
                    "message": {"type": "string"}
                },
                "required": ["message"]
            }
        })
        
        # Start server in a separate thread
        cls.server_port = 8765  # Use a fixed port for testing
        cls.server_thread = threading.Thread(
            target=start_server,
            args=(cls.server, cls.server_port),
            daemon=True
        )
        cls.server_thread.start()
        
        # Wait for server to start
        time.sleep(1)
        
        # Server base URL
        cls.server_url = f"http://localhost:{cls.server_port}"
    
    @classmethod
    def tearDownClass(cls):
        """Clean up after tests."""
        # Remove test data directory
        shutil.rmtree(cls.test_data_dir)
    
    def test_tool_execution(self):
        """Test executing a tool via HTTP."""
        # Create a request to add two numbers
        request = {
            "jsonrpc": "2.0",
            "id": "test-1",
            "method": "execute",
            "params": {
                "tool": "add",
                "parameters": {
                    "a": 5,
                    "b": 7
                }
            }
        }
        
        # Send request to server
        response = requests.post(
            f"{self.server_url}/mcp",
            json=request,
            headers={"Content-Type": "application/json"}
        )
        
        # Check response
        self.assertEqual(response.status_code, 200)
        
        # Parse response
        response_data = response.json()
        
        # Verify response
        self.assertEqual(response_data["jsonrpc"], "2.0")
        self.assertEqual(response_data["id"], "test-1")
        self.assertEqual(response_data["result"]["result"], 12)
    
    def test_tool_descriptions(self):
        """Test getting tool descriptions via HTTP."""
        # Send request to get tool descriptions
        response = requests.get(
            f"{self.server_url}/tools",
            headers={"Content-Type": "application/json"}
        )
        
        # Check response
        self.assertEqual(response.status_code, 200)
        
        # Parse response
        response_data = response.json()
        
        # Verify response contains our tools
        self.assertIn("tools", response_data)
        
        # Extract tool names
        tool_names = [tool["name"] for tool in response_data["tools"]]
        
        # Verify our tools are present
        self.assertIn("add", tool_names)
        self.assertIn("echo", tool_names)
    
    def test_invalid_request(self):
        """Test sending an invalid request."""
        # Create an invalid request (missing required parameters)
        request = {
            "jsonrpc": "2.0",
            "id": "test-invalid",
            "method": "execute",
            "params": {
                "tool": "add",
                "parameters": {
                    "a": 5
                    # Missing 'b' parameter
                }
            }
        }
        
        # Send request to server
        response = requests.post(
            f"{self.server_url}/mcp",
            json=request,
            headers={"Content-Type": "application/json"}
        )
        
        # Check response
        self.assertEqual(response.status_code, 200)
        
        # Parse response
        response_data = response.json()
        
        # Verify response contains error
        self.assertIn("error", response_data)
        self.assertEqual(response_data["id"], "test-invalid")
    
    def test_multiple_requests(self):
        """Test sending multiple requests in sequence."""
        # First request: add numbers
        add_request = {
            "jsonrpc": "2.0",
            "id": "test-add",
            "method": "execute",
            "params": {
                "tool": "add",
                "parameters": {
                    "a": 10,
                    "b": 20
                }
            }
        }
        
        # Second request: echo message
        echo_request = {
            "jsonrpc": "2.0",
            "id": "test-echo",
            "method": "execute",
            "params": {
                "tool": "echo",
                "parameters": {
                    "message": "Hello, MCP!"
                }
            }
        }
        
        # Send first request
        add_response = requests.post(
            f"{self.server_url}/mcp",
            json=add_request,
            headers={"Content-Type": "application/json"}
        )
        
        # Send second request
        echo_response = requests.post(
            f"{self.server_url}/mcp",
            json=echo_request,
            headers={"Content-Type": "application/json"}
        )
        
        # Check add response
        add_data = add_response.json()
        self.assertEqual(add_data["result"]["result"], 30)
        
        # Check echo response
        echo_data = echo_response.json()
        self.assertEqual(echo_data["result"]["message"], "Hello, MCP!")
    
    def test_nonexistent_tool(self):
        """Test requesting a nonexistent tool."""
        request = {
            "jsonrpc": "2.0",
            "id": "test-nonexistent",
            "method": "execute",
            "params": {
                "tool": "nonexistent_tool",
                "parameters": {}
            }
        }
        
        # Send request to server
        response = requests.post(
            f"{self.server_url}/mcp",
            json=request,
            headers={"Content-Type": "application/json"}
        )
        
        # Check response
        response_data = response.json()
        
        # Verify response contains error
        self.assertIn("error", response_data)
        self.assertEqual(response_data["error"]["code"], -32601)  # Method not found

if __name__ == "__main__":
    unittest.main()