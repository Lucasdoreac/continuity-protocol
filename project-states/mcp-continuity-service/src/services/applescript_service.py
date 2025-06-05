"""
AppleScript Service - Integration with macOS applications and system
Captures system context and automates macOS workflows
"""

import asyncio
import subprocess
import json
from typing import Dict, List, Optional, Any
from datetime import datetime
import logging
from pathlib import Path


class AppleScriptService:
    """
    Service for integrating with macOS applications via AppleScript.
    Captures system context and automates macOS workflows.
    """
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # Check if running on macOS
        import platform
        if platform.system() != 'Darwin':
            self.logger.warning("AppleScript service only works on macOS")
            self.available = False
        else:
            self.available = True
    
    async def execute_applescript(self, script: str) -> str:
        """Execute AppleScript and return result"""
        if not self.available:
            return "AppleScript not available on this platform"
        
        try:
            process = await asyncio.create_subprocess_exec(
                'osascript', '-e', script,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                return stdout.decode('utf-8').strip()
            else:
                error_msg = stderr.decode('utf-8').strip()
                self.logger.error(f"AppleScript error: {error_msg}")
                return f"Error: {error_msg}"
                
        except Exception as e:
            self.logger.error(f"AppleScript execution failed: {e}")
            return f"Error: {str(e)}"
    
    async def capture_system_context(self) -> Dict[str, Any]:
        """Capture comprehensive system context"""
        if not self.available:
            return {"error": "AppleScript not available"}
        
        context = {
            "timestamp": datetime.now().isoformat(),
            "system": await self.get_system_info(),
            "applications": await self.get_running_applications(),
            "frontmost_app": await self.get_frontmost_application(),
            "open_documents": await self.get_open_documents(),
            "finder_info": await self.get_finder_info(),
            "notes": await self.get_recent_notes(),
            "calendar": await self.get_recent_calendar_events()
        }
        
        return context
    
    async def get_system_info(self) -> Dict[str, Any]:
        """Get basic system information"""
        script = '''
        tell application "System Information"
            set systemInfo to system info
            return "macOS " & (system version of systemInfo) & ", " & (computer name of systemInfo)
        end tell
        '''
        
        result = await self.execute_applescript(script)
        return {"info": result}
    
    async def get_running_applications(self) -> List[Dict[str, str]]:
        """Get list of running applications"""
        script = '''
        tell application "System Events"
            set appList to {}
            repeat with theApp in (application processes whose visible is true)
                set end of appList to (name of theApp)
            end repeat
            return my listToString(appList, ", ")
        end tell
        
        on listToString(lst, delim)
            set AppleScript's text item delimiters to delim
            set str to lst as string
            set AppleScript's text item delimiters to ""
            return str
        end listToString
        '''
        
        result = await self.execute_applescript(script)
        if result and not result.startswith("Error"):
            apps = [{"name": app.strip()} for app in result.split(", ") if app.strip()]
            return apps
        return []
    
    async def get_frontmost_application(self) -> Dict[str, str]:
        """Get currently active application"""
        script = '''
        tell application "System Events"
            set frontApp to name of first application process whose frontmost is true
            return frontApp
        end tell
        '''
        
        result = await self.execute_applescript(script)
        return {"name": result if not result.startswith("Error") else "Unknown"}
    
    async def get_open_documents(self) -> List[Dict[str, str]]:
        """Get open documents from various applications"""
        # This is a simplified version - could be expanded for specific apps
        script = '''
        set documentList to {}
        
        -- Check Finder windows
        tell application "Finder"
            try
                repeat with theWindow in windows
                    set end of documentList to ("Finder: " & (name of theWindow))
                end repeat
            end try
        end tell
        
        -- Check TextEdit documents
        tell application "TextEdit"
            try
                repeat with theDoc in documents
                    set end of documentList to ("TextEdit: " & (name of theDoc))
                end repeat
            end try
        end tell
        
        return my listToString(documentList, "\\n")
        
        on listToString(lst, delim)
            set AppleScript's text item delimiters to delim
            set str to lst as string
            set AppleScript's text item delimiters to ""
            return str
        end listToString
        '''
        
        result = await self.execute_applescript(script)
        if result and not result.startswith("Error"):
            docs = [{"document": doc.strip()} for doc in result.split("\n") if doc.strip()]
            return docs
        return []
    
    async def get_finder_info(self) -> Dict[str, Any]:
        """Get current Finder window information"""
        script = '''
        tell application "Finder"
            try
                set currentWindow to front window
                set currentPath to (target of currentWindow as string)
                set currentView to (current view of currentWindow as string)
                return "Path: " & currentPath & ", View: " & currentView
            on error
                return "No Finder window open"
            end try
        end tell
        '''
        
        result = await self.execute_applescript(script)
        return {"info": result}
    
    async def get_recent_notes(self) -> List[Dict[str, str]]:
        """Get recent notes from Apple Notes"""
        script = '''
        tell application "Notes"
            try
                set recentNotes to {}
                repeat with i from 1 to (count of notes)
                    if i > 5 then exit repeat -- Limit to 5 recent notes
                    set theNote to note i
                    set noteTitle to name of theNote
                    set end of recentNotes to noteTitle
                end repeat
                return my listToString(recentNotes, "\\n")
            on error
                return "No notes available"
            end try
        end tell
        
        on listToString(lst, delim)
            set AppleScript's text item delimiters to delim
            set str to lst as string
            set AppleScript's text item delimiters to ""
            return str
        end listToString
        '''
        
        result = await self.execute_applescript(script)
        if result and not result.startswith("Error") and result != "No notes available":
            notes = [{"title": note.strip()} for note in result.split("\n") if note.strip()]
            return notes
        return []
    
    async def get_recent_calendar_events(self) -> List[Dict[str, str]]:
        """Get recent calendar events"""
        script = '''
        tell application "Calendar"
            try
                set todayEvents to {}
                set today to current date
                set startOfDay to date (short date string of today)
                set endOfDay to startOfDay + (24 * 60 * 60) - 1
                
                repeat with cal in calendars
                    set dayEvents to (events of cal whose start date ≥ startOfDay and start date ≤ endOfDay)
                    repeat with evt in dayEvents
                        set end of todayEvents to (summary of evt)
                    end repeat
                end repeat
                
                return my listToString(todayEvents, "\\n")
            on error
                return "No calendar events"
            end try
        end tell
        
        on listToString(lst, delim)
            set AppleScript's text item delimiters to delim
            set str to lst as string
            set AppleScript's text item delimiters to ""
            return str
        end listToString
        '''
        
        result = await self.execute_applescript(script)
        if result and not result.startswith("Error") and result != "No calendar events":
            events = [{"summary": event.strip()} for event in result.split("\n") if event.strip()]
            return events
        return []
    
    async def create_note(self, title: str, content: str) -> bool:
        """Create a new note in Apple Notes"""
        script = f'''
        tell application "Notes"
            make new note with properties {{name:"{title}", body:"{content}"}}
            return "Note created successfully"
        end tell
        '''
        
        result = await self.execute_applescript(script)
        return not result.startswith("Error")
    
    async def save_continuity_note(self, session_id: str, context: Dict[str, Any]) -> bool:
        """Save continuity context as a note"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        title = f"Continuity Context - {session_id} - {timestamp}"
        
        content = f"""
Continuity Context Saved: {timestamp}
Session ID: {session_id}

Active Projects:
{json.dumps(context.get('projects', []), indent=2)}

Critical Missions:
{json.dumps(context.get('critical_missions', []), indent=2)}

System Context:
{json.dumps(context.get('system_context', {}), indent=2)}

Generated by MCP Continuity Service
"""
        
        return await self.create_note(title, content)
    
    async def get_desktop_files(self) -> List[str]:
        """Get files on desktop"""
        script = '''
        tell application "Finder"
            set desktopFiles to {}
            repeat with theItem in (items of desktop)
                set end of desktopFiles to (name of theItem)
            end repeat
            return my listToString(desktopFiles, "\\n")
        end tell
        
        on listToString(lst, delim)
            set AppleScript's text item delimiters to delim
            set str to lst as string
            set AppleScript's text item delimiters to ""
            return str
        end listToString
        '''
        
        result = await self.execute_applescript(script)
        if result and not result.startswith("Error"):
            return [file.strip() for file in result.split("\n") if file.strip()]
        return []
    
    async def get_battery_status(self) -> Dict[str, Any]:
        """Get battery status"""
        script = '''
        tell application "System Events"
            tell power source 1 of power source domain "system"
                set batteryLevel to capacity
                set isCharging to charging
                return "Level: " & batteryLevel & "%, Charging: " & isCharging
            end tell
        end tell
        '''
        
        result = await self.execute_applescript(script)
        return {"status": result}
