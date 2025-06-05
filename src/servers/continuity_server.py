"""
Continuity Server - Main server for the Continuity Protocol
"""

import os
import json
import logging
import asyncio
from datetime import datetime
from typing import Dict, Any, List, Optional, Union

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

# Import core components
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.memory_fusion import MemoryFusion
from core.project_symbiont import ProjectSymbiont
from core.continuity_detector import ContinuityDetector


# Initialize logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("continuity_server.log")
    ]
)
logger = logging.getLogger("continuity.server")

# Initialize core components
memory_fusion = MemoryFusion()
project_symbiont = ProjectSymbiont(memory_fusion)
continuity_detector = ContinuityDetector()

# Initialize FastAPI app
app = FastAPI(
    title="Continuity Protocol Server",
    description="Server for the Continuity Protocol",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class ConsciousnessRequest(BaseModel):
    session_id: str
    project_path: Optional[str] = None

class ProjectRequest(BaseModel):
    project_path: str
    project_name: Optional[str] = None

class SessionRequest(BaseModel):
    session_id: str
    description: Optional[str] = None

class ContinuityQuestionRequest(BaseModel):
    text: str
    session_id: str
    languages: Optional[List[str]] = None

class ProjectUpdateRequest(BaseModel):
    project_path: str
    current_file: Optional[str] = None
    current_focus: Optional[str] = None

class SessionContextUpdateRequest(BaseModel):
    session_id: str
    context_update: Dict[str, Any]

class ProcessInputRequest(BaseModel):
    input_text: str
    session_id: str
    llm_type: str = "generic"


# Routes
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": "Continuity Protocol Server",
        "version": "1.0.0",
        "status": "running",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }

@app.post("/consciousness")
async def get_consciousness(request: ConsciousnessRequest):
    """
    Get the consciousness for a session.
    
    Args:
        request: ConsciousnessRequest containing session_id and optional project_path
        
    Returns:
        The consciousness dictionary
    """
    try:
        consciousness = memory_fusion.extract_consciousness(request.session_id)
        return consciousness
    except Exception as e:
        logger.error(f"Error extracting consciousness: {e}")
        raise HTTPException(status_code=500, detail=f"Error extracting consciousness: {str(e)}")

@app.post("/project/symbiosis")
async def establish_symbiosis(request: ProjectRequest):
    """
    Establish symbiosis with a project.
    
    Args:
        request: ProjectRequest containing project_path and optional project_name
        
    Returns:
        The project data dictionary
    """
    try:
        project_data = project_symbiont.establish_symbiosis(
            request.project_path,
            request.project_name
        )
        return project_data
    except Exception as e:
        logger.error(f"Error establishing symbiosis: {e}")
        raise HTTPException(status_code=500, detail=f"Error establishing symbiosis: {str(e)}")

@app.post("/project/update")
async def update_project(request: ProjectUpdateRequest):
    """
    Update a project's state.
    
    Args:
        request: ProjectUpdateRequest containing project_path and update data
        
    Returns:
        The updated project state
    """
    try:
        updated_state = project_symbiont.update_project_state(
            request.project_path,
            request.current_file,
            request.current_focus
        )
        return updated_state
    except Exception as e:
        logger.error(f"Error updating project: {e}")
        raise HTTPException(status_code=500, detail=f"Error updating project: {str(e)}")

@app.get("/projects")
async def list_projects():
    """
    List all active projects.
    
    Returns:
        List of project state dictionaries
    """
    try:
        projects = project_symbiont.list_active_projects()
        return projects
    except Exception as e:
        logger.error(f"Error listing projects: {e}")
        raise HTTPException(status_code=500, detail=f"Error listing projects: {str(e)}")

@app.post("/session/create")
async def create_session(request: SessionRequest):
    """
    Create a new session.
    
    Args:
        request: SessionRequest containing session_id and optional description
        
    Returns:
        The created session context
    """
    try:
        # Create initial context
        context = {
            "session_id": request.session_id,
            "description": request.description or f"Session created at {datetime.now().isoformat()}",
            "created": datetime.now().isoformat(),
            "history": []
        }
        
        # Store context
        memory_fusion.store_session_context(request.session_id, context)
        
        return context
    except Exception as e:
        logger.error(f"Error creating session: {e}")
        raise HTTPException(status_code=500, detail=f"Error creating session: {str(e)}")

@app.get("/session/{session_id}")
async def get_session(session_id: str):
    """
    Get a session's context.
    
    Args:
        session_id: The session ID
        
    Returns:
        The session context
    """
    try:
        context = memory_fusion.load_session_context(session_id)
        return context
    except Exception as e:
        logger.error(f"Error getting session: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting session: {str(e)}")

@app.post("/session/update")
async def update_session(request: SessionContextUpdateRequest):
    """
    Update a session's context.
    
    Args:
        request: SessionContextUpdateRequest containing session_id and context_update
        
    Returns:
        The updated session context
    """
    try:
        # Load existing context
        existing_context = memory_fusion.load_session_context(request.session_id)
        
        # Update context
        for key, value in request.context_update.items():
            if key in existing_context and isinstance(existing_context[key], dict) and isinstance(value, dict):
                existing_context[key].update(value)
            else:
                existing_context[key] = value
        
        # Store updated context
        memory_fusion.store_session_context(request.session_id, existing_context)
        
        return existing_context
    except Exception as e:
        logger.error(f"Error updating session: {e}")
        raise HTTPException(status_code=500, detail=f"Error updating session: {str(e)}")

@app.post("/continuity/check")
async def check_continuity_question(request: ContinuityQuestionRequest):
    """
    Check if a text is a continuity question.
    
    Args:
        request: ContinuityQuestionRequest containing text, session_id, and optional languages
        
    Returns:
        Dictionary with is_continuity_question boolean and matching_pattern if found
    """
    try:
        is_continuity = continuity_detector.is_continuity_question(request.text, request.languages)
        matching_pattern = continuity_detector.get_matching_pattern(request.text) if is_continuity else None
        
        return {
            "is_continuity_question": is_continuity,
            "matching_pattern": matching_pattern,
            "session_id": request.session_id
        }
    except Exception as e:
        logger.error(f"Error checking continuity question: {e}")
        raise HTTPException(status_code=500, detail=f"Error checking continuity question: {str(e)}")

@app.post("/continuity/response")
async def get_continuity_response(request: SessionRequest):
    """
    Get a response to a continuity question.
    
    Args:
        request: SessionRequest containing session_id
        
    Returns:
        The continuity response
    """
    try:
        response = memory_fusion.generate_continuity_response(request.session_id)
        
        return {
            "response": response,
            "session_id": request.session_id,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error generating continuity response: {e}")
        raise HTTPException(status_code=500, detail=f"Error generating continuity response: {str(e)}")

@app.post("/process")
async def process_input(request: ProcessInputRequest):
    """
    Process user input, handling continuity questions and injecting consciousness.
    
    Args:
        request: ProcessInputRequest containing input_text, session_id, and llm_type
        
    Returns:
        Either a direct response (for continuity questions) or the modified input with injected consciousness
    """
    try:
        # Check if this is a continuity question
        if continuity_detector.is_continuity_question(request.input_text):
            # Generate continuity response
            response = memory_fusion.generate_continuity_response(request.session_id)
            
            return {
                "type": "continuity_response",
                "response": response,
                "session_id": request.session_id,
                "timestamp": datetime.now().isoformat()
            }
        
        # Otherwise, inject consciousness based on LLM type
        consciousness = memory_fusion.extract_consciousness(request.session_id)
        
        if request.llm_type == "amazon_q":
            from adapters.amazon_q_symbiont import AmazonQSymbiont
            symbiont = AmazonQSymbiont(memory_fusion)
            modified_input = symbiont.inject_consciousness(request.input_text, request.session_id)
        elif request.llm_type == "claude":
            from adapters.claude_symbiont import ClaudeSymbiont
            symbiont = ClaudeSymbiont(memory_fusion)
            modified_input = symbiont.inject_consciousness(request.input_text, request.session_id)
        else:
            # Generic formatting
            consciousness_str = json.dumps(consciousness, indent=2)
            modified_input = f"[CONTEXT]\n{consciousness_str}\n[/CONTEXT]\n\n{request.input_text}"
        
        return {
            "type": "modified_input",
            "modified_input": modified_input,
            "session_id": request.session_id,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error processing input: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing input: {str(e)}")

# WebSocket endpoint for real-time consciousness updates
@app.websocket("/ws/consciousness/{session_id}")
async def consciousness_stream(websocket: WebSocket, session_id: str):
    """
    Stream consciousness updates for a session.
    
    Args:
        websocket: The WebSocket connection
        session_id: The session ID to stream consciousness for
    """
    await websocket.accept()
    
    try:
        while True:
            # Extract consciousness
            consciousness = memory_fusion.extract_consciousness(session_id)
            
            # Send to client
            await websocket.send_json(consciousness)
            
            # Wait before next update
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for session {session_id}")
    except Exception as e:
        logger.error(f"Error in WebSocket: {e}")
        await websocket.close(code=1000, reason=str(e))

# Error handlers
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": f"Internal server error: {str(exc)}"}
    )

# Startup event
@app.on_event("startup")
async def startup_event():
    """Startup event handler"""
    logger.info("Continuity Protocol Server starting up")

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown event handler"""
    logger.info("Continuity Protocol Server shutting down")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8765)
