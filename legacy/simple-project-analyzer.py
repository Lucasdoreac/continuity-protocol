#!/usr/bin/env python3
"""
Simple Project Analyzer - Uma ferramenta básica para analisar o projeto Continuity
"""

import os
import sys
import json
import subprocess
from datetime import datetime
from typing import Dict, Any, List

# Base paths
BASE_DIR = "/Users/lucascardoso/apps/MCP/CONTINUITY"
ANALYSIS_DIR = os.path.join(BASE_DIR, "analysis")
os.makedirs(ANALYSIS_DIR, exist_ok=True)

# Importar FastMCP
from mcp.server.fastmcp import FastMCP

# Inicializar FastMCP
mcp = FastMCP("continuity-analyzer")

@mcp.tool()
def project_analyze() -> str:
    """
    Analisa a estrutura do projeto Continuity
    """
    # Criar relatório de análise
    report = {
        "project_name": "Continuity Protocol",
        "analysis_date": datetime.now().isoformat(),
        "structure": {},
        "scripts": [],
        "servers": [],
        "documentation": []
    }
    
    # Analisar estrutura de diretórios
    result = subprocess.run(
        ["find", BASE_DIR, "-type", "d", "-not", "-path", "*/\\.*", "-maxdepth", "2"],
        capture_output=True,
        text=True
    )
    
    directories = result.stdout.strip().split("\n")
    report["structure"]["directories"] = [d.replace(BASE_DIR + "/", "") for d in directories if d != BASE_DIR]
    
    # Analisar scripts bash
    result = subprocess.run(
        ["find", BASE_DIR, "-name", "*.sh"],
        capture_output=True,
        text=True
    )
    
    bash_scripts = result.stdout.strip().split("\n")
    for script in bash_scripts:
        if script:
            script_name = os.path.basename(script)
            report["scripts"].append({
                "name": script_name,
                "path": script.replace(BASE_DIR + "/", ""),
                "type": "bash"
            })
    
    # Analisar servidores Python
    result = subprocess.run(
        ["find", BASE_DIR, "-name", "*.py"],
        capture_output=True,
        text=True
    )
    
    python_scripts = result.stdout.strip().split("\n")
    for script in python_scripts:
        if script:
            script_name = os.path.basename(script)
            if "server" in script_name.lower():
                report["servers"].append({
                    "name": script_name,
                    "path": script.replace(BASE_DIR + "/", "")
                })
            else:
                report["scripts"].append({
                    "name": script_name,
                    "path": script.replace(BASE_DIR + "/", ""),
                    "type": "python"
                })
    
    # Analisar documentação
    result = subprocess.run(
        ["find", BASE_DIR, "-name", "*.md"],
        capture_output=True,
        text=True
    )
    
    markdown_files = result.stdout.strip().split("\n")
    for md_file in markdown_files:
        if md_file:
            md_name = os.path.basename(md_file)
            report["documentation"].append({
                "name": md_name,
                "path": md_file.replace(BASE_DIR + "/", "")
            })
    
    # Salvar relatório
    report_path = os.path.join(ANALYSIS_DIR, "project_analysis.json")
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2)
    
    return json.dumps(report, indent=2)

@mcp.tool()
def script_analyze(script_path: str) -> str:
    """
    Analisa um script específico do projeto
    
    Args:
        script_path: Caminho relativo para o script
    """
    full_path = os.path.join(BASE_DIR, script_path)
    
    if not os.path.exists(full_path):
        return json.dumps({"error": f"Script não encontrado: {script_path}"}, indent=2)
    
    # Determinar tipo de script
    script_type = "unknown"
    if script_path.endswith(".sh"):
        script_type = "bash"
    elif script_path.endswith(".py"):
        script_type = "python"
    
    # Ler conteúdo do script
    with open(full_path, "r") as f:
        content = f.read()
    
    # Analisar script
    analysis = {
        "script_name": os.path.basename(script_path),
        "script_path": script_path,
        "script_type": script_type,
        "size_bytes": os.path.getsize(full_path),
        "last_modified": datetime.fromtimestamp(os.path.getmtime(full_path)).isoformat(),
        "is_executable": os.access(full_path, os.X_OK)
    }
    
    # Análise específica por tipo
    if script_type == "bash":
        # Analisar funções em scripts bash
        functions = []
        current_function = None
        
        for line in content.split("\n"):
            if line.strip().startswith("function ") or ("()" in line and "{" in line):
                if current_function:
                    functions.append(current_function)
                
                function_name = line.strip().replace("function ", "").replace("() {", "").strip()
                current_function = {
                    "name": function_name,
                    "description": ""
                }
            elif current_function and line.strip().startswith("#"):
                current_function["description"] += line.strip()[1:].strip() + " "
        
        if current_function:
            functions.append(current_function)
        
        analysis["functions"] = functions
    elif script_type == "python":
        # Analisar funções/classes em scripts Python
        functions = []
        classes = []
        imports = []
        
        current_item = None
        
        for line in content.split("\n"):
            line = line.strip()
            
            if line.startswith("import ") or line.startswith("from "):
                imports.append(line)
            elif line.startswith("def "):
                if current_item:
                    if "class" in current_item:
                        classes.append(current_item)
                    else:
                        functions.append(current_item)
                
                function_name = line.replace("def ", "").split("(")[0].strip()
                current_item = {
                    "type": "function",
                    "name": function_name,
                    "description": ""
                }
            elif line.startswith("class "):
                if current_item:
                    if "class" in current_item:
                        classes.append(current_item)
                    else:
                        functions.append(current_item)
                
                class_name = line.replace("class ", "").split("(")[0].replace(":", "").strip()
                current_item = {
                    "type": "class",
                    "name": class_name,
                    "description": ""
                }
            elif current_item and line.startswith('"""') or line.startswith("'''"):
                # Início da docstring
                if "description" in current_item and not current_item["description"]:
                    docstring_line = line.strip()[3:]
                    if docstring_line:
                        current_item["description"] += docstring_line + " "
        
        if current_item:
            if "class" in current_item:
                classes.append(current_item)
            else:
                functions.append(current_item)
        
        analysis["imports"] = imports
        analysis["functions"] = functions
        analysis["classes"] = classes
    
    # Salvar análise
    analysis_path = os.path.join(ANALYSIS_DIR, f"{os.path.basename(script_path)}_analysis.json")
    with open(analysis_path, "w") as f:
        json.dump(analysis, f, indent=2)
    
    return json.dumps(analysis, indent=2)

@mcp.tool()
def project_architecture() -> str:
    """
    Analisa a arquitetura geral do projeto Continuity
    """
    architecture = {
        "project_name": "Continuity Protocol",
        "analysis_date": datetime.now().isoformat(),
        "components": {
            "servers": [],
            "scripts": {
                "core": [],
                "utilities": [],
                "emergency": []
            },
            "protocols": []
        },
        "workflows": [],
        "dependencies": []
    }
    
    # Analisar servidores
    result = subprocess.run(
        ["find", BASE_DIR, "-name", "*server*.py"],
        capture_output=True,
        text=True
    )
    
    servers = result.stdout.strip().split("\n")
    for server in servers:
        if server:
            server_name = os.path.basename(server)
            # Ler primeiras linhas para obter descrição
            with open(server, "r") as f:
                content = f.read(1000)  # Primeiros 1000 caracteres
                description = ""
                for line in content.split("\n"):
                    if line.strip().startswith('"""') or line.strip().startswith("'''"):
                        description = line.strip()[3:].strip()
                        break
            
            architecture["components"]["servers"].append({
                "name": server_name,
                "path": server.replace(BASE_DIR + "/", ""),
                "description": description
            })
    
    # Analisar scripts core
    core_patterns = ["continuity", "recovery", "autonomous", "session"]
    for pattern in core_patterns:
        result = subprocess.run(
            ["find", BASE_DIR, "-name", f"*{pattern}*.sh"],
            capture_output=True,
            text=True
        )
        
        scripts = result.stdout.strip().split("\n")
        for script in scripts:
            if script and script not in architecture["components"]["scripts"]["core"]:
                script_name = os.path.basename(script)
                architecture["components"]["scripts"]["core"].append({
                    "name": script_name,
                    "path": script.replace(BASE_DIR + "/", "")
                })
    
    # Analisar scripts de emergência
    result = subprocess.run(
        ["find", BASE_DIR, "-name", "*emergency*.sh"],
        capture_output=True,
        text=True
    )
    
    scripts = result.stdout.strip().split("\n")
    for script in scripts:
        if script:
            script_name = os.path.basename(script)
            architecture["components"]["scripts"]["emergency"].append({
                "name": script_name,
                "path": script.replace(BASE_DIR + "/", "")
            })
    
    # Analisar protocolos
    result = subprocess.run(
        ["find", BASE_DIR, "-name", "*PROTOCOL*.md"],
        capture_output=True,
        text=True
    )
    
    protocols = result.stdout.strip().split("\n")
    for protocol in protocols:
        if protocol:
            protocol_name = os.path.basename(protocol)
            architecture["components"]["protocols"].append({
                "name": protocol_name,
                "path": protocol.replace(BASE_DIR + "/", "")
            })
    
    # Analisar fluxos de trabalho
    workflow_scripts = []
    for script_list in architecture["components"]["scripts"].values():
        workflow_scripts.extend([script["path"] for script in script_list])
    
    for script_path in workflow_scripts:
        full_path = os.path.join(BASE_DIR, script_path)
        if os.path.exists(full_path):
            with open(full_path, "r") as f:
                content = f.read()
                
                # Identificar outros scripts chamados
                called_scripts = []
                for line in content.split("\n"):
                    for other_script in workflow_scripts:
                        script_name = os.path.basename(other_script)
                        if script_name in line and script_name != os.path.basename(script_path):
                            if script_name not in called_scripts:
                                called_scripts.append(script_name)
                
                if called_scripts:
                    architecture["workflows"].append({
                        "script": os.path.basename(script_path),
                        "calls": called_scripts
                    })
    
    # Salvar arquitetura
    architecture_path = os.path.join(ANALYSIS_DIR, "project_architecture.json")
    with open(architecture_path, "w") as f:
        json.dump(architecture, f, indent=2)
    
    return json.dumps(architecture, indent=2)

@mcp.tool()
def project_refactor_plan() -> str:
    """
    Gera um plano de refatoração para o projeto Continuity
    """
    # Primeiro, analisar a arquitetura
    architecture_result = project_architecture()
    architecture = json.loads(architecture_result)
    
    # Identificar problemas e oportunidades
    issues = []
    opportunities = []
    
    # Analisar servidores
    if len(architecture["components"]["servers"]) > 1:
        issues.append({
            "type": "duplication",
            "component": "servers",
            "description": f"Múltiplos servidores MCP ({len(architecture['components']['servers'])}) fazendo funções similares",
            "impact": "high",
            "solution": "Unificar servidores em uma única implementação coesa"
        })
    
    # Analisar scripts de emergência
    emergency_scripts = architecture["components"]["scripts"]["emergency"]
    if len(emergency_scripts) > 3:
        issues.append({
            "type": "fragmentation",
            "component": "emergency_scripts",
            "description": f"Sistema de emergência fragmentado em {len(emergency_scripts)} scripts",
            "impact": "medium",
            "solution": "Consolidar em um único sistema de emergência modular"
        })
    
    # Identificar oportunidades
    if os.path.exists(os.path.join(BASE_DIR, "PROJECT_CONTINUITY_PROTOCOL.md")):
        opportunities.append({
            "type": "protocol_implementation",
            "description": "Implementar o Protocolo de Continuidade de Projetos completo",
            "benefit": "Permite persistência de contexto entre sessões e comunicação entre agentes",
            "priority": "high"
        })
    
    # Gerar plano de refatoração
    refactor_plan = {
        "project_name": "Continuity Protocol",
        "refactor_date": datetime.now().isoformat(),
        "issues": issues,
        "opportunities": opportunities,
        "plan": {
            "phase1": {
                "name": "Consolidação",
                "description": "Consolidar componentes duplicados e fragmentados",
                "tasks": [
                    "Unificar servidores MCP",
                    "Consolidar scripts de emergência",
                    "Limpar backup desnecessários"
                ]
            },
            "phase2": {
                "name": "Implementação de Protocolo",
                "description": "Implementar o Protocolo de Continuidade de Projetos",
                "tasks": [
                    "Implementar Project Cards",
                    "Implementar Context Store",
                    "Implementar Session Management"
                ]
            },
            "phase3": {
                "name": "Integração e Testes",
                "description": "Integrar todos os componentes e testar",
                "tasks": [
                    "Integrar com Claude Desktop",
                    "Testar persistência de contexto",
                    "Testar comunicação entre agentes"
                ]
            }
        }
    }
    
    # Salvar plano
    plan_path = os.path.join(ANALYSIS_DIR, "refactor_plan.json")
    with open(plan_path, "w") as f:
        json.dump(refactor_plan, f, indent=2)
    
    return json.dumps(refactor_plan, indent=2)

@mcp.tool()
def project_summary() -> str:
    """
    Gera um resumo do projeto Continuity
    """
    # Primeiro, analisar a arquitetura
    architecture_result = project_architecture()
    architecture = json.loads(architecture_result)
    
    # Gerar resumo
    summary = {
        "project_name": "Continuity Protocol",
        "summary_date": datetime.now().isoformat(),
        "overview": {
            "description": "O Continuity Protocol é uma implementação cibernética do Model Context Protocol (MCP) projetada para manter o contexto entre diferentes LLMs (Large Language Models) e ambientes de desenvolvimento.",
            "key_components": {
                "servers": len(architecture["components"]["servers"]),
                "core_scripts": len(architecture["components"]["scripts"]["core"]),
                "emergency_scripts": len(architecture["components"]["scripts"]["emergency"]),
                "protocols": len(architecture["components"]["protocols"])
            }
        },
        "strengths": [
            "Sistema robusto de backup e recuperação",
            "Integração com Claude Desktop",
            "Conceito inovador de continuidade entre sessões"
        ],
        "weaknesses": [
            "Multiplicidade de servidores causando confusão",
            "Fragmentação de funcionalidades",
            "Complexidade de uso"
        ],
        "opportunities": [
            "Implementação do Protocolo de Continuidade de Projetos",
            "Integração com outros LLMs",
            "Desenvolvimento de uma interface web"
        ],
        "next_steps": [
            "Consolidar servidores",
            "Implementar protocolo completo",
            "Desenvolver documentação abrangente"
        ]
    }
    
    # Salvar resumo
    summary_path = os.path.join(ANALYSIS_DIR, "project_summary.json")
    with open(summary_path, "w") as f:
        json.dump(summary, f, indent=2)
    
    return json.dumps(summary, indent=2)

# Ponto de entrada
if __name__ == "__main__":
    print("Simple Project Analyzer - Analisando o projeto Continuity")
    print(f"Análises serão salvas em: {ANALYSIS_DIR}")
    
    # Salvar PID
    pid_file = os.path.join(BASE_DIR, "analyzer.pid")
    with open(pid_file, "w") as f:
        f.write(str(os.getpid()))
    
    # Executar servidor MCP
    mcp.run()