"""
MCP Server implementation for Continuity Protocol.

This module provides the core server implementation for the Continuity Protocol,
following the Model Context Protocol (MCP) specification.
"""

from typing import Dict, Any, Callable, Optional, List, Union
import json
import sys
import logging
import inspect
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("continuity-protocol")

class MCPServer:
    """Base MCP Server implementation for Continuity Protocol"""
    
    def __init__(self, name: str = "Continuity-Protocol"):
        """
        Initialize a new MCP server.
        
        Args:
            name: Name of the server instance
        """
        self.name = name
        self.tools: Dict[str, Callable] = {}
        self.descriptions: Dict[str, Dict[str, Any]] = {}
        self.start_time = datetime.now().isoformat()
        logger.info(f"Initializing {self.name} MCP server")
    
    def register_tool(self, name: str, func: Callable, description: Dict[str, Any] = None) -> None:
        """
        Register a new tool with the server.
        
        Args:
            name: Name of the tool
            func: Function implementing the tool
            description: JSON Schema description of the tool (optional)
        """
        self.tools[name] = func
        
        # If no description is provided, generate one from the function's docstring
        if description is None:
            description = self._generate_description_from_function(name, func)
        
        self.descriptions[name] = description
        logger.info(f"Registered tool: {name}")
    
    def _generate_description_from_function(self, name: str, func: Callable) -> Dict[str, Any]:
        """Generate a tool description from a function's signature and docstring"""
        signature = inspect.signature(func)
        docstring = inspect.getdoc(func) or ""
        
        parameters = {}
        required = []
        
        for param_name, param in signature.parameters.items():
            if param.default == inspect.Parameter.empty:
                required.append(param_name)
            
            param_type = "string"  # Default type
            if param.annotation != inspect.Parameter.empty:
                if param.annotation == str:
                    param_type = "string"
                elif param.annotation == int:
                    param_type = "integer"
                elif param.annotation == float:
                    param_type = "number"
                elif param.annotation == bool:
                    param_type = "boolean"
                elif param.annotation == dict or param.annotation == Dict:
                    param_type = "object"
                elif param.annotation == list or param.annotation == List:
                    param_type = "array"
            
            parameters[param_name] = {
                "type": param_type,
                "description": f"Parameter {param_name}"
            }
        
        return {
            "name": name,
            "description": docstring,
            "parameters": {
                "type": "object",
                "properties": parameters,
                "required": required
            },
            "returns": {
                "type": "object",
                "description": "Result of the tool execution"
            }
        }
    
    def register_default_tools(self) -> None:
        """Register the default set of continuity tools"""
        try:
            # Import default tools
            from continuity_protocol.tools.session import session_create, session_save, session_restore
            from continuity_protocol.tools.context import context_store, context_retrieve, context_switch
            from continuity_protocol.tools.system import system_status, memory_optimize
            
            # Register session tools
            self.register_tool("session_create", session_create)
            self.register_tool("session_save", session_save)
            self.register_tool("session_restore", session_restore)
            
            # Register context tools
            self.register_tool("context_store", context_store)
            self.register_tool("context_retrieve", context_retrieve)
            self.register_tool("context_switch", context_switch)
            
            # Register system tools
            self.register_tool("system_status", system_status)
            self.register_tool("memory_optimize", memory_optimize)
            
            logger.info("Registered default continuity tools")
        except ImportError as e:
            logger.warning(f"Could not register all default tools: {e}")
    
    def register_llm_timesheet_tools(self) -> None:
        """Register LLM Timesheet tools"""
        try:
            # Import LLM Timesheet adapter
            from llmops.timesheet_mcp import llm_punch_in, llm_punch_out, llm_sprint_report
            
            # Register LLM Timesheet tools
            self.register_tool("llm_punch_in", llm_punch_in)
            self.register_tool("llm_punch_out", llm_punch_out)
            self.register_tool("llm_sprint_report", llm_sprint_report)
            
            logger.info("Registered LLM Timesheet tools")
        except ImportError as e:
            logger.warning(f"Could not register LLM Timesheet tools: {e}")
    
    def get_tool_descriptions(self) -> List[Dict[str, Any]]:
        """Get descriptions of all registered tools"""
        return list(self.descriptions.values())
    
    def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle a JSON-RPC request
        
        Args:
            request: JSON-RPC request object
            
        Returns:
            JSON-RPC response object
        """
        # Validate JSON-RPC version
        if request.get("jsonrpc") != "2.0":
            logger.error("Invalid JSON-RPC version")
            return {
                "jsonrpc": "2.0",
                "id": request.get("id", None),
                "error": {
                    "code": -32600,
                    "message": "Invalid Request: Not a valid JSON-RPC 2.0 request"
                }
            }
        
        # Validate method
        method = request.get("method")
        if method != "execute":
            logger.error(f"Method not found: {method}")
            return {
                "jsonrpc": "2.0",
                "id": request.get("id", None),
                "error": {
                    "code": -32601,
                    "message": f"Method not found: {method}"
                }
            }
        
        # Extract parameters
        params = request.get("params", {})
        tool_name = params.get("tool")
        tool_params = params.get("parameters", {})
        
        # Check if tool exists
        if tool_name not in self.tools:
            logger.error(f"Tool not found: {tool_name}")
            return {
                "jsonrpc": "2.0",
                "id": request.get("id", None),
                "error": {
                    "code": -32601,
                    "message": f"Tool not found: {tool_name}"
                }
            }
        
        # Execute tool
        try:
            logger.info(f"Executing tool: {tool_name}")
            result = self.tools[tool_name](**tool_params)
            logger.info(f"Tool execution successful: {tool_name}")
            
            return {
                "jsonrpc": "2.0",
                "id": request.get("id", None),
                "result": result
            }
        except Exception as e:
            logger.error(f"Error executing tool {tool_name}: {str(e)}")
            return {
                "jsonrpc": "2.0",
                "id": request.get("id", None),
                "error": {
                    "code": -32603,
                    "message": f"Internal error: {str(e)}"
                }
            }
    
    def run(self, transport: str = "stdio", host: str = "127.0.0.1", port: int = 8000) -> None:
        """
        Run the MCP server with the specified transport
        
        Args:
            transport: Transport mechanism (stdio or http)
            host: Host to bind to (for HTTP transport)
            port: Port to bind to (for HTTP transport)
        """
        logger.info(f"Starting server with {transport} transport")
        
        if transport == "stdio":
            self._run_stdio()
        elif transport == "http":
            self._run_http(host, port)
        else:
            raise ValueError(f"Unsupported transport: {transport}")
    
    def _run_stdio(self) -> None:
        """Run server using stdio transport"""
        logger.info("Running with stdio transport")
        print(f"# {self.name} MCP Server - Running", file=sys.stderr)
        
        while True:
            try:
                # Read a line from stdin
                line = sys.stdin.readline()
                if not line:
                    logger.info("End of input stream, shutting down")
                    break
                
                # Parse and handle the request
                try:
                    request = json.loads(line)
                    response = self.handle_request(request)
                except json.JSONDecodeError:
                    logger.error("Invalid JSON received")
                    response = {
                        "jsonrpc": "2.0",
                        "id": None,
                        "error": {
                            "code": -32700,
                            "message": "Parse error: Invalid JSON"
                        }
                    }
                
                # Write the response to stdout
                sys.stdout.write(json.dumps(response) + "\n")
                sys.stdout.flush()
                
            except Exception as e:
                logger.error(f"Unhandled error: {str(e)}")
                try:
                    sys.stdout.write(json.dumps({
                        "jsonrpc": "2.0",
                        "id": None,
                        "error": {
                            "code": -32603,
                            "message": f"Internal error: {str(e)}"
                        }
                    }) + "\n")
                    sys.stdout.flush()
                except:
                    pass
    
    def _run_http(self, host: str, port: int) -> None:
        """
        Run server using HTTP transport
        
        Args:
            host: Host to bind to
            port: Port to bind to
        """
        try:
            from continuity_protocol.transport import run_http_server
            
            if run_http_server is None:
                logger.error("HTTP transport is not available. Please install fastapi and uvicorn.")
                raise ImportError("HTTP transport is not available")
            
            run_http_server(self, host, port)
        except ImportError as e:
            logger.error(f"HTTP transport not available: {e}")
            raise ImportError(f"HTTP transport not available: {e}")


# Convenience function to create and run a server with default tools
def run_server(name: str = "Continuity-Protocol", transport: str = "stdio", 
               host: str = "127.0.0.1", port: int = 8000,
               register_defaults: bool = True, register_timesheet: bool = True) -> None:
    """
    Create and run an MCP server with default configuration
    
    Args:
        name: Name of the server
        transport: Transport mechanism (stdio or http)
        host: Host to bind to (for HTTP transport)
        port: Port to bind to (for HTTP transport)
        register_defaults: Whether to register default tools
        register_timesheet: Whether to register LLM Timesheet tools
    """
    server = MCPServer(name)
    
    if register_defaults:
        server.register_default_tools()
    
    if register_timesheet:
        server.register_llm_timesheet_tools()
    
    server.run(transport, host, port)


if __name__ == "__main__":
    # Run server with default configuration when executed directly
    import argparse
    
    parser = argparse.ArgumentParser(description="Run Continuity Protocol MCP Server")
    parser.add_argument("--name", default="Continuity-Protocol", help="Server name")
    parser.add_argument("--transport", choices=["stdio", "http"], default="stdio", help="Transport mechanism")
    parser.add_argument("--host", default="127.0.0.1", help="Host to bind to (for HTTP transport)")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind to (for HTTP transport)")
    parser.add_argument("--no-defaults", action="store_true", help="Disable default tools")
    parser.add_argument("--no-timesheet", action="store_true", help="Disable LLM Timesheet tools")
    
    args = parser.parse_args()
    
    run_server(
        name=args.name,
        transport=args.transport,
        host=args.host,
        port=args.port,
        register_defaults=not args.no_defaults,
        register_timesheet=not args.no_timesheet
    )