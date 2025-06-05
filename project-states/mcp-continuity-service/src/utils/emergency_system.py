"""
Emergency System - Handles emergency backup and recovery operations
"""

import asyncio
import json
import shutil
from typing import Dict, List, Optional, Any
from datetime import datetime
from pathlib import Path
import logging
import uuid


class EmergencySystem:
    """
    Handles emergency backup and recovery operations to prevent data loss.
    """
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        self.data_dir = Path(self.config.get('data_dir', 'data'))
        self.emergency_dir = self.data_dir / 'emergency'
        self.emergency_dir.mkdir(parents=True, exist_ok=True)
    
    async def freeze(self, session_id: str) -> str:
        """
        Create an emergency freeze of the current state.
        
        Args:
            session_id: Session to freeze
            
        Returns:
            Freeze ID for later recovery
        """
        freeze_id = f"{session_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{str(uuid.uuid4())[:8]}"
        freeze_path = self.emergency_dir / f"{freeze_id}.json"
        
        self.logger.info(f"Creating emergency freeze: {freeze_id}")
        
        try:
            # Collect all relevant data
            freeze_data = {
                'freeze_id': freeze_id,
                'session_id': session_id,
                'timestamp': datetime.now().isoformat(),
                'type': 'emergency_freeze',
                'data': await self._collect_session_data(session_id)
            }
            
            # Save freeze data
            with open(freeze_path, 'w') as f:
                json.dump(freeze_data, f, indent=2)
            
            self.logger.info(f"Emergency freeze created: {freeze_id}")
            return freeze_id
            
        except Exception as e:
            self.logger.error(f"Failed to create emergency freeze: {e}")
            raise
    
    async def unfreeze(self, freeze_id: str) -> bool:
        """
        Restore from an emergency freeze.
        
        Args:
            freeze_id: ID of the freeze to restore
            
        Returns:
            True if successful
        """
        freeze_path = self.emergency_dir / f"{freeze_id}.json"
        
        if not freeze_path.exists():
            self.logger.error(f"Freeze file not found: {freeze_id}")
            return False
        
        try:
            # Load freeze data
            with open(freeze_path, 'r') as f:
                freeze_data = json.load(f)
            
            session_id = freeze_data['session_id']
            self.logger.info(f"Restoring from freeze: {freeze_id} for session {session_id}")
            
            # Restore session data
            await self._restore_session_data(session_id, freeze_data['data'])
            
            self.logger.info(f"Successfully restored from freeze: {freeze_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to restore from freeze {freeze_id}: {e}")
            return False
    
    async def create_emergency_backup(self, session_id: str) -> str:
        """
        Create a quick emergency backup before risky operations.
        
        Args:
            session_id: Session to backup
            
        Returns:
            Backup ID
        """
        backup_id = f"{session_id}_emergency_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        backup_path = self.data_dir / 'backups' / f"{backup_id}.json"
        backup_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            backup_data = {
                'backup_id': backup_id,
                'session_id': session_id,
                'timestamp': datetime.now().isoformat(),
                'type': 'emergency_backup',
                'data': await self._collect_session_data(session_id)
            }
            
            with open(backup_path, 'w') as f:
                json.dump(backup_data, f, indent=2)
            
            return backup_id
            
        except Exception as e:
            self.logger.error(f"Failed to create emergency backup: {e}")
            raise
    
    async def _collect_session_data(self, session_id: str) -> Dict[str, Any]:
        """Collect all data for a session"""
        data = {
            'session_id': session_id,
            'collected_at': datetime.now().isoformat()
        }
        
        # Collect session file
        session_file = self.data_dir / 'sessions' / f'{session_id}.json'
        if session_file.exists():
            with open(session_file, 'r') as f:
                data['session'] = json.load(f)
        
        # Collect state files
        states_dir = self.data_dir / 'states' / session_id
        if states_dir.exists():
            data['states'] = {}
            for state_file in states_dir.glob('*.json'):
                with open(state_file, 'r') as f:
                    data['states'][state_file.name] = json.load(f)
        
        return data
    
    async def _restore_session_data(self, session_id: str, data: Dict[str, Any]):
        """Restore session data from backup"""
        # Restore session file
        if 'session' in data:
            session_file = self.data_dir / 'sessions' / f'{session_id}.json'
            session_file.parent.mkdir(parents=True, exist_ok=True)
            with open(session_file, 'w') as f:
                json.dump(data['session'], f, indent=2)
        
        # Restore state files
        if 'states' in data:
            states_dir = self.data_dir / 'states' / session_id
            states_dir.mkdir(parents=True, exist_ok=True)
            
            for filename, state_data in data['states'].items():
                state_file = states_dir / filename
                with open(state_file, 'w') as f:
                    json.dump(state_data, f, indent=2)
