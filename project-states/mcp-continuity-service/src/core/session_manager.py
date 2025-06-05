"""
Session Manager - Manages session state and lifecycle
"""

import asyncio
import json
import uuid
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from pathlib import Path
import logging


class SessionManager:
    """
    Manages session lifecycle, state persistence, and cleanup.
    """
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        self.sessions: Dict[str, Dict] = {}
        self.data_dir = Path(self.config.get('data_dir', 'data'))
        self.sessions_dir = self.data_dir / 'sessions'
        self.sessions_dir.mkdir(parents=True, exist_ok=True)
    
    async def create_session(self, session_id: Optional[str] = None) -> str:
        """
        Create a new session.
        
        Args:
            session_id: Optional session ID, generates one if not provided
            
        Returns:
            Session ID
        """
        if not session_id:
            session_id = str(uuid.uuid4())
        
        session_data = {
            'id': session_id,
            'created_at': datetime.now().isoformat(),
            'last_activity': datetime.now().isoformat(),
            'active_projects': [],
            'inputs': [],
            'context': {},
            'metadata': {}
        }
        
        self.sessions[session_id] = session_data
        await self.save_session(session_id)
        
        self.logger.info(f"Created session {session_id}")
        return session_id
    
    async def get_session(self, session_id: str) -> Optional[Dict]:
        """Get session data"""
        if session_id not in self.sessions:
            await self.load_session(session_id)
        
        return self.sessions.get(session_id)
    
    async def save_session(self, session_id: str):
        """Save session to disk"""
        if session_id in self.sessions:
            session_file = self.sessions_dir / f"{session_id}.json"
            with open(session_file, 'w') as f:
                json.dump(self.sessions[session_id], f, indent=2)
    
    async def load_session(self, session_id: str) -> bool:
        """Load session from disk"""
        session_file = self.sessions_dir / f"{session_id}.json"
        
        if session_file.exists():
            try:
                with open(session_file, 'r') as f:
                    self.sessions[session_id] = json.load(f)
                return True
            except Exception as e:
                self.logger.error(f"Error loading session {session_id}: {e}")
        
        return False
    
    async def save_input(self, user_input: str, session_id: str):
        """Save user input to session"""
        session = await self.get_session(session_id)
        if not session:
            await self.create_session(session_id)
            session = self.sessions[session_id]
        
        input_entry = {
            'content': user_input,
            'timestamp': datetime.now().isoformat(),
            'preserved': True
        }
        
        session['inputs'].append(input_entry)
        session['last_activity'] = datetime.now().isoformat()
        
        await self.save_session(session_id)
    
    async def get_active_projects(self, session_id: str) -> List[Dict]:
        """Get active projects for session"""
        session = await self.get_session(session_id)
        return session.get('active_projects', []) if session else []
    
    async def add_project(self, session_id: str, project: Dict):
        """Add project to session"""
        session = await self.get_session(session_id)
        if session:
            session['active_projects'].append(project)
            await self.save_session(session_id)
