#!/usr/bin/env python3
"""
Continuity Protocol MCP Server - Main Entry Point

This script launches the Continuity Protocol MCP server with the specified
configuration and tools.
"""

import os
import sys
import argparse
import logging
from typing import Dict, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
            "logs", 
            "continuity_server.log"
        ))
    ]
)
logger = logging.getLogger("continuity-server")

# Ensure the logs directory exists
os.makedirs(os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
    "logs"
), exist_ok=True)

# Import the MCP server
from continuity_protocol.server import MCPServer, run_server

def parse_args() -> Dict[str, Any]:
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description="Continuity Protocol MCP Server")
    
    parser.add_argument(
        "--name", 
        type=str, 
        default="Continuity-Protocol",
        help="Name of the server"
    )
    
    parser.add_argument(
        "--transport",
        type=str,
        choices=["stdio", "http"],
        default="stdio",
        help="Transport mechanism to use"
    )
    
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port for HTTP transport"
    )
    
    parser.add_argument(
        "--no-default-tools",
        action="store_true",
        help="Disable registration of default continuity tools"
    )
    
    parser.add_argument(
        "--no-timesheet",
        action="store_true",
        help="Disable LLM Timesheet tools"
    )
    
    parser.add_argument(
        "--log-level",
        type=str,
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        default="INFO",
        help="Logging level"
    )
    
    return vars(parser.parse_args())

def main() -> None:
    """Main entry point"""
    args = parse_args()
    
    # Set log level
    logging.getLogger().setLevel(getattr(logging, args["log_level"]))
    
    logger.info(f"Starting Continuity Protocol MCP Server: {args['name']}")
    logger.info(f"Transport: {args['transport']}")
    
    # Run server
    run_server(
        name=args["name"],
        transport=args["transport"],
        register_defaults=not args["no_default_tools"],
        register_timesheet=not args["no_timesheet"]
    )

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
        sys.exit(0)
    except Exception as e:
        logger.critical(f"Unhandled exception: {str(e)}", exc_info=True)
        sys.exit(1)