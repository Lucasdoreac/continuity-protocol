"""
Recovery Engine - Handles automatic recovery and context restoration
"""

import asyncio
import json
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from pathlib import Path
import logging


class RecoveryEngine:
    """
    Handles automatic recovery operations and context restoration.
    """
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        self.data_dir = Path(self.config.get('data_dir', 'data'))
        self.backups_dir = self.data_dir / 'backups'
        self.emergency_dir = self.data_dir / 'emergency'
        
        # Ensure directories exist
        self.backups_dir.mkdir(parents=True, exist_ok=True)
        self.emergency_dir.mkdir(parents=True, exist_ok=True)
    
    async def auto_recover(self, session_id: str) -> Dict[str, Any]:
        """
        Execute automatic recovery for a session.
        
        Args:
            session_id: Session to recover
            
        Returns:
            Recovery result information
        """
        self.logger.info(f"Starting auto-recovery for session {session_id}")
        
        recovery_result = {
            'session_id': session_id,
            'timestamp': datetime.now().isoformat(),
            'actions_taken': [],
            'projects_restored': [],
            'critical_missions': [],
            'success': True
        }
        
        try:
            # Load the latest backup
            backup_data = await self.load_latest_backup(session_id)
            if backup_data:
                recovery_result['actions_taken'].append('Loaded latest backup')
                recovery_result['projects_restored'] = backup_data.get('projects', [])
            
            # Check for critical missions
            critical_missions = await self.detect_critical_missions(session_id)
            recovery_result['critical_missions'] = critical_missions
            
            if critical_missions:
                recovery_result['actions_taken'].append(f'Found {len(critical_missions)} critical missions')
            
            # Restore context
            context = await self.restore_context(session_id, backup_data)
            recovery_result['context'] = context
            recovery_result['actions_taken'].append('Context restored')
            
            self.logger.info(f"Auto-recovery completed for session {session_id}")
            
        except Exception as e:
            self.logger.error(f"Auto-recovery failed for session {session_id}: {e}")
            recovery_result['success'] = False
            recovery_result['error'] = str(e)
        
        return recovery_result
    
    async def load_full_context(self, session_id: str) -> Dict[str, Any]:
        """
        Load complete context for a session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Full context data
        """
        context = {
            'session_id': session_id,
            'timestamp': datetime.now().isoformat(),
            'projects': [],
            'critical_missions': [],
            'recent_activity': [],
            'needs_recovery': False
        }
        
        try:
            # Load session data
            session_file = self.data_dir / 'sessions' / f'{session_id}.json'
            if session_file.exists():
                with open(session_file, 'r') as f:
                    session_data = json.load(f)
                    context['projects'] = session_data.get('active_projects', [])
                    context['recent_activity'] = session_data.get('inputs', [])[-10:]  # Last 10 inputs
            
            # Check for critical missions
            critical_missions = await self.detect_critical_missions(session_id)
            context['critical_missions'] = critical_missions
            context['needs_recovery'] = len(critical_missions) > 0
            
        except Exception as e:
            self.logger.error(f"Error loading context for session {session_id}: {e}")
            context['error'] = str(e)
        
        return context

    async def load_latest_backup(self, session_id: str) -> Optional[Dict]:
        """Load the most recent backup for a session"""
        backup_pattern = f"{session_id}_*.json"
        backup_files = list(self.backups_dir.glob(backup_pattern))
        
        if not backup_files:
            return None
        
        # Sort by modification time, get the latest
        latest_backup = max(backup_files, key=lambda f: f.stat().st_mtime)
        
        try:
            with open(latest_backup, 'r') as f:
                return json.load(f)
        except Exception as e:
            self.logger.error(f"Error loading backup {latest_backup}: {e}")
            return None
    
    async def detect_critical_missions(self, session_id: str) -> List[Dict]:
        """Detect critical missions that need attention"""
        missions = []
        
        # Check for emergency freezes
        emergency_files = list(self.emergency_dir.glob(f"{session_id}_*.json"))
        for emergency_file in emergency_files:
            missions.append({
                'type': 'emergency_freeze',
                'description': f'Emergency freeze found: {emergency_file.name}',
                'file': str(emergency_file),
                'priority': 'critical'
            })
        
        # Check for incomplete operations (placeholder)
        # This would integrate with actual operation tracking
        
        return missions
    
    async def restore_context(self, session_id: str, backup_data: Optional[Dict]) -> Dict:
        """Restore context from backup data"""
        context = {
            'restored_from_backup': backup_data is not None,
            'restoration_time': datetime.now().isoformat()
        }
        
        if backup_data:
            context.update({
                'projects': backup_data.get('projects', []),
                'last_action': backup_data.get('last_action', 'Unknown'),
                'progress': backup_data.get('progress', {})
            })
        
        return context
    
    async def get_critical_missions(self, session_id: str) -> List[Dict]:
        """Get critical missions for a session"""
        return await self.detect_critical_missions(session_id)
    
    async def create_recovery_point(self, session_id: str, data: Dict) -> str:
        """Create a recovery point"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        recovery_file = self.backups_dir / f"{session_id}_{timestamp}.json"
        
        recovery_data = {
            'session_id': session_id,
            'timestamp': datetime.now().isoformat(),
            'data': data
        }
        
        with open(recovery_file, 'w') as f:
            json.dump(recovery_data, f, indent=2)
        
        return str(recovery_file)
