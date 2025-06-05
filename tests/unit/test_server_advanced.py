"""
Advanced unit tests for the MCP server.

These tests focus on edge cases, error handling, and more complex scenarios.
"""

import unittest
from unittest.mock import patch, MagicMock, call
import json
import sys
import os
import tempfile
import threading
import time
from typing import Dict, Any, List, Optional, Union
import uuid

# Add src directory to path for imports
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__)))), "src"))

try:
    from continuity_protocol.server import MCPServer
except ImportError:
    from src.continuity_protocol.server import MCPServer

class TestMCPServerAdvanced(unittest.TestCase):
    """Advanced test cases for the MCPServer class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.server = MCPServer("Advanced-Test-Server")
        
        # Define and register various test tools
        def simple_tool(arg1: str) -> Dict[str, Any]:
            """A simple tool that returns the input argument."""
            return {"result": arg1}
        
        def complex_tool(arg1: str, arg2: int = 42, arg3: List[str] = None) -> Dict[str, Any]:
            """A more complex tool with default and optional arguments."""
            if arg3 is None:
                arg3 = []
            return {
                "result": {
                    "arg1": arg1,
                    "arg2": arg2,
                    "arg3": arg3
                }
            }
        
        def failing_tool(should_fail: bool = True) -> Dict[str, Any]:
            """A tool that can be configured to fail."""
            if should_fail:
                raise ValueError("Tool was configured to fail")
            return {"result": "success"}
        
        def slow_tool(sleep_seconds: int = 1) -> Dict[str, Any]:
            """A tool that simulates a slow operation."""
            time.sleep(sleep_seconds)
            return {"result": f"Completed after {sleep_seconds} seconds"}
        
        # Register the tools
        self.server.register_tool("simple_tool", simple_tool)
        self.server.register_tool("complex_tool", complex_tool)
        self.server.register_tool("failing_tool", failing_tool)
        self.server.register_tool("slow_tool", slow_tool)
    
    def test_concurrent_requests(self):
        """Test handling multiple concurrent requests."""
        # Create request objects
        request1 = {
            "jsonrpc": "2.0",
            "id": "test-1",
            "method": "execute",
            "params": {
                "tool": "simple_tool",
                "parameters": {"arg1": "request1"}
            }
        }
        
        request2 = {
            "jsonrpc": "2.0",
            "id": "test-2",
            "method": "execute",
            "params": {
                "tool": "simple_tool",
                "parameters": {"arg1": "request2"}
            }
        }
        
        # Function to handle a request and store the result
        def handle_request(request, results, index):
            results[index] = self.server.handle_request(request)
        
        # Create threads for concurrent execution
        results = [None, None]
        thread1 = threading.Thread(
            target=handle_request,
            args=(request1, results, 0)
        )
        thread2 = threading.Thread(
            target=handle_request,
            args=(request2, results, 1)
        )
        
        # Start and join threads
        thread1.start()
        thread2.start()
        thread1.join()
        thread2.join()
        
        # Verify results
        self.assertEqual(results[0]["result"]["result"], "request1")
        self.assertEqual(results[1]["result"]["result"], "request2")
    
    def test_complex_parameters(self):
        """Test handling complex parameter structures."""
        # Create a request with complex nested parameters
        request = {
            "jsonrpc": "2.0",
            "id": "test-complex",
            "method": "execute",
            "params": {
                "tool": "complex_tool",
                "parameters": {
                    "arg1": "test",
                    "arg2": 123,
                    "arg3": ["item1", "item2", "item3"]
                }
            }
        }
        
        # Handle the request
        response = self.server.handle_request(request)
        
        # Verify response
        self.assertEqual(response["jsonrpc"], "2.0")
        self.assertEqual(response["id"], "test-complex")
        self.assertEqual(response["result"]["result"]["arg1"], "test")
        self.assertEqual(response["result"]["result"]["arg2"], 123)
        self.assertEqual(response["result"]["result"]["arg3"], ["item1", "item2", "item3"])
    
    def test_tool_timeout(self):
        """Test handling tool timeouts."""
        # Create a request for the slow tool
        request = {
            "jsonrpc": "2.0",
            "id": "test-timeout",
            "method": "execute",
            "params": {
                "tool": "slow_tool",
                "parameters": {"sleep_seconds": 2}
            }
        }
        
        # Mock time.time to simulate timeout
        original_time = time.time
        mock_times = [100.0, 100.0, 103.0]  # Start, tool call start, tool call end
        
        with patch('time.time', side_effect=mock_times):
            with patch('continuity_protocol.server.TOOL_TIMEOUT', 1):
                # Handle the request (should timeout)
                response = self.server.handle_request(request)
        
        # Verify timeout error
        self.assertIn("error", response)
        self.assertEqual(response["error"]["code"], -32603)
        self.assertIn("timeout", response["error"]["message"].lower())
    
    def test_batch_requests(self):
        """Test handling a batch of requests."""
        # Create a batch request (array of individual requests)
        batch_request = [
            {
                "jsonrpc": "2.0",
                "id": "batch-1",
                "method": "execute",
                "params": {
                    "tool": "simple_tool",
                    "parameters": {"arg1": "batch-item-1"}
                }
            },
            {
                "jsonrpc": "2.0",
                "id": "batch-2",
                "method": "execute",
                "params": {
                    "tool": "simple_tool",
                    "parameters": {"arg1": "batch-item-2"}
                }
            }
        ]
        
        # Handle each request in the batch
        batch_response = [self.server.handle_request(req) for req in batch_request]
        
        # Verify responses
        self.assertEqual(len(batch_response), 2)
        self.assertEqual(batch_response[0]["id"], "batch-1")
        self.assertEqual(batch_response[0]["result"]["result"], "batch-item-1")
        self.assertEqual(batch_response[1]["id"], "batch-2")
        self.assertEqual(batch_response[1]["result"]["result"], "batch-item-2")
    
    def test_schema_validation(self):
        """Test parameter validation against JSON schema."""
        # Register a tool with a strict schema
        def validated_tool(value: str, options: Dict[str, Any]) -> Dict[str, Any]:
            """A tool with strict schema validation."""
            return {"result": f"Processed {value} with {len(options)} options"}
        
        self.server.register_tool("validated_tool", validated_tool, {
            "description": "Tool with strict schema validation",
            "parameters": {
                "type": "object",
                "properties": {
                    "value": {"type": "string", "minLength": 3},
                    "options": {
                        "type": "object",
                        "properties": {
                            "color": {"type": "string", "enum": ["red", "green", "blue"]},
                            "size": {"type": "integer", "minimum": 1, "maximum": 100}
                        },
                        "required": ["color"]
                    }
                },
                "required": ["value", "options"],
                "additionalProperties": False
            }
        })
        
        # Valid request
        valid_request = {
            "jsonrpc": "2.0",
            "id": "valid-schema",
            "method": "execute",
            "params": {
                "tool": "validated_tool",
                "parameters": {
                    "value": "test",
                    "options": {
                        "color": "blue",
                        "size": 50
                    }
                }
            }
        }
        
        # Invalid requests
        invalid_requests = [
            # value too short
            {
                "jsonrpc": "2.0",
                "id": "invalid-1",
                "method": "execute",
                "params": {
                    "tool": "validated_tool",
                    "parameters": {
                        "value": "ab",  # too short
                        "options": {"color": "red"}
                    }
                }
            },
            # Invalid color
            {
                "jsonrpc": "2.0",
                "id": "invalid-2",
                "method": "execute",
                "params": {
                    "tool": "validated_tool",
                    "parameters": {
                        "value": "test",
                        "options": {"color": "yellow"}  # not in enum
                    }
                }
            },
            # Missing required property
            {
                "jsonrpc": "2.0",
                "id": "invalid-3",
                "method": "execute",
                "params": {
                    "tool": "validated_tool",
                    "parameters": {
                        "value": "test",
                        "options": {"size": 50}  # missing required color
                    }
                }
            },
            # Additional property
            {
                "jsonrpc": "2.0",
                "id": "invalid-4",
                "method": "execute",
                "params": {
                    "tool": "validated_tool",
                    "parameters": {
                        "value": "test",
                        "options": {"color": "red"},
                        "extra": "not allowed"  # additional property
                    }
                }
            }
        ]
        
        # Process valid request
        valid_response = self.server.handle_request(valid_request)
        
        # Verify valid response
        self.assertNotIn("error", valid_response)
        self.assertIn("result", valid_response)
        
        # Process invalid requests
        for req in invalid_requests:
            response = self.server.handle_request(req)
            
            # Verify error response
            self.assertIn("error", response, f"Request {req['id']} should fail")
            self.assertEqual(response["error"]["code"], -32602)  # Invalid params
    
    def test_custom_error_handling(self):
        """Test custom error handling in tools."""
        # Define a tool with custom error handling
        def custom_error_tool(error_type: str) -> Dict[str, Any]:
            """A tool that raises different types of errors based on input."""
            if error_type == "value":
                raise ValueError("Value error message")
            elif error_type == "type":
                raise TypeError("Type error message")
            elif error_type == "key":
                raise KeyError("key_not_found")
            elif error_type == "custom":
                class CustomError(Exception):
                    """Custom error class for testing."""
                    pass
                raise CustomError("Custom error message")
            else:
                return {"result": "No error"}
        
        self.server.register_tool("custom_error_tool", custom_error_tool)
        
        # Create requests for different error types
        error_types = ["value", "type", "key", "custom", "none"]
        requests = [
            {
                "jsonrpc": "2.0",
                "id": f"error-{error_type}",
                "method": "execute",
                "params": {
                    "tool": "custom_error_tool",
                    "parameters": {"error_type": error_type}
                }
            }
            for error_type in error_types
        ]
        
        # Process requests
        responses = [self.server.handle_request(req) for req in requests]
        
        # Verify error responses
        for i, error_type in enumerate(error_types[:-1]):  # All except "none"
            response = responses[i]
            self.assertIn("error", response, f"Expected error for {error_type}")
            self.assertEqual(response["error"]["code"], -32603)  # Internal error
            
            # Error message should contain the original error message
            if error_type == "value":
                self.assertIn("Value error message", response["error"]["message"])
            elif error_type == "type":
                self.assertIn("Type error message", response["error"]["message"])
            elif error_type == "key":
                self.assertIn("key_not_found", response["error"]["message"])
            elif error_type == "custom":
                self.assertIn("Custom error message", response["error"]["message"])
        
        # Verify success response
        self.assertIn("result", responses[-1])
        self.assertEqual(responses[-1]["result"]["result"], "No error")
    
    def test_tool_registration_edge_cases(self):
        """Test edge cases in tool registration."""
        # Test registering a tool with no parameters
        def no_params_tool() -> Dict[str, Any]:
            """Tool that takes no parameters."""
            return {"result": "success"}
        
        self.server.register_tool("no_params_tool", no_params_tool)
        
        # Test a tool with *args and **kwargs
        def flexible_tool(*args, **kwargs) -> Dict[str, Any]:
            """Tool with flexible arguments."""
            return {
                "args": args,
                "kwargs": kwargs
            }
        
        self.server.register_tool("flexible_tool", flexible_tool)
        
        # Test these tools
        no_params_request = {
            "jsonrpc": "2.0",
            "id": "no-params",
            "method": "execute",
            "params": {
                "tool": "no_params_tool",
                "parameters": {}
            }
        }
        
        flexible_request = {
            "jsonrpc": "2.0",
            "id": "flexible",
            "method": "execute",
            "params": {
                "tool": "flexible_tool",
                "parameters": {
                    "a": 1,
                    "b": "test",
                    "c": [1, 2, 3]
                }
            }
        }
        
        # Process requests
        no_params_response = self.server.handle_request(no_params_request)
        flexible_response = self.server.handle_request(flexible_request)
        
        # Verify responses
        self.assertIn("result", no_params_response)
        self.assertEqual(no_params_response["result"]["result"], "success")
        
        self.assertIn("result", flexible_response)
        self.assertEqual(flexible_response["result"]["kwargs"]["a"], 1)
        self.assertEqual(flexible_response["result"]["kwargs"]["b"], "test")
        self.assertEqual(flexible_response["result"]["kwargs"]["c"], [1, 2, 3])
    
    def test_dynamic_tool_registration(self):
        """Test dynamic tool registration and unregistration."""
        # Define a dynamic tool creator
        def create_dynamic_tool(name: str, return_value: Any) -> callable:
            """Create a dynamic tool function with the given name."""
            def dynamic_tool() -> Dict[str, Any]:
                """Dynamically created tool."""
                return {"result": return_value}
            
            # Set function name and docstring
            dynamic_tool.__name__ = name
            dynamic_tool.__doc__ = f"Dynamic tool named {name}"
            
            return dynamic_tool
        
        # Create and register a dynamic tool
        dynamic_tool_1 = create_dynamic_tool("dynamic_1", "value_1")
        self.server.register_tool("dynamic_tool_1", dynamic_tool_1)
        
        # Verify tool is registered
        self.assertIn("dynamic_tool_1", self.server.tools)
        
        # Test the dynamic tool
        request = {
            "jsonrpc": "2.0",
            "id": "dynamic-1",
            "method": "execute",
            "params": {
                "tool": "dynamic_tool_1",
                "parameters": {}
            }
        }
        
        response = self.server.handle_request(request)
        self.assertEqual(response["result"]["result"], "value_1")
        
        # Unregister the tool
        self.server.unregister_tool("dynamic_tool_1")
        
        # Verify tool is unregistered
        self.assertNotIn("dynamic_tool_1", self.server.tools)
        
        # Try to use the unregistered tool
        request["id"] = "dynamic-1-after-unregister"
        response = self.server.handle_request(request)
        
        # Verify error response
        self.assertIn("error", response)
        self.assertEqual(response["error"]["code"], -32601)  # Method not found
    
    def test_tool_execution_tracking(self):
        """Test tracking of tool execution statistics."""
        # Enable tracking
        self.server.enable_tracking()
        
        # Create and execute some requests
        tools_to_test = ["simple_tool", "complex_tool", "failing_tool"]
        
        for tool in tools_to_test:
            request = {
                "jsonrpc": "2.0",
                "id": f"track-{tool}",
                "method": "execute",
                "params": {
                    "tool": tool,
                    "parameters": {"arg1": "test"} if tool != "failing_tool" else {"should_fail": True}
                }
            }
            
            # Execute the request (failing_tool will raise an exception)
            self.server.handle_request(request)
        
        # Get tracking statistics
        stats = self.server.get_tracking_stats()
        
        # Verify tracking data exists for all tools
        for tool in tools_to_test:
            self.assertIn(tool, stats)
            self.assertIn("calls", stats[tool])
            self.assertIn("errors", stats[tool])
            self.assertIn("total_time", stats[tool])
            self.assertIn("avg_time", stats[tool])
        
        # Verify error count for failing_tool
        self.assertEqual(stats["failing_tool"]["errors"], 1)
        
        # Verify call counts
        for tool in tools_to_test:
            self.assertEqual(stats[tool]["calls"], 1)
        
        # Reset tracking
        self.server.reset_tracking()
        
        # Verify stats are reset
        empty_stats = self.server.get_tracking_stats()
        for tool in tools_to_test:
            self.assertIn(tool, empty_stats)
            self.assertEqual(empty_stats[tool]["calls"], 0)
            self.assertEqual(empty_stats[tool]["errors"], 0)
    
    def test_request_validation(self):
        """Test validation of incoming requests."""
        # Collection of invalid requests
        invalid_requests = [
            # Missing jsonrpc version
            {
                "id": "invalid-1",
                "method": "execute",
                "params": {"tool": "simple_tool", "parameters": {}}
            },
            # Invalid jsonrpc version
            {
                "jsonrpc": "1.0",
                "id": "invalid-2",
                "method": "execute",
                "params": {"tool": "simple_tool", "parameters": {}}
            },
            # Missing id
            {
                "jsonrpc": "2.0",
                "method": "execute",
                "params": {"tool": "simple_tool", "parameters": {}}
            },
            # Missing method
            {
                "jsonrpc": "2.0",
                "id": "invalid-4",
                "params": {"tool": "simple_tool", "parameters": {}}
            },
            # Invalid method
            {
                "jsonrpc": "2.0",
                "id": "invalid-5",
                "method": "invalid_method",
                "params": {"tool": "simple_tool", "parameters": {}}
            },
            # Missing params
            {
                "jsonrpc": "2.0",
                "id": "invalid-6",
                "method": "execute"
            },
            # Missing tool in params
            {
                "jsonrpc": "2.0",
                "id": "invalid-7",
                "method": "execute",
                "params": {"parameters": {}}
            },
            # Missing parameters in params
            {
                "jsonrpc": "2.0",
                "id": "invalid-8",
                "method": "execute",
                "params": {"tool": "simple_tool"}
            },
            # Non-object parameters
            {
                "jsonrpc": "2.0",
                "id": "invalid-9",
                "method": "execute",
                "params": {"tool": "simple_tool", "parameters": "not_an_object"}
            }
        ]
        
        # Process each invalid request
        for i, request in enumerate(invalid_requests):
            response = self.server.handle_request(request)
            
            # Verify error response
            self.assertIn("error", response, f"Request #{i} should fail: {request}")
            self.assertIn("code", response["error"])
            self.assertIn("message", response["error"])
            
            # Check id is preserved or null if missing
            if "id" in request:
                self.assertEqual(response["id"], request["id"])
            else:
                self.assertIsNone(response["id"])

if __name__ == "__main__":
    unittest.main()