#!/usr/bin/env python3
"""
Simple Client for Continuity Protocol MCP Server

This script demonstrates how to interact with the Continuity Protocol MCP server
using the JSON-RPC 2.0 protocol.
"""

import json
import uuid
import subprocess
import sys
import os
from typing import Dict, Any, List, Optional

def execute_tool(server_process, tool: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
    """
    Execute a tool on the MCP server.
    
    Args:
        server_process: Subprocess object for the server
        tool: Name of the tool to execute
        parameters: Parameters for the tool
        
    Returns:
        Result of the tool execution
    """
    # Create JSON-RPC request
    request = {
        "jsonrpc": "2.0",
        "id": str(uuid.uuid4()),
        "method": "execute",
        "params": {
            "tool": tool,
            "parameters": parameters
        }
    }
    
    # Send request to server
    request_json = json.dumps(request)
    print(f"\n>>> Sending request: {request_json}")
    
    server_process.stdin.write(request_json + "\n")
    server_process.stdin.flush()
    
    # Read response from server
    response_json = server_process.stdout.readline().strip()
    print(f"<<< Received response: {response_json}")
    
    # Parse response
    response = json.loads(response_json)
    
    # Check for errors
    if "error" in response:
        print(f"Error: {response['error']['message']}")
    
    return response

def main():
    """Main function"""
    # Start server process
    server_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
        "start-server.sh"
    )
    
    print(f"Starting server: {server_path}")
    
    server_process = subprocess.Popen(
        [server_path, "--name", "Example-Server"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True,
        bufsize=1  # Line buffered
    )
    
    try:
        # Wait for server to start
        for line in server_process.stderr:
            print(line.strip())
            if "Starting server..." in line:
                break
        
        print("\n=== Continuity Protocol Client Demo ===\n")
        
        # Example 1: Create a session
        print("Example 1: Creating a session")
        response = execute_tool(server_process, "session_create", {
            "name": "Example Session",
            "metadata": {
                "description": "A demo session for the Continuity Protocol",
                "created_by": "Simple Client Example"
            }
        })
        
        if "result" in response:
            session_id = response["result"]["session_id"]
            print(f"Session created with ID: {session_id}")
        else:
            print("Failed to create session")
            return
        
        # Example 2: Store context
        print("\nExample 2: Storing context")
        response = execute_tool(server_process, "context_store", {
            "key": "user_preferences",
            "value": {
                "theme": "dark",
                "language": "en",
                "notifications": True
            },
            "namespace": "example"
        })
        
        if "result" in response and response["result"]["success"]:
            print("Context stored successfully")
        else:
            print("Failed to store context")
        
        # Example 3: Save session state
        print("\nExample 3: Saving session state")
        response = execute_tool(server_process, "session_save", {
            "session_id": session_id,
            "content": {
                "conversation": [
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": "Hello, how are you?"},
                    {"role": "assistant", "content": "I'm doing well, thank you for asking! How can I help you today?"}
                ],
                "state": {
                    "current_topic": "greeting",
                    "sentiment": "positive"
                }
            }
        })
        
        if "result" in response and response["result"]["success"]:
            version = response["result"]["version"]
            print(f"Session saved successfully as version {version}")
        else:
            print("Failed to save session")
        
        # Example 4: Retrieve context
        print("\nExample 4: Retrieving context")
        response = execute_tool(server_process, "context_retrieve", {
            "key": "user_preferences",
            "namespace": "example"
        })
        
        if "result" in response and response["result"]["success"]:
            value = response["result"]["value"]
            print(f"Context retrieved: {json.dumps(value, indent=2)}")
        else:
            print("Failed to retrieve context")
        
        # Example 5: Restore session
        print("\nExample 5: Restoring session")
        response = execute_tool(server_process, "session_restore", {
            "session_id": session_id
        })
        
        if "result" in response and response["result"]["success"]:
            content = response["result"]["content"]
            print(f"Session restored with content: {json.dumps(content, indent=2)}")
        else:
            print("Failed to restore session")
        
        # Example 6: Get system status
        print("\nExample 6: Getting system status")
        response = execute_tool(server_process, "system_status", {
            "include_sessions": True,
            "include_metrics": True
        })
        
        if "result" in response:
            status = response["result"]
            print(f"System status: {status['status']}")
            print(f"Version: {status['version']}")
            print(f"Uptime: {status['uptime_seconds']} seconds")
            
            if "metrics" in status:
                print(f"CPU: {status['metrics']['cpu_percent']}%")
                print(f"Memory: {status['metrics']['memory_percent']}%")
        else:
            print("Failed to get system status")
        
        print("\n=== Demo completed successfully ===")
        
    except KeyboardInterrupt:
        print("\nDemo interrupted by user")
    finally:
        # Terminate server process
        print("\nTerminating server...")
        server_process.terminate()
        try:
            server_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            server_process.kill()

if __name__ == "__main__":
    main()