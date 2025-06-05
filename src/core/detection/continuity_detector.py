#!/usr/bin/env python3
"""
Detector de Continuidade Avançado
Sistema para detectar quando uma pergunta é sobre continuidade de contexto
"""

import re
import json
from datetime import datetime
from typing import Dict, Any, List, Set, Tuple

class ContinuityDetector:
    """
    Detector de continuidade avançado com análise detalhada
    Suporta múltiplos idiomas e é facilmente extensível
    """
    
    def __init__(self):
        # Palavras-chave de alta confiança (português)
        self.high_confidence_keywords_pt = {
            "onde paramos", "continue", "status", "contexto", "projeto", 
            "trabalhamos", "continuity", "mcp-continuity", "retomar",
            "continuação", "prosseguir", "retome", "voltar", "voltemos"
        }
        
        # Palavras-chave de alta confiança (inglês)
        self.high_confidence_keywords_en = {
            "where we left", "continue", "status", "context", "project",
            "working on", "continuity", "mcp-continuity", "resume",
            "continuation", "proceed", "get back", "let's continue"
        }
        
        # Palavras-chave de média confiança (português)
        self.medium_confidence_keywords_pt = {
            "quebrar", "investigar", "procure", "produto continuity",
            "luaraujo", "sabedoria-financeira", "finn", "premium-hub",
            "andamento", "progresso", "avanço", "desenvolvimento"
        }
        
        # Palavras-chave de média confiança (inglês)
        self.medium_confidence_keywords_en = {
            "break", "investigate", "search", "continuity product",
            "progress", "advancement", "development", "ongoing"
        }
        
        # Padrões de contexto (português)
        self.context_patterns_pt = {
            "como", "quando", "porque", "qual", "fazer", 
            "implementar", "corrigir", "testar", "melhorar",
            "otimizar", "refatorar", "adicionar"
        }
        
        # Padrões de contexto (inglês)
        self.context_patterns_en = {
            "how", "when", "why", "which", "what", "do",
            "implement", "fix", "test", "improve",
            "optimize", "refactor", "add"
        }
        
        # Compilar expressões regulares para detecção mais eficiente
        self._compile_regex_patterns()
    
    def _compile_regex_patterns(self) -> None:
        """Compila expressões regulares para detecção mais eficiente"""
        # Padrões de perguntas
        self.question_pattern = re.compile(r'\?|como|what|how|quando|when|porque|why|qual|which|where')
        
        # Padrões de comandos
        self.command_pattern = re.compile(r'(mostre|continue|retome|show|continue|resume|list|listar)')
        
        # Padrões de referência a trabalho anterior
        self.previous_work_pattern = re.compile(r'(anterior|previous|last time|última vez|before|antes)')
    
    def detect(self, text: str) -> Dict[str, Any]:
        """
        Detecta se o texto é sobre continuidade com análise detalhada
        
        Args:
            text: Texto a ser analisado
            
        Returns:
            Dict: Resultado da análise com campos is_continuity, confidence, reasoning, etc.
        """
        text_lower = text.lower()
        
        # Detectar idioma (simplificado)
        is_english = self._detect_language(text_lower)
        
        # Inicializar resultado
        result = {
            "is_continuity": False,
            "confidence": 0.0,
            "reasoning": [],
            "detected_keywords": [],
            "detected_patterns": [],
            "language": "en" if is_english else "pt",
            "timestamp": datetime.now().isoformat()
        }
        
        # Selecionar conjuntos de palavras-chave com base no idioma
        high_confidence_keywords = self.high_confidence_keywords_en if is_english else self.high_confidence_keywords_pt
        medium_confidence_keywords = self.medium_confidence_keywords_en if is_english else self.medium_confidence_keywords_pt
        context_patterns = self.context_patterns_en if is_english else self.context_patterns_pt
        
        # Verificar palavras-chave de alta confiança
        for keyword in high_confidence_keywords:
            if keyword in text_lower:
                result["detected_keywords"].append(keyword)
                result["confidence"] += 0.3
                result["reasoning"].append(f"Palavra-chave de alta confiança: '{keyword}'")
        
        # Verificar palavras-chave de média confiança
        for keyword in medium_confidence_keywords:
            if keyword in text_lower:
                result["detected_keywords"].append(keyword)
                result["confidence"] += 0.15
                result["reasoning"].append(f"Palavra-chave de média confiança: '{keyword}'")
        
        # Verificar padrões de contexto
        for pattern in context_patterns:
            if pattern in text_lower:
                result["detected_patterns"].append(pattern)
                result["confidence"] += 0.1
                result["reasoning"].append(f"Padrão de contexto: '{pattern}'")
        
        # Verificar padrões de expressão regular
        if self.question_pattern.search(text_lower):
            result["detected_patterns"].append("question")
            result["confidence"] += 0.05
            result["reasoning"].append("Padrão de pergunta detectado")
            
        if self.command_pattern.search(text_lower):
            result["detected_patterns"].append("command")
            result["confidence"] += 0.1
            result["reasoning"].append("Padrão de comando detectado")
            
        if self.previous_work_pattern.search(text_lower):
            result["detected_patterns"].append("previous_work")
            result["confidence"] += 0.2
            result["reasoning"].append("Referência a trabalho anterior detectada")
        
        # Verificar entrada longa (pode precisar de contexto)
        if len(text) > 50:
            result["confidence"] += 0.1
            result["reasoning"].append(f"Entrada longa detectada ({len(text)} caracteres)")
        
        # Limitar confiança a 1.0
        result["confidence"] = min(result["confidence"], 1.0)
        
        # Determinar resultado final
        result["is_continuity"] = result["confidence"] >= 0.3
        
        return result
    
    def _detect_language(self, text: str) -> bool:
        """
        Detecta se o texto está em inglês (simplificado)
        
        Args:
            text: Texto a ser analisado
            
        Returns:
            bool: True se inglês, False se português
        """
        # Palavras comuns em inglês
        english_words = {"the", "and", "is", "in", "to", "it", "that", "was", "for", "on", "are", "with", "they", "be", "at"}
        
        # Palavras comuns em português
        portuguese_words = {"o", "a", "de", "que", "e", "do", "da", "em", "um", "para", "é", "com", "não", "uma", "os"}
        
        # Contar ocorrências
        english_count = sum(1 for word in english_words if f" {word} " in f" {text} ")
        portuguese_count = sum(1 for word in portuguese_words if f" {word} " in f" {text} ")
        
        # Determinar idioma
        return english_count > portuguese_count
    
    def train(self, examples: List[Tuple[str, bool]]) -> None:
        """
        Treina o detector com exemplos rotulados
        
        Args:
            examples: Lista de tuplas (texto, is_continuity)
        """
        # Implementação futura: treinar modelo ML com exemplos
        pass
    
    def save_model(self, path: str) -> bool:
        """
        Salva o modelo em disco
        
        Args:
            path: Caminho para salvar o modelo
            
        Returns:
            bool: True se sucesso, False caso contrário
        """
        try:
            model_data = {
                "high_confidence_keywords_pt": list(self.high_confidence_keywords_pt),
                "high_confidence_keywords_en": list(self.high_confidence_keywords_en),
                "medium_confidence_keywords_pt": list(self.medium_confidence_keywords_pt),
                "medium_confidence_keywords_en": list(self.medium_confidence_keywords_en),
                "context_patterns_pt": list(self.context_patterns_pt),
                "context_patterns_en": list(self.context_patterns_en)
            }
            
            with open(path, 'w') as f:
                json.dump(model_data, f, indent=2)
            
            return True
        except Exception as e:
            print(f"Erro ao salvar modelo: {e}")
            return False
    
    def load_model(self, path: str) -> bool:
        """
        Carrega o modelo do disco
        
        Args:
            path: Caminho para carregar o modelo
            
        Returns:
            bool: True se sucesso, False caso contrário
        """
        try:
            with open(path, 'r') as f:
                model_data = json.load(f)
            
            self.high_confidence_keywords_pt = set(model_data["high_confidence_keywords_pt"])
            self.high_confidence_keywords_en = set(model_data["high_confidence_keywords_en"])
            self.medium_confidence_keywords_pt = set(model_data["medium_confidence_keywords_pt"])
            self.medium_confidence_keywords_en = set(model_data["medium_confidence_keywords_en"])
            self.context_patterns_pt = set(model_data["context_patterns_pt"])
            self.context_patterns_en = set(model_data["context_patterns_en"])
            
            # Recompilar expressões regulares
            self._compile_regex_patterns()
            
            return True
        except Exception as e:
            print(f"Erro ao carregar modelo: {e}")
            return False
