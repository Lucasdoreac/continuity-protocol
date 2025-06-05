#!/usr/bin/env python3
"""
HTTP Client for Continuity Protocol MCP Server

This script demonstrates how to interact with the Continuity Protocol MCP server
using the HTTP transport.
"""

import json
import sys
import os
import argparse
import requests
from typing import Dict, Any, List, Optional

def execute_tool(server_url: str, tool: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
    """
    Execute a tool on the MCP server via HTTP.
    
    Args:
        server_url: URL of the server
        tool: Name of the tool to execute
        parameters: Parameters for the tool
        
    Returns:
        Result of the tool execution
    """
    # Create JSON-RPC request
    request = {
        "jsonrpc": "2.0",
        "id": "1",
        "method": "execute",
        "params": {
            "tool": tool,
            "parameters": parameters
        }
    }
    
    # Send request
    print(f"\n>>> Sending request to {server_url}: {json.dumps(request, indent=2)}")
    
    try:
        response = requests.post(server_url, json=request)
        response.raise_for_status()
        
        # Parse response
        result = response.json()
        print(f"<<< Received response: {json.dumps(result, indent=2)}")
        
        return result
    except requests.exceptions.RequestException as e:
        print(f"Error: {str(e)}")
        sys.exit(1)

def list_tools(server_url: str) -> List[Dict[str, Any]]:
    """
    List available tools on the MCP server.
    
    Args:
        server_url: Base URL of the server
        
    Returns:
        List of available tools
    """
    tools_url = f"{server_url.rstrip('/')}/tools"
    
    try:
        response = requests.get(tools_url)
        response.raise_for_status()
        
        result = response.json()
        return result.get("tools", [])
    except requests.exceptions.RequestException as e:
        print(f"Error listing tools: {str(e)}")
        return []

def check_health(server_url: str) -> Dict[str, Any]:
    """
    Check the health of the MCP server.
    
    Args:
        server_url: Base URL of the server
        
    Returns:
        Health status
    """
    health_url = f"{server_url.rstrip('/')}/health"
    
    try:
        response = requests.get(health_url)
        response.raise_for_status()
        
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error checking health: {str(e)}")
        return {"status": "error", "error": str(e)}

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="HTTP Client for Continuity Protocol MCP Server")
    parser.add_argument("--url", default="http://127.0.0.1:8000", help="Server URL")
    
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Health check command
    health_parser = subparsers.add_parser("health", help="Check server health")
    
    # List tools command
    tools_parser = subparsers.add_parser("list-tools", help="List available tools")
    
    # Session commands
    session_parser = subparsers.add_parser("session", help="Session management")
    session_subparsers = session_parser.add_subparsers(dest="session_command", help="Session command")
    
    # Create session
    create_parser = session_subparsers.add_parser("create", help="Create a session")
    create_parser.add_argument("--name", required=True, help="Session name")
    
    # Save session
    save_parser = session_subparsers.add_parser("save", help="Save session state")
    save_parser.add_argument("--session-id", required=True, help="Session ID")
    save_parser.add_argument("--content-file", required=True, help="JSON file with content to save")
    
    # Restore session
    restore_parser = session_subparsers.add_parser("restore", help="Restore session state")
    restore_parser.add_argument("--session-id", required=True, help="Session ID")
    
    # List sessions
    list_parser = session_subparsers.add_parser("list", help="List sessions")
    
    # Delete session
    delete_parser = session_subparsers.add_parser("delete", help="Delete a session")
    delete_parser.add_argument("--session-id", required=True, help="Session ID")
    
    # Context commands
    context_parser = subparsers.add_parser("context", help="Context management")
    context_subparsers = context_parser.add_subparsers(dest="context_command", help="Context command")
    
    # Store context
    store_parser = context_subparsers.add_parser("store", help="Store context")
    store_parser.add_argument("--key", required=True, help="Context key")
    store_parser.add_argument("--value-file", required=True, help="JSON file with value to store")
    store_parser.add_argument("--namespace", help="Context namespace")
    
    # Retrieve context
    retrieve_parser = context_subparsers.add_parser("retrieve", help="Retrieve context")
    retrieve_parser.add_argument("--key", required=True, help="Context key")
    retrieve_parser.add_argument("--namespace", help="Context namespace")
    
    # System commands
    system_parser = subparsers.add_parser("system", help="System management")
    system_subparsers = system_parser.add_subparsers(dest="system_command", help="System command")
    
    # System status
    status_parser = system_subparsers.add_parser("status", help="Get system status")
    status_parser.add_argument("--include-sessions", action="store_true", help="Include sessions in status")
    status_parser.add_argument("--include-metrics", action="store_true", help="Include metrics in status")
    
    args = parser.parse_args()
    
    # Determine the base URL and API endpoint
    base_url = args.url
    execute_url = f"{base_url.rstrip('/')}/execute"
    
    # Execute the command
    if args.command == "health":
        health = check_health(base_url)
        print(f"Server health: {json.dumps(health, indent=2)}")
    
    elif args.command == "list-tools":
        tools = list_tools(base_url)
        print(f"Available tools:")
        for tool in tools:
            print(f"  - {tool['name']}: {tool['description']}")
    
    elif args.command == "session":
        if args.session_command == "create":
            result = execute_tool(execute_url, "session_create", {
                "name": args.name
            })
            if "result" in result:
                print(f"Session created with ID: {result['result']['session_id']}")
        
        elif args.session_command == "save":
            # Load content from file
            with open(args.content_file, 'r') as f:
                content = json.load(f)
            
            result = execute_tool(execute_url, "session_save", {
                "session_id": args.session_id,
                "content": content
            })
            if "result" in result and result["result"]["success"]:
                print(f"Session saved as version {result['result']['version']}")
        
        elif args.session_command == "restore":
            result = execute_tool(execute_url, "session_restore", {
                "session_id": args.session_id
            })
            if "result" in result and result["result"]["success"]:
                print(f"Session restored with content:")
                print(json.dumps(result["result"]["content"], indent=2))
        
        elif args.session_command == "list":
            result = execute_tool(execute_url, "session_list", {})
            if "result" in result and result["result"]["success"]:
                print(f"Available sessions:")
                for session in result["result"]["sessions"]:
                    print(f"  - {session['session_id']}: {session['name']} ({session['versions']} versions)")
        
        elif args.session_command == "delete":
            result = execute_tool(execute_url, "session_delete", {
                "session_id": args.session_id
            })
            if "result" in result and result["result"]["success"]:
                print(f"Session {args.session_id} deleted")
    
    elif args.command == "context":
        if args.context_command == "store":
            # Load value from file
            with open(args.value_file, 'r') as f:
                value = json.load(f)
            
            parameters = {
                "key": args.key,
                "value": value
            }
            if args.namespace:
                parameters["namespace"] = args.namespace
            
            result = execute_tool(execute_url, "context_store", parameters)
            if "result" in result and result["result"]["success"]:
                print(f"Context stored successfully")
        
        elif args.context_command == "retrieve":
            parameters = {"key": args.key}
            if args.namespace:
                parameters["namespace"] = args.namespace
            
            result = execute_tool(execute_url, "context_retrieve", parameters)
            if "result" in result and result["result"]["success"]:
                print(f"Retrieved context:")
                print(json.dumps(result["result"]["value"], indent=2))
    
    elif args.command == "system":
        if args.system_command == "status":
            parameters = {
                "include_sessions": args.include_sessions,
                "include_metrics": args.include_metrics
            }
            
            result = execute_tool(execute_url, "system_status", parameters)
            if "result" in result:
                print(f"System status:")
                print(json.dumps(result["result"], indent=2))
    
    else:
        parser.print_help()

if __name__ == "__main__":
    main()