#!/usr/bin/env python3
"""
Vector Store para armazenamento de contexto escalável
Permite armazenar e recuperar contexto usando embeddings semânticos
"""

import os
import json
from typing import List, Dict, Any, Optional
import numpy as np

# Suporte condicional para diferentes backends de embedding
try:
    from langchain.vectorstores import Chroma
    from langchain.embeddings import OpenAIEmbeddings
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False

# Implementação de fallback simples quando dependências não estão disponíveis
class SimpleVectorStore:
    """Implementação simples de vector store para uso sem dependências externas"""
    
    def __init__(self, persist_directory: str):
        self.persist_directory = persist_directory
        os.makedirs(persist_directory, exist_ok=True)
        self.index_file = os.path.join(persist_directory, "index.json")
        self.vectors = self._load_vectors()
    
    def _load_vectors(self) -> List[Dict[str, Any]]:
        """Carrega vetores do disco"""
        if os.path.exists(self.index_file):
            try:
                with open(self.index_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Erro ao carregar vetores: {e}")
                return []
        return []
    
    def _save_vectors(self) -> None:
        """Salva vetores em disco"""
        with open(self.index_file, 'w') as f:
            json.dump(self.vectors, f, indent=2)
    
    def add_texts(self, texts: List[str], metadatas: List[Dict[str, Any]]) -> None:
        """Adiciona textos ao vector store"""
        for i, (text, metadata) in enumerate(zip(texts, metadatas)):
            # Usar hash simples como embedding de fallback
            hash_val = hash(text) % 10000
            vector_entry = {
                "id": f"doc_{len(self.vectors) + i}",
                "text": text,
                "metadata": metadata,
                "hash": hash_val
            }
            self.vectors.append(vector_entry)
        
        self._save_vectors()
    
    def similarity_search(self, query: str, k: int = 5, filter: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Busca por similaridade (implementação simplificada)"""
        # Filtrar por metadata se necessário
        candidates = self.vectors
        if filter:
            candidates = []
            for vector in self.vectors:
                match = True
                for key, value in filter.items():
                    if key not in vector["metadata"] or vector["metadata"][key] != value:
                        match = False
                        break
                if match:
                    candidates.append(vector)
        
        # Ordenar por "similaridade" (usando hash como aproximação)
        query_hash = hash(query) % 10000
        candidates.sort(key=lambda x: abs(x["hash"] - query_hash))
        
        # Retornar os k mais similares
        results = candidates[:k]
        return [{"page_content": r["text"], "metadata": r["metadata"]} for r in results]
    
    def persist(self) -> None:
        """Persiste vetores em disco"""
        self._save_vectors()

class ContextVectorStore:
    """Armazenamento vetorial de contexto com suporte a múltiplos backends"""
    
    def __init__(self, base_path: str):
        """
        Inicializa o vector store
        
        Args:
            base_path: Caminho base para armazenamento
        """
        self.base_path = base_path
        self.vector_db_path = os.path.join(base_path, "vector_db")
        os.makedirs(self.vector_db_path, exist_ok=True)
        
        # Inicializar backend apropriado
        if LANGCHAIN_AVAILABLE:
            try:
                self.embeddings = OpenAIEmbeddings()
                self.store = Chroma(
                    collection_name="continuity_context",
                    embedding_function=self.embeddings,
                    persist_directory=self.vector_db_path
                )
                self.backend = "langchain"
            except Exception as e:
                print(f"Erro ao inicializar LangChain: {e}")
                self.store = SimpleVectorStore(self.vector_db_path)
                self.backend = "simple"
        else:
            self.store = SimpleVectorStore(self.vector_db_path)
            self.backend = "simple"
        
        print(f"Vector store inicializado com backend: {self.backend}")
    
    def add_context(self, project_id: str, context_chunks: List[Dict[str, Any]]) -> bool:
        """
        Adiciona chunks de contexto ao vector store
        
        Args:
            project_id: ID do projeto
            context_chunks: Lista de chunks de contexto com campos 'text', 'source' e 'timestamp'
            
        Returns:
            bool: True se sucesso, False caso contrário
        """
        try:
            texts = [chunk["text"] for chunk in context_chunks]
            metadatas = [{"project_id": project_id, 
                        "source": chunk.get("source", "unknown"),
                        "timestamp": chunk.get("timestamp", "")} 
                        for chunk in context_chunks]
            
            self.store.add_texts(texts=texts, metadatas=metadatas)
            self.store.persist()
            return True
        except Exception as e:
            print(f"Erro ao adicionar contexto: {e}")
            return False
    
    def query_context(self, query_text: str, project_id: Optional[str] = None, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Consulta contexto relevante baseado em similaridade semântica
        
        Args:
            query_text: Texto da consulta
            project_id: ID do projeto (opcional)
            limit: Número máximo de resultados
            
        Returns:
            List[Dict]: Lista de resultados
        """
        try:
            filter_dict = {"project_id": project_id} if project_id else None
            results = self.store.similarity_search(
                query=query_text,
                k=limit,
                filter=filter_dict
            )
            
            # Formatar resultados
            formatted_results = []
            for doc in results:
                formatted_results.append({
                    "text": doc.page_content,
                    "metadata": doc.metadata
                })
            
            return formatted_results
        except Exception as e:
            print(f"Erro ao consultar contexto: {e}")
            return []
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Obtém estatísticas do vector store
        
        Returns:
            Dict: Estatísticas
        """
        stats = {
            "backend": self.backend,
            "path": self.vector_db_path
        }
        
        # Adicionar estatísticas específicas do backend
        if self.backend == "simple":
            stats["document_count"] = len(self.store.vectors)
        
        return stats
