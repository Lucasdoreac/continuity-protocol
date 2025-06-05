"""
Smart Cleanup - Intelligent cleanup of system resources and data
"""

import asyncio
import os
import shutil
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from pathlib import Path
import logging


class SmartCleanup:
    """
    Handles intelligent cleanup of system resources to optimize token usage
    and maintain system performance.
    """
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        self.data_dir = Path(self.config.get('data_dir', 'data'))
        
        # Cleanup thresholds
        self.log_retention_days = self.config.get('log_retention_days', 2)
        self.backup_retention_count = self.config.get('backup_retention_count', 6)
        self.session_timeout_hours = self.config.get('session_timeout_hours', 24)
    
    async def cleanup_session(self, session_id: str):
        """Clean up resources for a specific session"""
        self.logger.info(f"Cleaning up session {session_id}")
        
        # Clean old logs
        await self._cleanup_old_logs(session_id)
        
        # Clean excessive backups
        await self._cleanup_old_backups(session_id)
        
        # Clean temporary files
        await self._cleanup_temp_files(session_id)
    
    async def global_cleanup(self):
        """Perform global system cleanup"""
        self.logger.info("Performing global cleanup")
        
        # Clean old logs globally
        logs_dir = self.data_dir / 'logs'
        if logs_dir.exists():
            cutoff_date = datetime.now() - timedelta(days=self.log_retention_days)
            
            for log_file in logs_dir.glob('*.log'):
                if datetime.fromtimestamp(log_file.stat().st_mtime) < cutoff_date:
                    log_file.unlink()
                    self.logger.info(f"Removed old log: {log_file}")
        
        # Clean old emergency freezes
        emergency_dir = self.data_dir / 'emergency'
        if emergency_dir.exists():
            cutoff_date = datetime.now() - timedelta(days=7)
            
            for freeze_file in emergency_dir.glob('*.json'):
                if datetime.fromtimestamp(freeze_file.stat().st_mtime) < cutoff_date:
                    freeze_file.unlink()
                    self.logger.info(f"Removed old freeze: {freeze_file}")
    
    async def _cleanup_old_logs(self, session_id: str):
        """Clean old logs for a session"""
        session_logs = self.data_dir / 'logs' / session_id
        if session_logs.exists():
            cutoff_date = datetime.now() - timedelta(days=self.log_retention_days)
            
            for log_file in session_logs.glob('*.log'):
                if datetime.fromtimestamp(log_file.stat().st_mtime) < cutoff_date:
                    log_file.unlink()
    
    async def _cleanup_old_backups(self, session_id: str):
        """Keep only the most recent backups"""
        backups_dir = self.data_dir / 'backups'
        if not backups_dir.exists():
            return
        
        # Get all backup files for this session
        backup_files = list(backups_dir.glob(f"{session_id}_*.json"))
        
        # Sort by modification time (newest first)
        backup_files.sort(key=lambda f: f.stat().st_mtime, reverse=True)
        
        # Remove excess backups
        if len(backup_files) > self.backup_retention_count:
            for backup_file in backup_files[self.backup_retention_count:]:
                backup_file.unlink()
                self.logger.info(f"Removed old backup: {backup_file}")
    
    async def _cleanup_temp_files(self, session_id: str):
        """Clean temporary files for a session"""
        temp_dir = self.data_dir / 'temp' / session_id
        if temp_dir.exists():
            shutil.rmtree(temp_dir)
            self.logger.info(f"Removed temp directory: {temp_dir}")
    
    async def get_cleanup_stats(self) -> Dict:
        """Get statistics about what can be cleaned up"""
        stats = {
            'old_logs': 0,
            'excess_backups': 0,
            'old_freezes': 0,
            'temp_files': 0,
            'total_size_mb': 0
        }
        
        # Count old logs
        logs_dir = self.data_dir / 'logs'
        if logs_dir.exists():
            cutoff_date = datetime.now() - timedelta(days=self.log_retention_days)
            for log_file in logs_dir.rglob('*.log'):
                if datetime.fromtimestamp(log_file.stat().st_mtime) < cutoff_date:
                    stats['old_logs'] += 1
                    stats['total_size_mb'] += log_file.stat().st_size / (1024 * 1024)
        
        return stats
