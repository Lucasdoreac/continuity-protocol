"""
LLM Timesheet MCP Adapter

This module provides MCP-compatible functions for the LLM Timesheet system,
allowing it to be used through the Model Context Protocol.
"""

import os
import sys
import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List, Union

# Configure logging
logger = logging.getLogger("llmops.timesheet-mcp")

# Ensure the llmops module can be imported
from llmops.llm_timesheet import LLMTimesheet

# Singleton instance of LLM Timesheet
_timesheet_instance = None

def _get_timesheet() -> LLMTimesheet:
    """Get or initialize the LLM Timesheet singleton instance"""
    global _timesheet_instance
    
    if _timesheet_instance is None:
        _timesheet_instance = LLMTimesheet()
    
    return _timesheet_instance

def llm_punch_in(llm_name: str, task_description: str, context: Optional[str] = None) -> Dict[str, Any]:
    """
    Register the start of a task for an LLM.
    
    Args:
        llm_name: Name of the LLM (e.g., 'claude', 'gpt-4')
        task_description: Description of the task
        context: Additional context (optional)
        
    Returns:
        Dictionary with task information
    """
    try:
        timesheet = _get_timesheet()
        task_id = timesheet.punch_in(llm_name, task_description, context)
        
        logger.info(f"Task started: {task_id} - {llm_name} - {task_description}")
        
        return {
            "success": True,
            "task_id": task_id,
            "llm_name": llm_name,
            "task_description": task_description,
            "start_time": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error in llm_punch_in: {str(e)}")
        return {
            "success": False,
            "error": f"Error registering task start: {str(e)}"
        }

def llm_punch_out(task_id: str, summary: str, detect_files: bool = True) -> Dict[str, Any]:
    """
    Register the end of a task for an LLM.
    
    Args:
        task_id: Task identifier
        summary: Summary of the work done
        detect_files: Whether to automatically detect modified files
        
    Returns:
        Dictionary with task completion information
    """
    try:
        timesheet = _get_timesheet()
        
        # Detect modified files if requested
        files_modified = None
        if detect_files:
            # Get the start time of the task
            start_time = None
            
            # Try to find task in current sprint
            for task in timesheet.sprint["tasks"]:
                if task["task_id"] == task_id:
                    start_time = task["start_time"]
                    break
            
            # If not found in sprint tasks, try to load from timesheet file
            if start_time is None:
                # Determine timesheet directory
                from llmops.llm_timesheet import TIMESHEET_DIR
                
                timesheet_path = os.path.join(TIMESHEET_DIR, f"{task_id}.json")
                if os.path.exists(timesheet_path):
                    with open(timesheet_path, 'r') as f:
                        timesheet_data = json.load(f)
                        start_time = timesheet_data.get("start_time")
            
            # Detect modified files
            if start_time:
                files_modified = timesheet.detect_modified_files(start_time)
        
        # Register task completion
        result = timesheet.punch_out(task_id, summary, files_modified)
        
        if "error" in result:
            logger.error(f"Error in timesheet.punch_out: {result['error']}")
            return {
                "success": False,
                "error": result["error"]
            }
        
        logger.info(f"Task completed: {task_id} - {summary}")
        
        return {
            "success": True,
            "task_id": task_id,
            "duration_seconds": result.get("duration_seconds", 0),
            "end_time": result.get("end_time"),
            "files_modified": len(result.get("files_modified", [])),
            "summary": summary
        }
    except Exception as e:
        logger.error(f"Error in llm_punch_out: {str(e)}")
        return {
            "success": False,
            "error": f"Error registering task completion: {str(e)}"
        }

def llm_sprint_report() -> Dict[str, Any]:
    """
    Generate a report for the current sprint.
    
    Returns:
        Dictionary with sprint report
    """
    try:
        timesheet = _get_timesheet()
        report = timesheet.create_sprint_report()
        
        logger.info(f"Sprint report generated: {report['sprint_id']}")
        
        return {
            "success": True,
            "sprint_id": report["sprint_id"],
            "project_name": report["project_name"],
            "status": report["status"],
            "statistics": report["statistics"],
            "contributors": report["contributors"]
        }
    except Exception as e:
        logger.error(f"Error in llm_sprint_report: {str(e)}")
        return {
            "success": False,
            "error": f"Error generating sprint report: {str(e)}"
        }

def llm_finish_sprint(summary: str) -> Dict[str, Any]:
    """
    Finish the current sprint and start a new one.
    
    Args:
        summary: Sprint summary
        
    Returns:
        Dictionary with sprint completion information
    """
    try:
        timesheet = _get_timesheet()
        report = timesheet.finish_sprint(summary)
        
        logger.info(f"Sprint finished: {report['sprint_id']}")
        
        return {
            "success": True,
            "sprint_id": report["sprint_id"],
            "completion_rate": report["statistics"]["completion_rate"],
            "next_sprint": timesheet.current_sprint
        }
    except Exception as e:
        logger.error(f"Error in llm_finish_sprint: {str(e)}")
        return {
            "success": False,
            "error": f"Error finishing sprint: {str(e)}"
        }

def llm_active_tasks() -> Dict[str, Any]:
    """
    List active tasks in the current sprint.
    
    Returns:
        Dictionary with list of active tasks
    """
    try:
        timesheet = _get_timesheet()
        active_tasks = []
        
        for task in timesheet.sprint["tasks"]:
            if task["status"] == "in_progress":
                active_tasks.append({
                    "task_id": task["task_id"],
                    "llm_name": task["llm_name"],
                    "description": task["description"],
                    "start_time": task["start_time"]
                })
        
        logger.info(f"Listed {len(active_tasks)} active tasks")
        
        return {
            "success": True,
            "sprint_id": timesheet.current_sprint,
            "active_tasks": active_tasks,
            "count": len(active_tasks)
        }
    except Exception as e:
        logger.error(f"Error in llm_active_tasks: {str(e)}")
        return {
            "success": False,
            "error": f"Error listing active tasks: {str(e)}"
        }

def llm_task_details(task_id: str) -> Dict[str, Any]:
    """
    Get details of a specific task.
    
    Args:
        task_id: Task identifier
        
    Returns:
        Dictionary with task details
    """
    try:
        timesheet = _get_timesheet()
        
        # Try to find task in current sprint
        for task in timesheet.sprint["tasks"]:
            if task["task_id"] == task_id:
                return {
                    "success": True,
                    "task_id": task["task_id"],
                    "llm_name": task["llm_name"],
                    "description": task["description"],
                    "status": task["status"],
                    "start_time": task["start_time"],
                    "end_time": task.get("end_time"),
                    "summary": task.get("summary"),
                    "files_modified": len(task.get("files_modified", []))
                }
        
        # If not found in sprint tasks, try to load from timesheet file
        from llmops.llm_timesheet import TIMESHEET_DIR
        
        timesheet_path = os.path.join(TIMESHEET_DIR, f"{task_id}.json")
        if os.path.exists(timesheet_path):
            with open(timesheet_path, 'r') as f:
                task_data = json.load(f)
                return {
                    "success": True,
                    "task_id": task_data["task_id"],
                    "llm_name": task_data["llm_name"],
                    "description": task_data["description"],
                    "status": "completed" if task_data.get("end_time") else "in_progress",
                    "start_time": task_data["start_time"],
                    "end_time": task_data.get("end_time"),
                    "summary": task_data.get("summary"),
                    "files_modified": len(task_data.get("files_modified", []))
                }
        
        logger.error(f"Task not found: {task_id}")
        return {
            "success": False,
            "error": f"Task not found: {task_id}"
        }
    except Exception as e:
        logger.error(f"Error in llm_task_details: {str(e)}")
        return {
            "success": False,
            "error": f"Error retrieving task details: {str(e)}"
        }

def llm_auto_session(llm_name: str, task_description: str, summary: str) -> Dict[str, Any]:
    """
    Execute a complete LLM session (punch in + punch out) in a single call.
    
    Args:
        llm_name: Name of the LLM
        task_description: Description of the task
        summary: Summary of the work done
        
    Returns:
        Dictionary with session information
    """
    try:
        # Start task
        start_result = llm_punch_in(llm_name, task_description)
        
        if not start_result["success"]:
            return start_result
        
        task_id = start_result["task_id"]
        
        # End task
        end_result = llm_punch_out(task_id, summary, True)
        
        return {
            "success": end_result["success"],
            "task_id": task_id,
            "start": start_result,
            "end": end_result
        }
    except Exception as e:
        logger.error(f"Error in llm_auto_session: {str(e)}")
        return {
            "success": False,
            "error": f"Error executing auto session: {str(e)}"
        }