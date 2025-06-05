"""
MCP Continuity Service - FastAPI Main Application
"""

from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer
from pydantic import BaseModel
from typing import Dict, Any, Optional
import logging
from datetime import datetime

# Import core components
from ..core.continuity_manager import ContinuityManager

# Security setup
oauth2_scheme = HTTPBearer()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="MCP Continuity Service",
    description="Professional continuity service for LLMs with MCP integration",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize continuity manager
continuity_manager = ContinuityManager()

# Pydantic models
class ProcessInputRequest(BaseModel):
    user_input: str
    session_id: str
    metadata: Optional[Dict[str, Any]] = None

class ProcessInputResponse(BaseModel):
    type: str
    content: Optional[str] = None
    context: Optional[Dict[str, Any]] = None
    projects: Optional[list] = None
    critical_missions: Optional[list] = None
    next_actions: Optional[list] = None
    session_id: str
    timestamp: str

# API Routes
@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "MCP Continuity Service",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }

@app.post("/api/process-input", response_model=ProcessInputResponse)
async def process_input(request: ProcessInputRequest):
    """
    Main endpoint for processing user input through the continuity system.
    """
    try:
        result = await continuity_manager.process_user_input(
            user_input=request.user_input,
            session_id=request.session_id
        )
        
        return ProcessInputResponse(**result)
        
    except Exception as e:
        logger.error(f"Error processing input: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/sessions/{session_id}/context")
async def get_session_context(session_id: str):
    """Get context for a specific session"""
    try:
        context = await continuity_manager.recovery_engine.load_full_context(session_id)
        return context
    except Exception as e:
        logger.error(f"Error getting session context: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/sessions/{session_id}/emergency-freeze")
async def emergency_freeze(session_id: str):
    """Create emergency freeze of session state"""
    try:
        freeze_id = await continuity_manager.emergency_freeze(session_id)
        return {"freeze_id": freeze_id, "message": "Emergency freeze created"}
    except Exception as e:
        logger.error(f"Error creating emergency freeze: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/sessions/{session_id}/recovery")
async def trigger_recovery(session_id: str):
    """Manually trigger recovery for a session"""
    try:
        result = await continuity_manager.recovery_engine.auto_recover(session_id)
        return result
    except Exception as e:
        logger.error(f"Error triggering recovery: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Exception handlers
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"message": "Internal server error", "detail": str(exc)}
    )

# Startup event
@app.on_event("startup")
async def startup_event():
    logger.info("MCP Continuity Service starting up...")

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    logger.info("MCP Continuity Service shutting down...")

def run_server():
    """Function to run the server programmatically"""
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)

if __name__ == "__main__":
    run_server()

# Import and include authentication routes
try:
    from .routes.auth import router as auth_router
    from .routes.billing import router as billing_router
    
    app.include_router(auth_router)
    app.include_router(billing_router)
    logger.info("Authentication and billing routes loaded successfully")
except ImportError as e:
    logger.warning(f"Could not load auth/billing routes: {e}")

# Add authentication dependency function
async def get_current_user(token: str = Depends(oauth2_scheme)):
    """Get current authenticated user"""
    from .routes.auth import users_db
    from jose import jwt, JWTError
    
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = users_db.get(email)
    if user is None:
        raise credentials_exception
    
    return user

# Update process_input to include authentication
@app.post("/api/process-input", response_model=ProcessInputResponse)
async def process_input(request: ProcessInputRequest, current_user = Depends(get_current_user)):
    """
    Main endpoint for processing user input through the continuity system.
    Now requires authentication.
    """
    try:
        # Check subscription limits
        if current_user["subscription_plan"] != "enterprise":
            if current_user["sessions_used"] >= current_user["sessions_limit"]:
                raise HTTPException(
                    status_code=403, 
                    detail="Session limit reached. Please upgrade your subscription."
                )
        
        result = await continuity_manager.process_user_input(
            user_input=request.user_input,
            session_id=request.session_id,
            user_id=current_user["id"]
        )
        
        # Increment session usage
        current_user["sessions_used"] += 1
        # Save updated user data (implement save_user function)
        
        return ProcessInputResponse(**result)
        
    except Exception as e:
        logger.error(f"Error processing input: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Add test endpoint for bash scripts (no authentication)
@app.post("/api/test-bash")
async def test_bash_scripts(request: ProcessInputRequest):
    """
    Test endpoint that directly calls bash scripts (bypass authentication)
    """
    try:
        # Import here to avoid circular imports
        import sys
        import os
        sys.path.append(os.path.dirname(os.path.dirname(__file__)))
        from services.bash_scripts_service import BashScriptsService
        
        bash_service = BashScriptsService()
        
        # Check if it's a continuity question
        user_input_lower = request.user_input.lower()
        if "onde paramos" in user_input_lower or "where" in user_input_lower:
            result = await bash_service.recovery_where_stopped()
        else:
            result = await bash_service.process_continuity_request(request.user_input)
        
        return {
            "type": "bash_test",
            "method": "direct_bash",
            "success": result["success"],
            "content": result["output"] if result["success"] else result["error"],
            "session_id": request.session_id,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Bash test error: {e}")
        return {
            "type": "bash_test",
            "method": "direct_bash", 
            "success": False,
            "content": f"Error: {str(e)}",
            "session_id": request.session_id,
            "timestamp": datetime.now().isoformat()
        }
