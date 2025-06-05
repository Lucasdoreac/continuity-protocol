#!/usr/bin/env python3
"""
Schema Validation - Continuity Protocol
Implementação de validação de schema para metadados e outros dados do sistema
"""

import json
import re
from typing import Dict, List, Any, Optional, Union, Callable

class SchemaValidator:
    """
    Validador de schema para o Continuity Protocol
    """
    
    # Schema para metadados de artefatos
    ARTIFACT_METADATA_SCHEMA = {
        "type": "object",
        "properties": {
            "title": {"type": "string", "required": True, "max_length": 100},
            "description": {"type": "string", "max_length": 500},
            "version": {"type": "string", "pattern": r"^\d+\.\d+(\.\d+)?$"},
            "author": {"type": "string"},
            "type": {"type": "string"},
            "category": {"type": "string"},
            "tags": {"type": "array", "item_type": "string"},
            "status": {"type": "string"},
            "dependencies": {"type": "array", "item_type": "string"},
            "milestone": {"type": "string"},
            "test_date": {"type": "string", "pattern": r"^\d{4}-\d{2}-\d{2}$"},
            "completion_date": {"type": "string", "pattern": r"^\d{4}-\d{2}-\d{2}$"},
            "validation_date": {"type": "string", "pattern": r"^\d{4}-\d{2}-\d{2}$"},
            "audience": {"type": "string"},
            "next_agent": {"type": "string"}
        },
        "required": ["title"]
    }
    
    # Schema para projetos
    PROJECT_SCHEMA = {
        "type": "object",
        "properties": {
            "id": {"type": "string", "required": True, "pattern": r"^[a-z0-9-]+$"},
            "name": {"type": "string", "required": True, "max_length": 100},
            "description": {"type": "string", "required": True, "max_length": 500},
            "created_at": {"type": "string", "required": True},
            "updated_at": {"type": "string", "required": True},
            "artifacts": {"type": "array", "item_type": "string"},
            "agents": {"type": "array", "item_type": "string"}
        },
        "required": ["id", "name", "description"]
    }
    
    # Schema para agentes
    AGENT_SCHEMA = {
        "type": "object",
        "properties": {
            "id": {"type": "string", "required": True},
            "type": {"type": "string", "required": True},
            "capabilities": {"type": "array", "item_type": "string", "required": True},
            "registered_at": {"type": "string", "required": True},
            "last_active": {"type": "string", "required": True},
            "projects": {"type": "array", "item_type": "string"}
        },
        "required": ["id", "type", "capabilities"]
    }
    
    @classmethod
    def validate_type(cls, value: Any, expected_type: str) -> bool:
        """
        Valida o tipo de um valor
        
        Args:
            value: Valor a ser validado
            expected_type: Tipo esperado
            
        Returns:
            bool: True se o tipo for válido, False caso contrário
        """
        if expected_type == "string":
            return isinstance(value, str)
        elif expected_type == "number":
            return isinstance(value, (int, float))
        elif expected_type == "integer":
            return isinstance(value, int)
        elif expected_type == "boolean":
            return isinstance(value, bool)
        elif expected_type == "array":
            return isinstance(value, list)
        elif expected_type == "object":
            return isinstance(value, dict)
        else:
            return False
    
    @classmethod
    def validate_pattern(cls, value: str, pattern: str) -> bool:
        """
        Valida um valor contra um padrão regex
        
        Args:
            value: Valor a ser validado
            pattern: Padrão regex
            
        Returns:
            bool: True se o valor corresponder ao padrão, False caso contrário
        """
        try:
            return bool(re.match(pattern, value))
        except:
            return False
    
    @classmethod
    def validate_max_length(cls, value: str, max_length: int) -> bool:
        """
        Valida o comprimento máximo de uma string
        
        Args:
            value: Valor a ser validado
            max_length: Comprimento máximo
            
        Returns:
            bool: True se o comprimento for válido, False caso contrário
        """
        return len(value) <= max_length
    
    @classmethod
    def validate_array_items(cls, array: List[Any], item_type: str) -> bool:
        """
        Valida os itens de um array
        
        Args:
            array: Array a ser validado
            item_type: Tipo esperado dos itens
            
        Returns:
            bool: True se todos os itens forem válidos, False caso contrário
        """
        return all(cls.validate_type(item, item_type) for item in array)
    
    @classmethod
    def validate_against_schema(cls, data: Dict[str, Any], schema: Dict[str, Any]) -> Dict[str, Any]:
        """
        Valida dados contra um schema
        
        Args:
            data: Dados a serem validados
            schema: Schema para validação
            
        Returns:
            Dict: Resultado da validação
        """
        result = {
            "valid": True,
            "errors": []
        }
        
        # Verificar tipo do objeto principal
        if not cls.validate_type(data, schema.get("type", "object")):
            result["valid"] = False
            result["errors"].append(f"Data is not of type {schema.get('type', 'object')}")
            return result
        
        # Verificar propriedades
        properties = schema.get("properties", {})
        for prop_name, prop_schema in properties.items():
            # Verificar se propriedade é obrigatória
            is_required = prop_schema.get("required", False) or prop_name in schema.get("required", [])
            
            if is_required and prop_name not in data:
                result["valid"] = False
                result["errors"].append(f"Required property '{prop_name}' is missing")
                continue
            
            # Pular validação se propriedade não estiver presente
            if prop_name not in data:
                continue
            
            value = data[prop_name]
            
            # Validar tipo
            if "type" in prop_schema and not cls.validate_type(value, prop_schema["type"]):
                result["valid"] = False
                result["errors"].append(f"Property '{prop_name}' should be of type {prop_schema['type']}")
            
            # Validar padrão
            if "pattern" in prop_schema and isinstance(value, str):
                if not cls.validate_pattern(value, prop_schema["pattern"]):
                    result["valid"] = False
                    result["errors"].append(f"Property '{prop_name}' does not match pattern {prop_schema['pattern']}")
            
            # Validar comprimento máximo
            if "max_length" in prop_schema and isinstance(value, str):
                if not cls.validate_max_length(value, prop_schema["max_length"]):
                    result["valid"] = False
                    result["errors"].append(f"Property '{prop_name}' exceeds maximum length of {prop_schema['max_length']}")
            
            # Validar itens de array
            if "item_type" in prop_schema and isinstance(value, list):
                if not cls.validate_array_items(value, prop_schema["item_type"]):
                    result["valid"] = False
                    result["errors"].append(f"Items in array '{prop_name}' should be of type {prop_schema['item_type']}")
        
        return result
    
    @classmethod
    def validate_artifact_metadata(cls, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Valida metadados de artefato
        
        Args:
            metadata: Metadados a serem validados
            
        Returns:
            Dict: Resultado da validação
        """
        return cls.validate_against_schema(metadata, cls.ARTIFACT_METADATA_SCHEMA)
    
    @classmethod
    def validate_project(cls, project: Dict[str, Any]) -> Dict[str, Any]:
        """
        Valida dados de projeto
        
        Args:
            project: Dados do projeto a serem validados
            
        Returns:
            Dict: Resultado da validação
        """
        return cls.validate_against_schema(project, cls.PROJECT_SCHEMA)
    
    @classmethod
    def validate_agent(cls, agent: Dict[str, Any]) -> Dict[str, Any]:
        """
        Valida dados de agente
        
        Args:
            agent: Dados do agente a serem validados
            
        Returns:
            Dict: Resultado da validação
        """
        return cls.validate_against_schema(agent, cls.AGENT_SCHEMA)
    
    @classmethod
    def sanitize_metadata(cls, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sanitiza metadados para garantir conformidade com o schema
        
        Args:
            metadata: Metadados a serem sanitizados
            
        Returns:
            Dict: Metadados sanitizados
        """
        sanitized = {}
        
        # Garantir que title existe
        if "title" not in metadata or not isinstance(metadata["title"], str):
            sanitized["title"] = "Untitled"
        else:
            # Limitar comprimento do título
            sanitized["title"] = metadata["title"][:100]
        
        # Sanitizar description
        if "description" in metadata and isinstance(metadata["description"], str):
            sanitized["description"] = metadata["description"][:500]
        
        # Sanitizar version
        if "version" in metadata and isinstance(metadata["version"], str):
            if re.match(r"^\d+\.\d+(\.\d+)?$", metadata["version"]):
                sanitized["version"] = metadata["version"]
            else:
                sanitized["version"] = "1.0.0"
        
        # Copiar outros campos válidos
        for key, value in metadata.items():
            if key not in sanitized and key in cls.ARTIFACT_METADATA_SCHEMA["properties"]:
                prop_schema = cls.ARTIFACT_METADATA_SCHEMA["properties"][key]
                
                # Validar tipo
                if "type" in prop_schema and cls.validate_type(value, prop_schema["type"]):
                    # Validar comprimento para strings
                    if prop_schema["type"] == "string" and "max_length" in prop_schema:
                        sanitized[key] = value[:prop_schema["max_length"]]
                    # Validar itens de array
                    elif prop_schema["type"] == "array" and "item_type" in prop_schema:
                        if cls.validate_array_items(value, prop_schema["item_type"]):
                            sanitized[key] = value
                    else:
                        sanitized[key] = value
        
        return sanitized
    
    @classmethod
    def sanitize_path(cls, path: str) -> str:
        """
        Sanitiza um caminho de arquivo para evitar path traversal
        
        Args:
            path: Caminho a ser sanitizado
            
        Returns:
            str: Caminho sanitizado
        """
        # Remover caracteres perigosos
        path = re.sub(r'[^\w\s\-\./]', '', path)
        
        # Remover tentativas de path traversal
        path = path.replace('../', '').replace('..\\', '')
        
        return path
