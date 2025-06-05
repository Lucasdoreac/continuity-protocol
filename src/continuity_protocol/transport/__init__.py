"""
Transport modules for Continuity Protocol.

This package provides different transport mechanisms for the Continuity Protocol.
"""

# Import transports
try:
    from .http import HTTPTransport, run_http_server
except ImportError:
    # HTTP transport requires FastAPI and uvicorn
    HTTPTransport = None
    run_http_server = None