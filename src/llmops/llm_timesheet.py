"""
LLM Timesheet - A system for tracking LLM contributions.

Simplified version of the original LLM Timesheet system, adapted for the
Continuity Protocol.
"""

import os
import uuid
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Union

# Configure logging
logger = logging.getLogger("llmops.timesheet")

# Base directories
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TIMESHEET_DIR = os.path.join(BASE_DIR, "data", "llmops", "timesheets")
SPRINTS_DIR = os.path.join(BASE_DIR, "data", "llmops", "sprints")
REPORTS_DIR = os.path.join(BASE_DIR, "data", "llmops", "reports")
CONFIG_FILE = os.path.join(BASE_DIR, "data", "llmops", "config.json")

# Ensure directories exist
os.makedirs(TIMESHEET_DIR, exist_ok=True)
os.makedirs(SPRINTS_DIR, exist_ok=True)
os.makedirs(REPORTS_DIR, exist_ok=True)
os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)

# Default configuration
DEFAULT_CONFIG = {
    "project_name": os.path.basename(os.path.dirname(BASE_DIR)),
    "current_sprint": "sprint-1",
    "sprint_duration_days": 7,
    "known_llms": ["claude", "gpt-4", "gemini", "llama"],
    "timesheet_format": "json",
    "auto_organize": True,
    "organization_rules": {
        "code": ["*.py", "*.js", "*.html", "*.css", "*.sh"],
        "documentation": ["*.md", "README*", "*.txt"],
        "configuration": ["*.json", "*.yml", "*.yaml", "*.toml"],
        "data": ["*.csv", "*.json", "*.xml"]
    }
}

# Load or create configuration
if os.path.exists(CONFIG_FILE):
    with open(CONFIG_FILE, 'r') as f:
        config = json.load(f)
else:
    config = DEFAULT_CONFIG
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2)

class LLMTimesheet:
    """LLM Timesheet system for tracking LLM contributions"""
    
    def __init__(self):
        """Initialize the timesheet system"""
        self.config = config
        self.current_sprint = self.config["current_sprint"]
        
        # Load or create current sprint
        self.sprint_path = os.path.join(SPRINTS_DIR, f"{self.current_sprint}.json")
        if os.path.exists(self.sprint_path):
            with open(self.sprint_path, 'r') as f:
                self.sprint = json.load(f)
        else:
            # Create new sprint
            start_date = datetime.now().isoformat()
            self.sprint = {
                "sprint_id": self.current_sprint,
                "project_name": self.config["project_name"],
                "start_date": start_date,
                "end_date": None,
                "status": "active",
                "tasks": [],
                "contributors": {},
                "summary": None
            }
            self._save_sprint()
    
    def _save_sprint(self):
        """Save the current sprint"""
        with open(self.sprint_path, 'w') as f:
            json.dump(self.sprint, f, indent=2)
    
    def punch_in(self, llm_name: str, task_description: str, context: Optional[str] = None) -> str:
        """
        Register the start of a task
        
        Args:
            llm_name: Name of the LLM
            task_description: Description of the task
            context: Additional context (optional)
            
        Returns:
            Task ID
        """
        logger.info(f"Punch in: {llm_name} - {task_description}")
        
        # Generate unique ID
        task_id = str(uuid.uuid4())
        
        # Create task record
        task = {
            "task_id": task_id,
            "llm_name": llm_name,
            "description": task_description,
            "context": context,
            "start_time": datetime.now().isoformat(),
            "end_time": None,
            "status": "in_progress",
            "files_modified": [],
            "summary": None
        }
        
        # Add task to sprint
        self.sprint["tasks"].append(task)
        
        # Update contributors
        if llm_name not in self.sprint["contributors"]:
            self.sprint["contributors"][llm_name] = {
                "tasks_completed": 0,
                "tasks_in_progress": 1,
                "total_time": 0
            }
        else:
            self.sprint["contributors"][llm_name]["tasks_in_progress"] += 1
        
        # Save sprint
        self._save_sprint()
        
        # Create timesheet
        timesheet = {
            "task_id": task_id,
            "llm_name": llm_name,
            "sprint_id": self.current_sprint,
            "description": task_description,
            "context": context,
            "start_time": datetime.now().isoformat(),
            "end_time": None,
            "duration_seconds": 0,
            "files_modified": [],
            "summary": None
        }
        
        # Save timesheet
        timesheet_path = os.path.join(TIMESHEET_DIR, f"{task_id}.json")
        with open(timesheet_path, 'w') as f:
            json.dump(timesheet, f, indent=2)
        
        return task_id
    
    def punch_out(self, task_id: str, summary: str, files_modified: List[str] = None) -> Dict[str, Any]:
        """
        Register the end of a task
        
        Args:
            task_id: Task ID
            summary: Summary of work done
            files_modified: List of modified files (optional)
            
        Returns:
            Task data
        """
        logger.info(f"Punch out: {task_id}")
        
        # Load timesheet
        timesheet_path = os.path.join(TIMESHEET_DIR, f"{task_id}.json")
        if not os.path.exists(timesheet_path):
            logger.error(f"Timesheet not found: {task_id}")
            return {"error": "Timesheet not found"}
        
        with open(timesheet_path, 'r') as f:
            timesheet = json.load(f)
        
        # Update timesheet
        timesheet["end_time"] = datetime.now().isoformat()
        timesheet["summary"] = summary
        
        # Calculate duration
        start_time = datetime.fromisoformat(timesheet["start_time"])
        end_time = datetime.fromisoformat(timesheet["end_time"])
        duration_seconds = (end_time - start_time).total_seconds()
        timesheet["duration_seconds"] = duration_seconds
        
        # Add modified files
        if files_modified:
            timesheet["files_modified"] = files_modified
        
        # Update task in sprint
        for task in self.sprint["tasks"]:
            if task["task_id"] == task_id:
                task["end_time"] = timesheet["end_time"]
                task["status"] = "completed"
                task["summary"] = summary
                if files_modified:
                    task["files_modified"] = files_modified
                
                # Update contributor
                llm_name = task["llm_name"]
                self.sprint["contributors"][llm_name]["tasks_completed"] += 1
                self.sprint["contributors"][llm_name]["tasks_in_progress"] -= 1
                self.sprint["contributors"][llm_name]["total_time"] += duration_seconds
                break
        
        # Save timesheet and sprint
        with open(timesheet_path, 'w') as f:
            json.dump(timesheet, f, indent=2)
        self._save_sprint()
        
        return timesheet
    
    def create_sprint_report(self) -> Dict[str, Any]:
        """
        Create a report for the current sprint
        
        Returns:
            Sprint report data
        """
        logger.info(f"Creating sprint report: {self.current_sprint}")
        
        # Calculate statistics
        total_tasks = len(self.sprint["tasks"])
        completed_tasks = sum(1 for task in self.sprint["tasks"] if task["status"] == "completed")
        in_progress_tasks = sum(1 for task in self.sprint["tasks"] if task["status"] == "in_progress")
        
        # Get modified files
        files_modified = set()
        for task in self.sprint["tasks"]:
            if "files_modified" in task and task["files_modified"]:
                files_modified.update(task["files_modified"])
        
        # Create report
        report = {
            "sprint_id": self.current_sprint,
            "project_name": self.config["project_name"],
            "start_date": self.sprint["start_date"],
            "end_date": datetime.now().isoformat() if not self.sprint["end_date"] else self.sprint["end_date"],
            "status": self.sprint["status"],
            "statistics": {
                "total_tasks": total_tasks,
                "completed_tasks": completed_tasks,
                "in_progress_tasks": in_progress_tasks,
                "completion_rate": completed_tasks / total_tasks if total_tasks > 0 else 0,
                "total_files_modified": len(files_modified)
            },
            "contributors": self.sprint["contributors"],
            "files_modified": list(files_modified),
            "tasks": [
                {
                    "task_id": task["task_id"],
                    "llm_name": task["llm_name"],
                    "description": task["description"],
                    "status": task["status"],
                    "summary": task["summary"]
                }
                for task in self.sprint["tasks"]
            ]
        }
        
        # Save report
        report_path = os.path.join(REPORTS_DIR, f"{self.current_sprint}_report.json")
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        return report
    
    def finish_sprint(self, summary: str) -> Dict[str, Any]:
        """
        Finish the current sprint and start a new one
        
        Args:
            summary: Sprint summary
            
        Returns:
            Final sprint report
        """
        logger.info(f"Finishing sprint: {self.current_sprint}")
        
        # Finalize in-progress tasks
        for task in self.sprint["tasks"]:
            if task["status"] == "in_progress":
                task["status"] = "incomplete"
        
        # Update sprint
        self.sprint["status"] = "completed"
        self.sprint["end_date"] = datetime.now().isoformat()
        self.sprint["summary"] = summary
        self._save_sprint()
        
        # Create final report
        report = self.create_sprint_report()
        
        # Increment sprint number
        sprint_num = int(self.current_sprint.split("-")[1])
        next_sprint = f"sprint-{sprint_num + 1}"
        
        # Update configuration
        self.config["current_sprint"] = next_sprint
        with open(CONFIG_FILE, 'w') as f:
            json.dump(self.config, f, indent=2)
        
        # Initialize next sprint
        self.current_sprint = next_sprint
        self.sprint = {
            "sprint_id": self.current_sprint,
            "project_name": self.config["project_name"],
            "start_date": datetime.now().isoformat(),
            "end_date": None,
            "status": "active",
            "tasks": [],
            "contributors": {},
            "summary": None
        }
        self.sprint_path = os.path.join(SPRINTS_DIR, f"{self.current_sprint}.json")
        self._save_sprint()
        
        return report
    
    def detect_modified_files(self, since: Optional[str] = None) -> List[str]:
        """
        Detect files modified since a given time
        
        Args:
            since: ISO timestamp (optional)
            
        Returns:
            List of modified file paths
        """
        logger.info("Detecting modified files")
        
        # Base directory
        base_dir = BASE_DIR
        
        # Try using git if available
        try:
            if os.path.exists(os.path.join(base_dir, ".git")):
                if since:
                    # Convert ISO timestamp to git format
                    dt = datetime.fromisoformat(since)
                    git_time = dt.strftime("%Y-%m-%d %H:%M:%S")
                    cmd = ["git", "-C", base_dir, "diff", "--name-only", f"--since=\"{git_time}\""]
                else:
                    cmd = ["git", "-C", base_dir, "diff", "--name-only"]
                
                import subprocess
                result = subprocess.run(cmd, capture_output=True, text=True)
                if result.returncode == 0:
                    files = [os.path.join(base_dir, f) for f in result.stdout.strip().split("\n") if f]
                    return files
        except Exception as e:
            logger.warning(f"Error using git: {e}")
        
        # Fallback: use file modification time
        files = []
        if since:
            since_dt = datetime.fromisoformat(since)
            since_timestamp = since_dt.timestamp()
            
            for root, _, filenames in os.walk(base_dir):
                for filename in filenames:
                    file_path = os.path.join(root, filename)
                    try:
                        mtime = os.path.getmtime(file_path)
                        if mtime >= since_timestamp:
                            files.append(file_path)
                    except Exception:
                        pass
        
        return files