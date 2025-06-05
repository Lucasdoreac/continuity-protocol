"""
HTTP transport for Continuity Protocol.

This module implements an HTTP server for the Continuity Protocol.
"""

import json
import logging
from typing import Dict, Any, Optional
import uvicorn
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

# Configure logging
logger = logging.getLogger("continuity-protocol.transport.http")

class HTTPTransport:
    """HTTP transport implementation for MCP server"""
    
    def __init__(self, mcp_server, host: str = "127.0.0.1", port: int = 8000):
        """
        Initialize HTTP transport
        
        Args:
            mcp_server: MCP server instance
            host: Host to bind to
            port: Port to bind to
        """
        self.mcp_server = mcp_server
        self.host = host
        self.port = port
        self.app = FastAPI(title=f"{self.mcp_server.name} API", version="0.1.0")
        
        # Configure CORS
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # Register routes
        self._register_routes()
    
    def _register_routes(self):
        """Register API routes"""
        
        @self.app.post("/execute")
        async def execute(request: Request):
            """Execute an MCP tool"""
            try:
                # Parse JSON request
                request_data = await request.json()
                
                # Handle request
                response = self.mcp_server.handle_request(request_data)
                
                return JSONResponse(content=response)
            except json.JSONDecodeError:
                logger.error("Invalid JSON in request")
                return JSONResponse(
                    status_code=400,
                    content={
                        "jsonrpc": "2.0",
                        "id": None,
                        "error": {
                            "code": -32700,
                            "message": "Parse error: Invalid JSON"
                        }
                    }
                )
            except Exception as e:
                logger.error(f"Error handling request: {str(e)}")
                return JSONResponse(
                    status_code=500,
                    content={
                        "jsonrpc": "2.0",
                        "id": None,
                        "error": {
                            "code": -32603,
                            "message": f"Internal error: {str(e)}"
                        }
                    }
                )
        
        @self.app.get("/tools")
        async def list_tools():
            """List available tools"""
            return {
                "tools": self.mcp_server.get_tool_descriptions()
            }
        
        @self.app.get("/health")
        async def health_check():
            """Health check endpoint"""
            return {
                "status": "healthy",
                "server": self.mcp_server.name,
                "version": "0.1.0"
            }
    
    def run(self):
        """Run the HTTP server"""
        logger.info(f"Starting HTTP server on {self.host}:{self.port}")
        uvicorn.run(self.app, host=self.host, port=self.port)

def run_http_server(mcp_server, host: str = "127.0.0.1", port: int = 8000):
    """
    Run an HTTP server for the given MCP server
    
    Args:
        mcp_server: MCP server instance
        host: Host to bind to
        port: Port to bind to
    """
    transport = HTTPTransport(mcp_server, host, port)
    transport.run()