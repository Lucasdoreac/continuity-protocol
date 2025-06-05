# 🤖 Plano de Agentificação - Hub Local MCP (Fase A)

## 🎯 **PRIORIZAÇÃO DE SCRIPTS PARA AGENTIFICAR**

### **🔥 PRIORIDADE 1 - Agentes Core (Semana 1-2)**

#### **1.1 Session Agent** 
```python
# Base: auto-continuity.sh + magic-system.sh
class SessionAgent:
    """Gerencia ciclo de vida das sessões do Lucas"""
    
    @mcp_tool
    async def start_session(self, project_name: str) -> dict:
        """Iniciar nova sessão de trabalho"""
        session_id = f"lucas-{project_name}-{timestamp}"
        session_data = {
            "user_id": "lucas-cardoso",
            "project": project_name,
            "started_at": datetime.now(),
            "context": await self.capture_initial_context()
        }
        await self.orchestrator.save_session(session_id, session_data)
        return {"session_id": session_id, "status": "started"}
    
    @mcp_tool 
    async def end_session(self, session_id: str) -> dict:
        """Finalizar sessão com backup automático"""
        await self.backup_agent.create_backup(session_id)
        await self.orchestrator.archive_session(session_id)
        return {"status": "ended", "backup_created": True}
```

#### **1.2 Recovery Agent**
```python
# Base: autonomous-recovery.sh + recovery.sh
class RecoveryAgent:
    """Detecta e recupera contexto de sessões interrompidas"""
    
    @mcp_tool
    async def detect_recovery_needed(self) -> dict:
        """Detectar se há recuperação pendente"""
        orphaned_files = await self.scan_orphaned_files()
        interrupted_sessions = await self.scan_interrupted_sessions()
        critical_missions = await self.scan_critical_missions()
        
        return {
            "needs_recovery": len(orphaned_files) > 0 or len(interrupted_sessions) > 0,
            "orphaned_files": orphaned_files,
            "interrupted_sessions": interrupted_sessions,
            "critical_missions": critical_missions
        }
    
    @mcp_tool
    async def auto_recover(self, session_id: str = None) -> dict:
        """Executar recuperação automática"""
        if session_id:
            return await self.recover_specific_session(session_id)
        else:
            return await self.recover_latest_session()
```

#### **1.3 Guard Agent**
```python  
# Base: mcp-guard.sh + mcp-self-monitor.sh
class GuardAgent:
    """Monitora segurança e integridade das operações MCP"""
    
    @mcp_tool
    async def validate_mcp_action(self, action: str, target: str, context: str) -> dict:
        """Validar ação MCP antes da execução"""
        risk_score = await self.calculate_risk_score(action, target, context)
        
        if risk_score > 100:
            return {
                "approved": False,
                "risk_score": risk_score,
                "reason": "High risk action detected",
                "alternative": await self.suggest_safer_alternative(action)
            }
        
        return {"approved": True, "risk_score": risk_score}
    
    @mcp_tool
    async def monitor_mcp_health(self) -> dict:
        """Monitorar saúde dos serviços MCP"""
        return {
            "desktop_commander": await self.check_service_health("desktop-commander"),
            "memory_server": await self.check_service_health("memory-server"),
            "applescript": await self.check_service_health("applescript")
        }
```

### **⚡ PRIORIDADE 2 - Agentes Especializados (Semana 3-4)**

#### **2.1 Project Manager Agent**
```python
# Base: funcionalidades de project switching
class ProjectManagerAgent:
    """Gerencia projetos do Lucas (luaraujo, premium-hub, continuity)"""
    
    @mcp_tool
    async def switch_project(self, project_name: str) -> dict:
        """Alternar contexto para projeto específico"""
        project_context = await self.load_project_context(project_name)
        await self.session_agent.update_current_context(project_context)
        
        return {
            "active_project": project_name,
            "context_loaded": True,
            "last_session": project_context.get("last_session"),
            "pending_tasks": project_context.get("pending_tasks", [])
        }
    
    @mcp_tool
    async def get_project_status(self, project_name: str = None) -> dict:
        """Obter status detalhado do projeto"""
        if not project_name:
            # Retornar status de todos os projetos
            return {
                "luaraujo": await self.get_single_project_status("luaraujo"),
                "premium-hub": await self.get_single_project_status("premium-hub"), 
                "continuity": await self.get_single_project_status("continuity")
            }
        
        return await self.get_single_project_status(project_name)
```

#### **2.2 Input Registrator Agent**
```python
# Base: input-preservator.sh + input-preservation.log
class InputRegistratorAgent:
    """Registra e preserva inputs importantes do Lucas"""
    
    @mcp_tool
    async def register_input(self, user_input: str, session_id: str, metadata: dict = None) -> dict:
        """Registrar input do usuário com contexto"""
        input_record = {
            "input": user_input,
            "session_id": session_id,
            "timestamp": datetime.now(),
            "metadata": metadata or {},
            "context_snapshot": await self.capture_context_snapshot(),
            "classification": await self.classify_input(user_input)
        }
        
        await self.orchestrator.save_input_record(input_record)
        
        # Decidir se precisa preservar para continuidade
        if input_record["classification"]["substantive"]:
            await self.session_agent.update_session_context(session_id, input_record)
        
        return {"registered": True, "preserved": input_record["classification"]["substantive"]}
    
    async def classify_input(self, user_input: str) -> dict:
        """Classificar input como substantivo, pergunta simples, etc."""
        # Lógica baseada no magic-system.sh
        if any(phrase in user_input.lower() for phrase in ["onde paramos", "continue", "status"]):
            return {"type": "continuity_query", "substantive": False}
        elif len(user_input) > 50 and any(word in user_input.lower() for word in ["implementar", "criar", "desenvolver"]):
            return {"type": "development_request", "substantive": True}
        else:
            return {"type": "general_query", "substantive": len(user_input) > 20}
```

### **🔄 PRIORIDADE 3 - Agentes de Monitoramento (Semana 5-6)**

#### **3.1 Monitor Agent**
```python
# Base: monitor.sh + system monitoring scripts
class MonitorAgent:
    """Monitora estado do sistema e ferramentas MCP"""
    
    @mcp_tool
    async def get_system_status(self) -> dict:
        """Status completo do sistema do Lucas"""
        return {
            "active_processes": await self.get_active_processes(),
            "mcp_services": await self.guard_agent.monitor_mcp_health(),
            "disk_space": await self.get_disk_space(),
            "memory_usage": await self.get_memory_usage(),
            "project_states": await self.project_manager.get_all_project_status()
        }
    
    @mcp_tool
    async def monitor_continuous(self, interval_seconds: int = 60) -> dict:
        """Iniciar monitoramento contínuo"""
        # Iniciar background task de monitoramento
        task_id = await self.start_monitoring_task(interval_seconds)
        return {"monitoring_started": True, "task_id": task_id}
```

## 🔌 **INTEGRAÇÃO COM SERVIDOR MCP DE ORQUESTRAÇÃO**

### **Arquitetura de Comunicação**
```python
# orchestrator_server.py - Servidor MCP de Orquestração
from fastmcp import FastMCP

class OrchestrationServer:
    def __init__(self):
        self.mcp_server = FastMCP("Lucas-Continuity-Hub")
        self.db = SQLiteDB("lucas_continuity.db")
        self.agents = {
            "session": SessionAgent(self),
            "recovery": RecoveryAgent(self),
            "guard": GuardAgent(self),
            "project_manager": ProjectManagerAgent(self),
            "input_registrator": InputRegistratorAgent(self),
            "monitor": MonitorAgent(self)
        }
        self.register_all_agent_tools()
    
    def register_all_agent_tools(self):
        """Registrar todas as ferramentas dos agentes no servidor MCP"""
        for agent_name, agent in self.agents.items():
            for tool_name, tool_func in agent.get_mcp_tools():
                self.mcp_server.register_tool(f"{agent_name}_{tool_name}", tool_func)
    
    async def save_session(self, session_id: str, session_data: dict):
        """Salvar dados de sessão no SQLite"""
        await self.db.execute(
            "INSERT INTO sessions (id, data, created_at) VALUES (?, ?, ?)",
            (session_id, json.dumps(session_data), datetime.now())
        )
    
    async def load_session(self, session_id: str) -> dict:
        """Carregar dados de sessão do SQLite"""
        result = await self.db.fetchone(
            "SELECT data FROM sessions WHERE id = ?", (session_id,)
        )
        return json.loads(result["data"]) if result else None
```

## 🎯 **ESTRATÉGIA DE DESENVOLVIMENTO INCREMENTAL**

### **Fase A.1 (Semanas 1-2): Core Agents**
- SessionAgent + RecoveryAgent + GuardAgent
- Servidor MCP de Orquestração básico
- SQLite setup
- Testes com scripts existentes

### **Fase A.2 (Semanas 3-4): Specialized Agents** 
- ProjectManagerAgent + InputRegistratorAgent
- Integração com projetos reais do Lucas
- Dashboard Streamlit básico

### **Fase A.3 (Semanas 5-6): Monitoring & Polish**
- MonitorAgent + logging completo
- Dashboard Streamlit avançado
- Integração GitHub para Jules
- Testes completos
