#!/usr/bin/env python3
"""
Search System - Continuity Protocol
Sistema de busca para artefatos
"""

import os
import json
import re
import time
from datetime import datetime
from typing import Dict, List, Any, Optional, Union

class SearchSystem:
    """
    Sistema de busca para artefatos do Continuity Protocol
    """
    
    def __init__(self, search_dir: str = None):
        """
        Inicializa o sistema de busca
        
        Args:
            search_dir: Diretório para armazenamento de índices de busca
        """
        # Configurar diretório de busca
        if search_dir:
            self.search_dir = search_dir
        else:
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            self.search_dir = os.path.join(base_dir, "shared_context", "search")
        
        # Criar diretório se não existir
        os.makedirs(self.search_dir, exist_ok=True)
        
        # Arquivo de índice de busca
        self.index_file = os.path.join(self.search_dir, "search_index.json")
        
        # Carregar ou criar índice de busca
        self.search_index = self._load_or_create_index()
    
    def _load_or_create_index(self) -> Dict[str, Any]:
        """
        Carrega ou cria índice de busca
        
        Returns:
            Dict: Índice de busca
        """
        if os.path.exists(self.index_file):
            try:
                with open(self.index_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        
        # Criar índice vazio
        index = {
            "artifacts": {},
            "terms": {},
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "last_indexed": None
        }
        
        # Salvar índice
        with open(self.index_file, 'w') as f:
            json.dump(index, f, indent=2)
        
        return index
    
    def _save_index(self) -> None:
        """Salva índice de busca"""
        self.search_index["updated_at"] = datetime.now().isoformat()
        with open(self.index_file, 'w') as f:
            json.dump(self.search_index, f, indent=2)
    
    def _tokenize(self, text: str) -> List[str]:
        """
        Tokeniza texto em termos para indexação
        
        Args:
            text: Texto a ser tokenizado
            
        Returns:
            List[str]: Lista de termos
        """
        # Converter para minúsculas
        text = text.lower()
        
        # Remover caracteres especiais
        text = re.sub(r'[^\w\s]', ' ', text)
        
        # Dividir em termos
        terms = text.split()
        
        # Remover termos muito curtos
        terms = [term for term in terms if len(term) > 2]
        
        # Remover duplicatas
        terms = list(set(terms))
        
        return terms
    
    def _extract_metadata_terms(self, metadata: Dict[str, Any]) -> List[str]:
        """
        Extrai termos de metadados
        
        Args:
            metadata: Metadados do artefato
            
        Returns:
            List[str]: Lista de termos
        """
        terms = []
        
        # Processar campos de metadados
        for key, value in metadata.items():
            if isinstance(value, str):
                # Adicionar valor como termo
                terms.extend(self._tokenize(value))
                
                # Adicionar chave como termo
                terms.extend(self._tokenize(key))
            elif isinstance(value, (int, float)):
                # Adicionar valor numérico como string
                terms.append(str(value))
        
        return terms
    
    def index_artifact(self, artifact_id: str, content: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Indexa um artefato para busca
        
        Args:
            artifact_id: ID do artefato
            content: Conteúdo do artefato
            metadata: Metadados do artefato
            
        Returns:
            Dict: Resultado da indexação
        """
        # Extrair termos do conteúdo
        content_terms = self._tokenize(content)
        
        # Extrair termos dos metadados
        metadata_terms = self._extract_metadata_terms(metadata)
        
        # Combinar termos
        all_terms = content_terms + metadata_terms
        
        # Registrar artefato no índice
        self.search_index["artifacts"][artifact_id] = {
            "indexed_at": datetime.now().isoformat(),
            "term_count": len(all_terms),
            "metadata": {
                "title": metadata.get("title", ""),
                "type": metadata.get("type", ""),
                "created_at": metadata.get("created_at", ""),
                "created_by": metadata.get("created_by", "")
            }
        }
        
        # Indexar termos
        for term in all_terms:
            if term not in self.search_index["terms"]:
                self.search_index["terms"][term] = []
            
            if artifact_id not in self.search_index["terms"][term]:
                self.search_index["terms"][term].append(artifact_id)
        
        # Atualizar timestamp de última indexação
        self.search_index["last_indexed"] = datetime.now().isoformat()
        
        # Salvar índice
        self._save_index()
        
        return {
            "success": True,
            "artifact_id": artifact_id,
            "term_count": len(all_terms),
            "indexed_at": self.search_index["artifacts"][artifact_id]["indexed_at"]
        }
    
    def remove_from_index(self, artifact_id: str) -> Dict[str, Any]:
        """
        Remove um artefato do índice
        
        Args:
            artifact_id: ID do artefato
            
        Returns:
            Dict: Resultado da remoção
        """
        # Verificar se artefato está indexado
        if artifact_id not in self.search_index["artifacts"]:
            return {
                "success": False,
                "error": f"Artefato {artifact_id} não está indexado"
            }
        
        # Remover artefato do índice
        artifact_info = self.search_index["artifacts"].pop(artifact_id)
        
        # Remover artefato dos termos
        for term, artifacts in list(self.search_index["terms"].items()):
            if artifact_id in artifacts:
                artifacts.remove(artifact_id)
            
            # Remover termo se não tiver mais artefatos
            if not artifacts:
                del self.search_index["terms"][term]
        
        # Salvar índice
        self._save_index()
        
        return {
            "success": True,
            "artifact_id": artifact_id,
            "removed_at": datetime.now().isoformat()
        }
    
    def search(self, query: str, artifact_type: str = None, 
              created_by: str = None, limit: int = 10) -> Dict[str, Any]:
        """
        Busca artefatos por termos
        
        Args:
            query: Termos de busca
            artifact_type: Filtro por tipo de artefato
            created_by: Filtro por criador
            limit: Número máximo de resultados
            
        Returns:
            Dict: Resultados da busca
        """
        # Tokenizar query
        query_terms = self._tokenize(query)
        
        if not query_terms:
            return {
                "success": False,
                "error": "Query inválida ou muito curta"
            }
        
        # Encontrar artefatos que contêm os termos
        matching_artifacts = {}
        
        for term in query_terms:
            if term in self.search_index["terms"]:
                for artifact_id in self.search_index["terms"][term]:
                    if artifact_id not in matching_artifacts:
                        matching_artifacts[artifact_id] = 0
                    
                    matching_artifacts[artifact_id] += 1
        
        # Ordenar por relevância (número de termos correspondentes)
        sorted_artifacts = sorted(
            matching_artifacts.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        # Aplicar filtros
        filtered_artifacts = []
        
        for artifact_id, score in sorted_artifacts:
            # Verificar se artefato ainda existe no índice
            if artifact_id not in self.search_index["artifacts"]:
                continue
            
            artifact_info = self.search_index["artifacts"][artifact_id]
            
            # Filtrar por tipo
            if artifact_type and artifact_info["metadata"].get("type") != artifact_type:
                continue
            
            # Filtrar por criador
            if created_by and artifact_info["metadata"].get("created_by") != created_by:
                continue
            
            # Adicionar à lista filtrada
            filtered_artifacts.append({
                "artifact_id": artifact_id,
                "score": score,
                "relevance": score / len(query_terms),
                "metadata": artifact_info["metadata"]
            })
            
            # Limitar número de resultados
            if len(filtered_artifacts) >= limit:
                break
        
        return {
            "success": True,
            "query": query,
            "terms": query_terms,
            "results": filtered_artifacts,
            "total": len(filtered_artifacts)
        }
    
    def reindex_all(self, artifacts_provider: callable) -> Dict[str, Any]:
        """
        Reindexar todos os artefatos
        
        Args:
            artifacts_provider: Função que retorna lista de artefatos
            
        Returns:
            Dict: Resultado da reindexação
        """
        # Obter lista de artefatos
        try:
            artifacts = artifacts_provider()
        except Exception as e:
            return {
                "success": False,
                "error": f"Erro ao obter lista de artefatos: {str(e)}"
            }
        
        # Limpar índice atual
        self.search_index["artifacts"] = {}
        self.search_index["terms"] = {}
        
        # Indexar artefatos
        indexed_count = 0
        errors = []
        
        for artifact in artifacts:
            try:
                artifact_id = artifact["id"]
                content = artifact["content"]
                metadata = {
                    "title": artifact.get("title", ""),
                    "type": artifact.get("type", ""),
                    "created_at": artifact.get("created_at", ""),
                    "created_by": artifact.get("created_by", ""),
                    "metadata": artifact.get("metadata", {})
                }
                
                self.index_artifact(artifact_id, content, metadata)
                indexed_count += 1
            except Exception as e:
                errors.append({
                    "artifact_id": artifact.get("id", "unknown"),
                    "error": str(e)
                })
        
        # Atualizar timestamp de última indexação
        self.search_index["last_indexed"] = datetime.now().isoformat()
        
        # Salvar índice
        self._save_index()
        
        return {
            "success": True,
            "indexed_count": indexed_count,
            "error_count": len(errors),
            "errors": errors,
            "indexed_at": self.search_index["last_indexed"]
        }
    
    def get_index_stats(self) -> Dict[str, Any]:
        """
        Obtém estatísticas do índice
        
        Returns:
            Dict: Estatísticas do índice
        """
        return {
            "success": True,
            "artifact_count": len(self.search_index["artifacts"]),
            "term_count": len(self.search_index["terms"]),
            "created_at": self.search_index["created_at"],
            "updated_at": self.search_index["updated_at"],
            "last_indexed": self.search_index["last_indexed"]
        }
    
    def search_by_metadata(self, metadata_filters: Dict[str, Any], 
                          limit: int = 10) -> Dict[str, Any]:
        """
        Busca artefatos por metadados
        
        Args:
            metadata_filters: Filtros de metadados
            limit: Número máximo de resultados
            
        Returns:
            Dict: Resultados da busca
        """
        if not metadata_filters:
            return {
                "success": False,
                "error": "Nenhum filtro de metadados fornecido"
            }
        
        # Encontrar artefatos que correspondem aos filtros
        matching_artifacts = []
        
        for artifact_id, artifact_info in self.search_index["artifacts"].items():
            # Verificar se todos os filtros correspondem
            match = True
            
            for key, value in metadata_filters.items():
                if key not in artifact_info["metadata"] or artifact_info["metadata"][key] != value:
                    match = False
                    break
            
            if match:
                matching_artifacts.append({
                    "artifact_id": artifact_id,
                    "metadata": artifact_info["metadata"]
                })
                
                # Limitar número de resultados
                if len(matching_artifacts) >= limit:
                    break
        
        return {
            "success": True,
            "filters": metadata_filters,
            "results": matching_artifacts,
            "total": len(matching_artifacts)
        }

# Instância global para uso em todo o sistema
search_system = SearchSystem()
