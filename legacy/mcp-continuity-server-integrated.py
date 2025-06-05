#!/usr/bin/env python3
"""
MCP Continuity Server - Integrated Version with LLMOps
Integrates bash scripts and LLM Timesheet with MCP protocol for seamless continuity
"""

import subprocess
import os
import sys
from typing import Dict, List, Any, Optional

# Import FastMCP
from mcp.server.fastmcp import FastMCP

# Base paths
CONTINUITY_BASE = "/Users/lucascardoso/apps/MCP/CONTINUITY"
SCRIPTS_PATH = CONTINUITY_BASE

# Adicionar path para módulos locais
sys.path.append(CONTINUITY_BASE)

# Importar módulo de timesheet MCP
from llmops.llm_timesheet_mcp import LLMTimesheetMCP

# Initialize FastMCP Server
mcp = FastMCP("MCP-Continuity-Integrated")

# Initialize LLM Timesheet
timesheet_mcp = LLMTimesheetMCP()

def run_bash_script(script_name: str, args: List[str] = None) -> Dict[str, Any]:
    """Execute bash script and return structured result"""
    try:
        script_path = f"{SCRIPTS_PATH}/{script_name}"
        
        if not os.path.exists(script_path):
            return {
                "error": f"Script not found: {script_path}",
                "success": False
            }
        
        cmd = [script_path]
        if args:
            cmd.extend(args)
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        return {
            "success": result.returncode == 0,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode
        }
        
    except subprocess.TimeoutExpired:
        return {
            "error": "Script execution timeout",
            "success": False
        }
    except Exception as e:
        return {
            "error": f"Execution error: {str(e)}",
            "success": False
        }

#
# Ferramentas de Continuidade Original
#

@mcp.tool()
def continuity_where_stopped() -> str:
    """Execute 'onde paramos?' - automatic recovery and context loading"""
    result = run_bash_script("autonomous-recovery.sh")
    
    if result.get("success"):
        response = f"✅ SUCCESS\n\n{result.get('stdout', '')}"
        if result.get('stderr'):
            response += f"\n\n⚠️ WARNINGS:\n{result['stderr']}"
        return response
    else:
        response = f"❌ ERROR: {result.get('error', 'Unknown error')}"
        if result.get('stderr'):
            response += f"\n\nSTDERR: {result['stderr']}"
        if result.get('stdout'):
            response += f"\n\nSTDOUT: {result['stdout']}"
        return response

@mcp.tool()
def continuity_magic_system(user_input: str) -> str:
    """Process user input through magic detection system"""
    result = run_bash_script("magic-system.sh", [user_input])
    
    if result.get("success"):
        response = f"✅ SUCCESS\n\n{result.get('stdout', '')}"
        if result.get('stderr'):
            response += f"\n\n⚠️ WARNINGS:\n{result['stderr']}"
        return response
    else:
        response = f"❌ ERROR: {result.get('error', 'Unknown error')}"
        if result.get('stderr'):
            response += f"\n\nSTDERR: {result['stderr']}"
        if result.get('stdout'):
            response += f"\n\nSTDOUT: {result['stdout']}"
        return response

@mcp.tool()
def continuity_emergency_freeze() -> str:
    """Create emergency backup freeze of current state"""
    result = run_bash_script("emergency-absolute.sh", ["freeze"])
    
    if result.get("success"):
        response = f"✅ SUCCESS\n\n{result.get('stdout', '')}"
        if result.get('stderr'):
            response += f"\n\n⚠️ WARNINGS:\n{result['stderr']}"
        return response
    else:
        response = f"❌ ERROR: {result.get('error', 'Unknown error')}"
        if result.get('stderr'):
            response += f"\n\nSTDERR: {result['stderr']}"
        if result.get('stdout'):
            response += f"\n\nSTDOUT: {result['stdout']}"
        return response

@mcp.tool()
def continuity_emergency_unfreeze() -> str:
    """Restore from emergency backup freeze"""
    result = run_bash_script("emergency-absolute.sh", ["unfreeze"])
    
    if result.get("success"):
        response = f"✅ SUCCESS\n\n{result.get('stdout', '')}"
        if result.get('stderr'):
            response += f"\n\n⚠️ WARNINGS:\n{result['stderr']}"
        return response
    else:
        response = f"❌ ERROR: {result.get('error', 'Unknown error')}"
        if result.get('stderr'):
            response += f"\n\nSTDERR: {result['stderr']}"
        if result.get('stdout'):
            response += f"\n\nSTDOUT: {result['stdout']}"
        return response

@mcp.tool()
def continuity_system_status() -> str:
    """Get complete system status and project overview"""
    result = run_bash_script("emergency-absolute.sh", ["status"])
    
    if result.get("success"):
        response = f"✅ SUCCESS\n\n{result.get('stdout', '')}"
        if result.get('stderr'):
            response += f"\n\n⚠️ WARNINGS:\n{result['stderr']}"
        return response
    else:
        response = f"❌ ERROR: {result.get('error', 'Unknown error')}"
        if result.get('stderr'):
            response += f"\n\nSTDERR: {result['stderr']}"
        if result.get('stdout'):
            response += f"\n\nSTDOUT: {result['stdout']}"
        return response

#
# Ferramentas de LLMOps Timesheet
#

@mcp.tool()
def llm_punch_in(llm_name: str, task_description: str, context: Optional[str] = None) -> Dict[str, Any]:
    """
    Registra o início de uma tarefa para um LLM
    
    Args:
        llm_name: Nome do LLM (ex: "claude", "gpt-4")
        task_description: Descrição da tarefa
        context: Contexto adicional (opcional)
        
    Returns:
        Informações sobre a tarefa iniciada
    """
    return timesheet_mcp.punch_in(llm_name, task_description, context)

@mcp.tool()
def llm_punch_out(task_id: str, summary: str, detect_files: bool = True) -> Dict[str, Any]:
    """
    Registra o fim de uma tarefa para um LLM
    
    Args:
        task_id: ID da tarefa
        summary: Resumo do trabalho realizado
        detect_files: Se deve detectar automaticamente arquivos modificados
        
    Returns:
        Informações sobre a tarefa finalizada
    """
    return timesheet_mcp.punch_out(task_id, summary, detect_files)

@mcp.tool()
def llm_sprint_report() -> Dict[str, Any]:
    """
    Gera um relatório do sprint atual
    
    Returns:
        Relatório do sprint atual
    """
    return timesheet_mcp.get_sprint_report()

@mcp.tool()
def llm_finish_sprint(summary: str) -> Dict[str, Any]:
    """
    Finaliza o sprint atual e inicia um novo
    
    Args:
        summary: Resumo do sprint
        
    Returns:
        Informações sobre o sprint finalizado
    """
    return timesheet_mcp.finish_sprint(summary)

@mcp.tool()
def llm_active_tasks() -> Dict[str, Any]:
    """
    Lista tarefas ativas no sprint atual
    
    Returns:
        Lista de tarefas ativas
    """
    return timesheet_mcp.list_active_tasks()

@mcp.tool()
def llm_task_details(task_id: str) -> Dict[str, Any]:
    """
    Obtém detalhes de uma tarefa específica
    
    Args:
        task_id: ID da tarefa
        
    Returns:
        Detalhes da tarefa
    """
    return timesheet_mcp.get_task_details(task_id)

@mcp.tool()
def llm_auto_punch_in(llm_name: str, task_description: str) -> Dict[str, Any]:
    """
    Inicia uma sessão automática para o LLM, detectando o contexto
    
    Args:
        llm_name: Nome do LLM
        task_description: Descrição da tarefa
        
    Returns:
        Informações sobre a tarefa iniciada
    """
    # Detectar contexto atual
    result = run_bash_script("smart-context-detector.sh")
    context = None
    
    if result.get("success") and result.get("stdout"):
        context = result.get("stdout").strip()
    
    # Registrar início da tarefa
    return timesheet_mcp.punch_in(llm_name, task_description, context)

@mcp.tool()
def llm_auto_punch_out(task_id: str, summary: str) -> Dict[str, Any]:
    """
    Finaliza uma sessão automática para o LLM, fazendo backup e detectando arquivos
    
    Args:
        task_id: ID da tarefa
        summary: Resumo do trabalho realizado
        
    Returns:
        Informações sobre a tarefa finalizada
    """
    # Criar backup antes de finalizar
    run_bash_script("auto-backup.sh")
    
    # Registrar fim da tarefa
    return timesheet_mcp.punch_out(task_id, summary, True)

@mcp.tool()
def llm_auto_session(llm_name: str, task_description: str, summary: str) -> Dict[str, Any]:
    """
    Executa uma sessão completa (punch in + punch out) em uma única chamada
    
    Args:
        llm_name: Nome do LLM
        task_description: Descrição da tarefa
        summary: Resumo do trabalho realizado
        
    Returns:
        Informações sobre a sessão completa
    """
    # Iniciar tarefa
    punch_in_result = llm_auto_punch_in(llm_name, task_description)
    
    if not punch_in_result.get("success", False):
        return punch_in_result
    
    task_id = punch_in_result["task_id"]
    
    # Finalizar tarefa
    punch_out_result = llm_auto_punch_out(task_id, summary)
    
    return {
        "success": punch_out_result.get("success", False),
        "task_id": task_id,
        "start": punch_in_result,
        "end": punch_out_result
    }

if __name__ == "__main__":
    # FastMCP simplifica tudo - só precisa disso!
    mcp.run(transport="stdio")