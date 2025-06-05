#!/usr/bin/env python3
"""
MCP Query Language (MQL)
Linguagem de consulta específica para o Continuity Protocol
"""

import re
from typing import Dict, Any, List, Optional, Union, Callable
from datetime import datetime, timedelta

class MCPQueryParser:
    """
    Parser para MCP Query Language (MQL)
    """
    
    def __init__(self):
        """Inicializa o parser MQL"""
        # Definir gramática simplificada
        self.keywords = {
            "FIND": self._parse_find,
            "WHERE": self._parse_where,
            "CONTEXT": self._parse_context,
            "IN": None,  # Tratado especialmente
            "PRIORITIZE": self._parse_prioritize
        }
        
        self.operators = ["=", "CONTAINS", "IN", "AND", "OR", ">", "<", ">=", "<="]
        
        # Expressões regulares para tokenização
        self.token_pattern = re.compile(
            r'([A-Z_]+(?=\s|$))|'  # Palavras-chave e identificadores
            r'("(?:\\.|[^"])*")|'  # Strings com aspas duplas
            r'(\'(?:\\.|[^\'])*\')|'  # Strings com aspas simples
            r'([=><]=?|,)|'  # Operadores
            r'(\(|\))|'  # Parênteses
            r'([^\s,()=><]+)'  # Outros tokens
        )
    
    def parse(self, query_string: str) -> Dict[str, Any]:
        """
        Parseia uma consulta MQL
        
        Args:
            query_string: String de consulta MQL
            
        Returns:
            Dict: AST da consulta
        """
        try:
            # Tokenizar consulta
            tokens = self._tokenize(query_string)
            
            # Determinar tipo de consulta
            if not tokens:
                raise ValueError("Consulta vazia")
            
            if tokens[0] == "FIND":
                return self._parse_find_query(tokens)
            elif tokens[0] == "WHERE":
                return self._parse_where_query(tokens)
            elif tokens[0] == "CONTEXT":
                return self._parse_context_query(tokens)
            else:
                raise ValueError(f"Tipo de consulta desconhecido: {tokens[0]}")
        except Exception as e:
            return {
                "error": f"Erro ao parsear consulta: {str(e)}",
                "query": query_string
            }
    
    def _tokenize(self, query_string: str) -> List[str]:
        """
        Tokeniza uma string de consulta
        
        Args:
            query_string: String de consulta
            
        Returns:
            List[str]: Lista de tokens
        """
        tokens = []
        for match in self.token_pattern.finditer(query_string):
            token = match.group(0)
            if token.strip():  # Ignorar espaços em branco
                tokens.append(token)
        
        return tokens
    
    def _parse_find_query(self, tokens: List[str]) -> Dict[str, Any]:
        """
        Parseia uma consulta FIND
        
        Args:
            tokens: Lista de tokens
            
        Returns:
            Dict: AST da consulta
        """
        # Verificar formato básico
        if len(tokens) < 4 or tokens[0] != "FIND" or tokens[2] != "IN":
            raise ValueError("Formato inválido para consulta FIND")
        
        # Extrair valor e escopo
        value = self._parse_value(tokens[1])
        scope = tokens[3]
        
        # Inicializar resultado
        result = {
            "type": "find",
            "value": value,
            "scope": scope
        }
        
        # Processar cláusulas adicionais
        i = 4
        while i < len(tokens):
            if tokens[i] == "WHERE":
                where_clause, i = self._parse_where_clause(tokens, i)
                result["condition"] = where_clause
            elif tokens[i] == "CONTEXT":
                context_clause, i = self._parse_context_clause(tokens, i)
                result["context"] = context_clause
            elif tokens[i] == "PRIORITIZE":
                priority_clause, i = self._parse_priority_clause(tokens, i)
                result["priority"] = priority_clause
            else:
                i += 1
        
        return result
    
    def _parse_where_query(self, tokens: List[str]) -> Dict[str, Any]:
        """
        Parseia uma consulta WHERE
        
        Args:
            tokens: Lista de tokens
            
        Returns:
            Dict: AST da consulta
        """
        # Verificar formato básico
        if len(tokens) < 4 or tokens[0] != "WHERE":
            raise ValueError("Formato inválido para consulta WHERE")
        
        # Encontrar índice de IN
        in_index = -1
        for i, token in enumerate(tokens):
            if token == "IN" and i > 1:
                in_index = i
                break
        
        if in_index == -1:
            raise ValueError("Cláusula IN não encontrada em consulta WHERE")
        
        # Extrair condição e escopo
        condition_tokens = tokens[1:in_index]
        condition = self._parse_condition(condition_tokens)
        scope = tokens[in_index + 1]
        
        # Inicializar resultado
        result = {
            "type": "where",
            "condition": condition,
            "scope": scope
        }
        
        # Processar cláusulas adicionais
        i = in_index + 2
        while i < len(tokens):
            if tokens[i] == "CONTEXT":
                context_clause, i = self._parse_context_clause(tokens, i)
                result["context"] = context_clause
            elif tokens[i] == "PRIORITIZE":
                priority_clause, i = self._parse_priority_clause(tokens, i)
                result["priority"] = priority_clause
            else:
                i += 1
        
        return result
    
    def _parse_context_query(self, tokens: List[str]) -> Dict[str, Any]:
        """
        Parseia uma consulta CONTEXT
        
        Args:
            tokens: Lista de tokens
            
        Returns:
            Dict: AST da consulta
        """
        # Verificar formato básico
        if len(tokens) < 2 or tokens[0] != "CONTEXT":
            raise ValueError("Formato inválido para consulta CONTEXT")
        
        # Extrair escopo
        scope = tokens[1]
        
        # Inicializar resultado
        result = {
            "type": "context",
            "scope": scope
        }
        
        # Processar cláusulas adicionais
        i = 2
        while i < len(tokens):
            if tokens[i] == "WHERE":
                where_clause, i = self._parse_where_clause(tokens, i)
                result["condition"] = where_clause
            elif tokens[i] == "PRIORITIZE":
                priority_clause, i = self._parse_priority_clause(tokens, i)
                result["priority"] = priority_clause
            else:
                i += 1
        
        return result
    
    def _parse_where_clause(self, tokens: List[str], start_index: int) -> Tuple[Dict[str, Any], int]:
        """
        Parseia uma cláusula WHERE
        
        Args:
            tokens: Lista de tokens
            start_index: Índice inicial
            
        Returns:
            Tuple[Dict, int]: Cláusula WHERE e próximo índice
        """
        if start_index >= len(tokens) or tokens[start_index] != "WHERE":
            raise ValueError("Cláusula WHERE esperada")
        
        # Encontrar fim da cláusula
        end_index = start_index + 1
        while end_index < len(tokens) and tokens[end_index] not in ["CONTEXT", "PRIORITIZE"]:
            end_index += 1
        
        # Parsear condição
        condition_tokens = tokens[start_index + 1:end_index]
        condition = self._parse_condition(condition_tokens)
        
        return condition, end_index
    
    def _parse_context_clause(self, tokens: List[str], start_index: int) -> Tuple[str, int]:
        """
        Parseia uma cláusula CONTEXT
        
        Args:
            tokens: Lista de tokens
            start_index: Índice inicial
            
        Returns:
            Tuple[str, int]: Cláusula CONTEXT e próximo índice
        """
        if start_index >= len(tokens) or tokens[start_index] != "CONTEXT":
            raise ValueError("Cláusula CONTEXT esperada")
        
        # Verificar se há token de contexto
        if start_index + 1 >= len(tokens):
            raise ValueError("Especificação de contexto esperada após CONTEXT")
        
        context_spec = tokens[start_index + 1]
        
        return context_spec, start_index + 2
    
    def _parse_priority_clause(self, tokens: List[str], start_index: int) -> Tuple[List[str], int]:
        """
        Parseia uma cláusula PRIORITIZE
        
        Args:
            tokens: Lista de tokens
            start_index: Índice inicial
            
        Returns:
            Tuple[List[str], int]: Cláusula PRIORITIZE e próximo índice
        """
        if start_index >= len(tokens) or tokens[start_index] != "PRIORITIZE":
            raise ValueError("Cláusula PRIORITIZE esperada")
        
        # Coletar prioridades
        priorities = []
        i = start_index + 1
        
        while i < len(tokens) and tokens[i] not in self.keywords:
            if tokens[i] == ",":
                i += 1
                continue
            
            priorities.append(tokens[i])
            i += 1
        
        if not priorities:
            raise ValueError("Pelo menos uma prioridade esperada após PRIORITIZE")
        
        return priorities, i
    
    def _parse_condition(self, tokens: List[str]) -> Dict[str, Any]:
        """
        Parseia uma condição
        
        Args:
            tokens: Lista de tokens
            
        Returns:
            Dict: Condição parseada
        """
        if not tokens:
            raise ValueError("Condição vazia")
        
        # Verificar operadores lógicos (AND, OR)
        for op in ["AND", "OR"]:
            if op in tokens:
                idx = tokens.index(op)
                left = self._parse_condition(tokens[:idx])
                right = self._parse_condition(tokens[idx + 1:])
                
                return {
                    "type": "logical",
                    "operator": op,
                    "left": left,
                    "right": right
                }
        
        # Condição simples (campo operador valor)
        if len(tokens) < 3:
            raise ValueError(f"Condição inválida: {' '.join(tokens)}")
        
        field = tokens[0]
        
        # Determinar operador
        op_idx = -1
        for i, token in enumerate(tokens):
            if token in self.operators:
                op_idx = i
                break
        
        if op_idx == -1:
            raise ValueError(f"Operador não encontrado em condição: {' '.join(tokens)}")
        
        operator = tokens[op_idx]
        
        # Parsear valor
        if operator == "IN":
            # Formato: campo IN (valor1, valor2, ...)
            if op_idx + 1 >= len(tokens) or tokens[op_idx + 1] != "(":
                raise ValueError("Parêntese de abertura esperado após IN")
            
            # Encontrar parêntese de fechamento
            close_idx = -1
            for i in range(op_idx + 2, len(tokens)):
                if tokens[i] == ")":
                    close_idx = i
                    break
            
            if close_idx == -1:
                raise ValueError("Parêntese de fechamento não encontrado")
            
            # Extrair valores
            values = []
            i = op_idx + 2
            while i < close_idx:
                if tokens[i] == ",":
                    i += 1
                    continue
                
                values.append(self._parse_value(tokens[i]))
                i += 1
            
            return {
                "type": "comparison",
                "field": field,
                "operator": operator,
                "value": values
            }
        else:
            # Formato: campo operador valor
            value = self._parse_value(tokens[op_idx + 1])
            
            return {
                "type": "comparison",
                "field": field,
                "operator": operator,
                "value": value
            }
    
    def _parse_value(self, token: str) -> Union[str, int, float, bool]:
        """
        Parseia um valor
        
        Args:
            token: Token a ser parseado
            
        Returns:
            Union[str, int, float, bool]: Valor parseado
        """
        # Remover aspas de strings
        if (token.startswith('"') and token.endswith('"')) or (token.startswith("'") and token.endswith("'")):
            return token[1:-1]
        
        # Tentar converter para número
        try:
            if "." in token:
                return float(token)
            else:
                return int(token)
        except ValueError:
            pass
        
        # Verificar booleanos
        if token.lower() == "true":
            return True
        elif token.lower() == "false":
            return False
        
        # Retornar como string
        return token
    
    def _parse_find(self, tokens: List[str], start_index: int) -> Tuple[Dict[str, Any], int]:
        """Implementação futura"""
        pass
    
    def _parse_where(self, tokens: List[str], start_index: int) -> Tuple[Dict[str, Any], int]:
        """Implementação futura"""
        pass
    
    def _parse_context(self, tokens: List[str], start_index: int) -> Tuple[str, int]:
        """Implementação futura"""
        pass
    
    def _parse_prioritize(self, tokens: List[str], start_index: int) -> Tuple[List[str], int]:
        """Implementação futura"""
        pass

class MCPQueryExecutor:
    """
    Executor para MCP Query Language (MQL)
    """
    
    def __init__(self, context_storage=None, project_manager=None, session_manager=None):
        """
        Inicializa o executor MQL
        
        Args:
            context_storage: Armazenamento de contexto
            project_manager: Gerenciador de projetos
            session_manager: Gerenciador de sessões
        """
        self.context_storage = context_storage
        self.project_manager = project_manager
        self.session_manager = session_manager
        self.parser = MCPQueryParser()
    
    def execute(self, query_string: str) -> Dict[str, Any]:
        """
        Executa uma consulta MQL
        
        Args:
            query_string: String de consulta MQL
            
        Returns:
            Dict: Resultado da consulta
        """
        try:
            # Parsear consulta
            query_ast = self.parser.parse(query_string)
            
            # Verificar erro de parsing
            if "error" in query_ast:
                return query_ast
            
            # Executar consulta
            query_type = query_ast["type"]
            
            if query_type == "find":
                return self._execute_find(query_ast)
            elif query_type == "where":
                return self._execute_where(query_ast)
            elif query_type == "context":
                return self._execute_context(query_ast)
            else:
                return {
                    "error": f"Tipo de consulta desconhecido: {query_type}",
                    "query": query_string
                }
        except Exception as e:
            return {
                "error": f"Erro ao executar consulta: {str(e)}",
                "query": query_string
            }
    
    def _execute_find(self, query: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executa uma consulta FIND
        
        Args:
            query: AST da consulta
            
        Returns:
            Dict: Resultado da consulta
        """
        # Verificar dependências
        if not self.context_storage:
            return {
                "error": "Armazenamento de contexto não disponível",
                "query_type": "find"
            }
        
        # Extrair parâmetros
        value = query["value"]
        scope = query["scope"]
        
        # Resolver escopo
        projects = self._resolve_scope(scope)
        
        # Aplicar condição se existir
        if "condition" in query:
            projects = self._filter_projects(projects, query["condition"])
        
        # Recuperar contexto
        context_spec = query.get("context", "LAST_SESSION")
        context = self._retrieve_context(projects, context_spec)
        
        # Pesquisar valor
        results = []
        for project_id, project_context in context.items():
            project_results = self._search_value(value, project_context)
            if project_results:
                results.append({
                    "project_id": project_id,
                    "results": project_results
                })
        
        # Aplicar priorização
        if "priority" in query:
            results = self._apply_priority(results, query["priority"])
        
        return {
            "query_type": "find",
            "value": value,
            "scope": scope,
            "projects_searched": len(projects),
            "results": results
        }
    
    def _execute_where(self, query: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executa uma consulta WHERE
        
        Args:
            query: AST da consulta
            
        Returns:
            Dict: Resultado da consulta
        """
        # Verificar dependências
        if not self.project_manager:
            return {
                "error": "Gerenciador de projetos não disponível",
                "query_type": "where"
            }
        
        # Extrair parâmetros
        condition = query["condition"]
        scope = query["scope"]
        
        # Resolver escopo
        projects = self._resolve_scope(scope)
        
        # Filtrar projetos
        filtered_projects = self._filter_projects(projects, condition)
        
        # Recuperar contexto se necessário
        results = filtered_projects
        if "context" in query:
            context_spec = query["context"]
            context = self._retrieve_context(filtered_projects, context_spec)
            
            # Formatar resultados com contexto
            results = []
            for project_id, project_context in context.items():
                results.append({
                    "project_id": project_id,
                    "context": project_context
                })
        
        # Aplicar priorização
        if "priority" in query:
            results = self._apply_priority(results, query["priority"])
        
        return {
            "query_type": "where",
            "scope": scope,
            "projects_searched": len(projects),
            "projects_matched": len(filtered_projects),
            "results": results
        }
    
    def _execute_context(self, query: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executa uma consulta CONTEXT
        
        Args:
            query: AST da consulta
            
        Returns:
            Dict: Resultado da consulta
        """
        # Verificar dependências
        if not self.project_manager:
            return {
                "error": "Gerenciador de projetos não disponível",
                "query_type": "context"
            }
        
        # Extrair parâmetros
        scope = query["scope"]
        
        # Resolver escopo
        projects = self._resolve_scope(scope)
        
        # Filtrar projetos se houver condição
        if "condition" in query:
            projects = self._filter_projects(projects, query["condition"])
        
        # Recuperar contexto completo
        context = {}
        for project_id in projects:
            if self.project_manager:
                project = self.project_manager.get_project(project_id)
                context[project_id] = project
        
        # Aplicar priorização
        results = list(context.items())
        if "priority" in query:
            results = self._apply_priority(results, query["priority"])
        
        return {
            "query_type": "context",
            "scope": scope,
            "projects_matched": len(projects),
            "results": results
        }
    
    def _resolve_scope(self, scope: str) -> List[str]:
        """
        Resolve escopo para lista de IDs de projeto
        
        Args:
            scope: Escopo da consulta
            
        Returns:
            List[str]: Lista de IDs de projeto
        """
        if not self.project_manager:
            return []
        
        if scope == "CURRENT_PROJECT":
            # Obter projeto atual da sessão ativa
            if self.session_manager:
                active_sessions = self.session_manager.get_all_sessions()
                if active_sessions:
                    # Usar o projeto da sessão mais recente
                    latest_session = active_sessions[0]
                    current_project = latest_session.get("current_project")
                    if current_project:
                        return [current_project]
            
            return []
        elif scope == "ALL_PROJECTS":
            # Obter todos os projetos
            all_projects = self.project_manager.get_all_projects()
            return [p["id"] for p in all_projects]
        else:
            # Escopo é um nome de projeto específico
            project = self.project_manager.get_project(scope)
            return [project["id"]]
    
    def _filter_projects(self, project_ids: List[str], condition: Dict[str, Any]) -> List[str]:
        """
        Filtra projetos com base em condição
        
        Args:
            project_ids: Lista de IDs de projeto
            condition: Condição de filtro
            
        Returns:
            List[str]: Lista filtrada de IDs de projeto
        """
        if not self.project_manager:
            return []
        
        filtered_ids = []
        
        for project_id in project_ids:
            project = self.project_manager.get_project(project_id)
            
            if self._evaluate_condition(project, condition):
                filtered_ids.append(project_id)
        
        return filtered_ids
    
    def _evaluate_condition(self, project: Dict[str, Any], condition: Dict[str, Any]) -> bool:
        """
        Avalia condição para um projeto
        
        Args:
            project: Dados do projeto
            condition: Condição a avaliar
            
        Returns:
            bool: True se condição for satisfeita, False caso contrário
        """
        condition_type = condition["type"]
        
        if condition_type == "logical":
            operator = condition["operator"]
            left = self._evaluate_condition(project, condition["left"])
            right = self._evaluate_condition(project, condition["right"])
            
            if operator == "AND":
                return left and right
            elif operator == "OR":
                return left or right
            else:
                return False
        elif condition_type == "comparison":
            field = condition["field"]
            operator = condition["operator"]
            value = condition["value"]
            
            # Obter valor do campo
            field_value = self._get_field_value(project, field)
            
            # Avaliar operador
            if operator == "=":
                return field_value == value
            elif operator == "CONTAINS":
                if isinstance(field_value, str) and isinstance(value, str):
                    return value in field_value
                elif isinstance(field_value, list):
                    return value in field_value
                else:
                    return False
            elif operator == "IN":
                return field_value in value
            elif operator == ">":
                return field_value > value
            elif operator == "<":
                return field_value < value
            elif operator == ">=":
                return field_value >= value
            elif operator == "<=":
                return field_value <= value
            else:
                return False
        else:
            return False
    
    def _get_field_value(self, project: Dict[str, Any], field: str) -> Any:
        """
        Obtém valor de um campo do projeto
        
        Args:
            project: Dados do projeto
            field: Nome do campo
            
        Returns:
            Any: Valor do campo
        """
        # Campos especiais
        if field == "NAME":
            return project.get("name", "")
        elif field == "DESCRIPTION":
            return project.get("description", "")
        elif field == "STATUS":
            return project.get("status", "")
        elif field == "CREATED_AT":
            return project.get("created_at", "")
        elif field == "UPDATED_AT":
            return project.get("updated_at", "")
        
        # Campos aninhados (usando notação de ponto)
        if "." in field:
            parts = field.split(".")
            value = project
            
            for part in parts:
                if isinstance(value, dict) and part in value:
                    value = value[part]
                else:
                    return None
            
            return value
        
        # Campo direto
        return project.get(field)
    
    def _retrieve_context(self, project_ids: List[str], context_spec: str) -> Dict[str, Any]:
        """
        Recupera contexto para projetos
        
        Args:
            project_ids: Lista de IDs de projeto
            context_spec: Especificação de contexto
            
        Returns:
            Dict: Contexto por projeto
        """
        context = {}
        
        for project_id in project_ids:
            if context_spec == "LAST_SESSION":
                # Obter contexto da última sessão
                if self.session_manager:
                    sessions = self.session_manager.get_all_sessions()
                    for session in sessions:
                        if session.get("current_project") == project_id:
                            session_data = self.session_manager.get_session(session["id"])
                            context[project_id] = session_data.get("context", {})
                            break
            elif context_spec.startswith("LAST_") and context_spec.endswith("_COMMITS"):
                # Obter contexto dos últimos N commits
                try:
                    n_commits = int(context_spec.split("_")[1])
                    
                    if self.project_manager:
                        project = self.project_manager.get_project(project_id)
                        if "git_path" in project.get("metadata", {}):
                            git_context = self.project_manager.get_git_context(project["metadata"]["git_path"])
                            if "commits" in git_context:
                                context[project_id] = {
                                    "commits": git_context["commits"][:n_commits]
                                }
                except:
                    pass
            elif context_spec.startswith("LAST_") and context_spec.endswith("_DAYS"):
                # Obter contexto dos últimos N dias
                try:
                    n_days = int(context_spec.split("_")[1])
                    cutoff_date = datetime.now() - timedelta(days=n_days)
                    
                    if self.project_manager:
                        project = self.project_manager.get_project(project_id)
                        context[project_id] = {
                            "history": [
                                entry for entry in project.get("history", [])
                                if entry.get("timestamp", "") >= cutoff_date.isoformat()
                            ]
                        }
                except:
                    pass
            else:
                # Usar contexto completo do projeto
                if self.project_manager:
                    project = self.project_manager.get_project(project_id)
                    context[project_id] = project.get("context", {})
        
        return context
    
    def _search_value(self, value: str, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Pesquisa valor em contexto
        
        Args:
            value: Valor a pesquisar
            context: Contexto do projeto
            
        Returns:
            List[Dict]: Resultados da pesquisa
        """
        results = []
        
        # Pesquisar em campos de texto
        self._search_in_dict(context, value, "", results)
        
        return results
    
    def _search_in_dict(self, d: Dict[str, Any], value: str, path: str, results: List[Dict[str, Any]]) -> None:
        """
        Pesquisa recursivamente em dicionário
        
        Args:
            d: Dicionário a pesquisar
            value: Valor a pesquisar
            path: Caminho atual
            results: Lista de resultados
        """
        for k, v in d.items():
            current_path = f"{path}.{k}" if path else k
            
            if isinstance(v, dict):
                self._search_in_dict(v, value, current_path, results)
            elif isinstance(v, list):
                for i, item in enumerate(v):
                    if isinstance(item, dict):
                        self._search_in_dict(item, value, f"{current_path}[{i}]", results)
                    elif isinstance(item, str) and value in item:
                        results.append({
                            "path": f"{current_path}[{i}]",
                            "value": item
                        })
            elif isinstance(v, str) and value in v:
                results.append({
                    "path": current_path,
                    "value": v
                })
    
    def _apply_priority(self, results: List[Any], priorities: List[str]) -> List[Any]:
        """
        Aplica priorização aos resultados
        
        Args:
            results: Resultados a priorizar
            priorities: Lista de prioridades
            
        Returns:
            List: Resultados priorizados
        """
        # Implementação simplificada
        if "RECENCY" in priorities:
            # Ordenar por data de atualização (mais recente primeiro)
            if isinstance(results, list) and results and isinstance(results[0], dict) and "updated_at" in results[0]:
                results.sort(key=lambda x: x.get("updated_at", ""), reverse=True)
        
        if "RELEVANCE" in priorities and self.context_storage:
            # Implementação futura: ordenar por relevância usando embeddings
            pass
        
        return results
