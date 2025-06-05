"""
Context Detector - Detects continuity questions and recovery needs
"""

import re
import asyncio
from typing import List, Dict, Tuple, Optional
from datetime import datetime, timedelta
import logging
from pathlib import Path


class ContextDetector:
    """
    Detects continuity questions and determines when recovery is needed.
    """
    
    CONTINUITY_PATTERNS = [
        r"onde paramos\??",
        r"o que estava(mos)? fazendo\??",
        r"continue de onde parou",
        r"qual (o )?status do projeto\??",
        r"preciso recuperar o contexto",
        r"what were we doing\??",
        r"where did we leave off\??",
        r"continue from where we stopped",
        r"resume session",
        r"load previous context"
    ]
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        self.session_timeout = timedelta(hours=1)  # Default timeout
        
    async def is_continuity_question(self, text: str) -> bool:
        """
        Detect if the input is a continuity question.
        
        Args:
            text: User input text
            
        Returns:
            True if it's a continuity question
        """
        if not text:
            return False
            
        text_lower = text.lower().strip()
        
        # Check exact matches first
        exact_matches = [
            "onde paramos?",
            "onde paramos",
            "what were we doing?",
            "where did we leave off?",
            "continue",
            "resume"
        ]
        
        if text_lower in exact_matches:
            return True
        
        # Check pattern matches
        for pattern in self.CONTINUITY_PATTERNS:
            if re.search(pattern, text_lower):
                return True
        
        return False
    
    async def needs_recovery(self, session_id: str) -> bool:
        """
        Determine if a session needs recovery.
        
        Args:
            session_id: Session identifier
            
        Returns:
            True if recovery is needed
        """
        try:
            # Check for orphaned files
            orphaned_files = await self.detect_orphaned_files(session_id)
            if orphaned_files:
                self.logger.info(f"Found {len(orphaned_files)} orphaned files")
                return True
            
            # Check for stale states
            stale_states = await self.detect_stale_states(session_id)
            if stale_states:
                self.logger.info(f"Found {len(stale_states)} stale states")
                return True
            
            # Check for critical missions
            critical_missions = await self.detect_critical_missions(session_id)
            if critical_missions:
                self.logger.info(f"Found {len(critical_missions)} critical missions")
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error checking recovery needs: {e}")
            return False
    
    async def detect_orphaned_files(self, session_id: str) -> List[str]:
        """Detect files that were created but not tracked"""
        # This would integrate with the file system monitoring
        # For now, return empty list as placeholder
        return []
    
    async def detect_stale_states(self, session_id: str) -> List[str]:
        """Detect states that are older than threshold"""
        stale_states = []
        
        # Check state files age
        state_dir = Path(f"data/states/{session_id}")
        if state_dir.exists():
            for state_file in state_dir.glob("*.json"):
                modified_time = datetime.fromtimestamp(state_file.stat().st_mtime)
                if datetime.now() - modified_time > self.session_timeout:
                    stale_states.append(str(state_file))
        
        return stale_states
    
    async def detect_critical_missions(self, session_id: str) -> List[Dict]:
        """Detect critical missions that need attention"""
        # This would check for interrupted operations
        # For now, return empty list as placeholder
        return []
