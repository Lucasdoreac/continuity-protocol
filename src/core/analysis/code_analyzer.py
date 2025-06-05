#!/usr/bin/env python3
"""
Analisador de Código
Sistema para analisar código-fonte e extrair informações relevantes
"""

import os
import ast
import json
import re
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple

class CodeAnalyzer:
    """
    Analisador de código com suporte a múltiplas linguagens
    """
    
    def __init__(self):
        """Inicializa o analisador de código"""
        self.supported_languages = {
            ".py": self._analyze_python,
            ".js": self._analyze_javascript,
            ".html": self._analyze_html,
            ".css": self._analyze_css,
            ".json": self._analyze_json,
            ".md": self._analyze_markdown,
            ".txt": self._analyze_text
        }
    
    def analyze_file(self, file_path: str) -> Dict[str, Any]:
        """
        Analisa um arquivo de código
        
        Args:
            file_path: Caminho do arquivo
            
        Returns:
            Dict: Resultado da análise
        """
        if not os.path.exists(file_path):
            return {
                "error": f"Arquivo não encontrado: {file_path}",
                "success": False
            }
        
        # Determinar extensão do arquivo
        _, ext = os.path.splitext(file_path)
        ext = ext.lower()
        
        # Verificar se extensão é suportada
        if ext in self.supported_languages:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Analisar arquivo
                result = self.supported_languages[ext](content)
                
                # Adicionar metadados
                file_info = os.stat(file_path)
                result.update({
                    "file_path": file_path,
                    "file_size": file_info.st_size,
                    "last_modified": datetime.fromtimestamp(file_info.st_mtime).isoformat(),
                    "lines_count": len(content.splitlines()),
                    "success": True
                })
                
                return result
            except Exception as e:
                return {
                    "error": f"Erro ao analisar arquivo: {str(e)}",
                    "file_path": file_path,
                    "success": False
                }
        else:
            # Análise genérica para arquivos não suportados
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                file_info = os.stat(file_path)
                return {
                    "file_path": file_path,
                    "file_size": file_info.st_size,
                    "last_modified": datetime.fromtimestamp(file_info.st_mtime).isoformat(),
                    "lines_count": len(content.splitlines()),
                    "content_preview": content[:500] + ("..." if len(content) > 500 else ""),
                    "success": True
                }
            except Exception as e:
                return {
                    "error": f"Erro ao ler arquivo: {str(e)}",
                    "file_path": file_path,
                    "success": False
                }
    
    def analyze_directory(self, dir_path: str, max_files: int = 100) -> Dict[str, Any]:
        """
        Analisa um diretório de código
        
        Args:
            dir_path: Caminho do diretório
            max_files: Número máximo de arquivos a analisar
            
        Returns:
            Dict: Resultado da análise
        """
        if not os.path.exists(dir_path) or not os.path.isdir(dir_path):
            return {
                "error": f"Diretório não encontrado: {dir_path}",
                "success": False
            }
        
        results = {
            "dir_path": dir_path,
            "files_analyzed": 0,
            "languages": {},
            "files": [],
            "success": True
        }
        
        # Percorrer diretório
        file_count = 0
        for root, _, files in os.walk(dir_path):
            for file in files:
                # Verificar limite de arquivos
                if file_count >= max_files:
                    break
                
                # Ignorar arquivos ocultos e diretórios especiais
                if file.startswith('.') or '__pycache__' in root or 'node_modules' in root:
                    continue
                
                # Analisar arquivo
                file_path = os.path.join(root, file)
                _, ext = os.path.splitext(file)
                ext = ext.lower()
                
                # Incrementar contagem de linguagem
                if ext in results["languages"]:
                    results["languages"][ext] += 1
                else:
                    results["languages"][ext] = 1
                
                # Analisar apenas arquivos suportados
                if ext in self.supported_languages:
                    file_result = self.analyze_file(file_path)
                    if file_result["success"]:
                        # Adicionar resultado resumido
                        results["files"].append({
                            "path": os.path.relpath(file_path, dir_path),
                            "language": ext[1:] if ext.startswith('.') else ext,
                            "lines": file_result.get("lines_count", 0),
                            "size": file_result.get("file_size", 0)
                        })
                        
                        file_count += 1
        
        results["files_analyzed"] = file_count
        return results
    
    def _analyze_python(self, content: str) -> Dict[str, Any]:
        """
        Analisa código Python
        
        Args:
            content: Conteúdo do arquivo
            
        Returns:
            Dict: Resultado da análise
        """
        try:
            tree = ast.parse(content)
            
            # Extrair informações
            classes = []
            functions = []
            imports = []
            
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    methods = []
                    for item in node.body:
                        if isinstance(item, ast.FunctionDef):
                            methods.append(item.name)
                    
                    classes.append({
                        "name": node.name,
                        "lineno": node.lineno,
                        "methods": methods
                    })
                elif isinstance(node, ast.FunctionDef):
                    # Verificar se não é método de classe
                    parent_classes = [p for p in ast.iter_fields(tree) if isinstance(p, ast.ClassDef)]
                    if not any(node in c.body for c in parent_classes):
                        functions.append({
                            "name": node.name,
                            "lineno": node.lineno,
                            "args": [a.arg for a in node.args.args if hasattr(a, 'arg')]
                        })
                elif isinstance(node, ast.Import):
                    for name in node.names:
                        imports.append(name.name)
                elif isinstance(node, ast.ImportFrom):
                    for name in node.names:
                        imports.append(f"{node.module}.{name.name}" if node.module else name.name)
            
            # Calcular complexidade (simplificado)
            complexity = len(classes) * 3 + len(functions) * 2 + len(imports)
            
            return {
                "language": "python",
                "classes": classes,
                "functions": functions,
                "imports": imports,
                "complexity": complexity
            }
        except SyntaxError as e:
            return {
                "language": "python",
                "error": f"Erro de sintaxe: {str(e)}"
            }
    
    def _analyze_javascript(self, content: str) -> Dict[str, Any]:
        """
        Análise básica de JavaScript
        
        Args:
            content: Conteúdo do arquivo
            
        Returns:
            Dict: Resultado da análise
        """
        # Implementação simplificada
        functions = []
        classes = []
        imports = []
        
        # Detectar funções
        function_pattern = r'function\s+(\w+)\s*\([^)]*\)'
        for match in re.finditer(function_pattern, content):
            functions.append({
                "name": match.group(1),
                "lineno": content[:match.start()].count('\n') + 1
            })
        
        # Detectar funções arrow
        arrow_pattern = r'(?:const|let|var)\s+(\w+)\s*=\s*(?:\([^)]*\)|[^=]*)\s*=>'
        for match in re.finditer(arrow_pattern, content):
            functions.append({
                "name": match.group(1),
                "lineno": content[:match.start()].count('\n') + 1,
                "type": "arrow"
            })
        
        # Detectar classes
        class_pattern = r'class\s+(\w+)'
        for match in re.finditer(class_pattern, content):
            classes.append({
                "name": match.group(1),
                "lineno": content[:match.start()].count('\n') + 1
            })
        
        # Detectar imports
        import_pattern = r'import\s+(?:{[^}]*}|[^;]*)\s+from\s+[\'"]([^\'"]*)[\'"]'
        for match in re.finditer(import_pattern, content):
            imports.append(match.group(1))
        
        # Calcular complexidade (simplificado)
        complexity = len(classes) * 3 + len(functions) * 2 + len(imports)
        
        return {
            "language": "javascript",
            "functions": functions,
            "classes": classes,
            "imports": imports,
            "complexity": complexity
        }
    
    def _analyze_html(self, content: str) -> Dict[str, Any]:
        """
        Análise básica de HTML
        
        Args:
            content: Conteúdo do arquivo
            
        Returns:
            Dict: Resultado da análise
        """
        # Detectar tags
        tags = {}
        tag_pattern = r'<(\w+)[^>]*>'
        for match in re.finditer(tag_pattern, content):
            tag = match.group(1)
            if tag in tags:
                tags[tag] += 1
            else:
                tags[tag] = 1
        
        # Detectar scripts
        scripts = []
        script_pattern = r'<script[^>]*src=[\'"]([^\'"]*)[\'"]'
        for match in re.finditer(script_pattern, content):
            scripts.append(match.group(1))
        
        # Detectar estilos
        styles = []
        style_pattern = r'<link[^>]*rel=[\'"]stylesheet[\'"][^>]*href=[\'"]([^\'"]*)[\'"]'
        for match in re.finditer(style_pattern, content):
            styles.append(match.group(1))
        
        return {
            "language": "html",
            "tags": tags,
            "scripts": scripts,
            "styles": styles
        }
    
    def _analyze_css(self, content: str) -> Dict[str, Any]:
        """
        Análise básica de CSS
        
        Args:
            content: Conteúdo do arquivo
            
        Returns:
            Dict: Resultado da análise
        """
        # Detectar seletores
        selectors = []
        selector_pattern = r'([^{]+)\s*\{'
        for match in re.finditer(selector_pattern, content):
            selectors.append(match.group(1).strip())
        
        # Detectar propriedades
        properties = {}
        property_pattern = r'([a-zA-Z-]+)\s*:'
        for match in re.finditer(property_pattern, content):
            prop = match.group(1)
            if prop in properties:
                properties[prop] += 1
            else:
                properties[prop] = 1
        
        # Detectar media queries
        media_queries = []
        media_pattern = r'@media\s+([^{]+)'
        for match in re.finditer(media_pattern, content):
            media_queries.append(match.group(1).strip())
        
        return {
            "language": "css",
            "selectors": selectors,
            "selectors_count": len(selectors),
            "properties": properties,
            "media_queries": media_queries
        }
    
    def _analyze_json(self, content: str) -> Dict[str, Any]:
        """
        Análise de JSON
        
        Args:
            content: Conteúdo do arquivo
            
        Returns:
            Dict: Resultado da análise
        """
        try:
            data = json.loads(content)
            
            # Análise básica da estrutura
            if isinstance(data, dict):
                keys = list(data.keys())
                return {
                    "language": "json",
                    "structure": "object",
                    "keys": keys,
                    "keys_count": len(keys)
                }
            elif isinstance(data, list):
                return {
                    "language": "json",
                    "structure": "array",
                    "items_count": len(data)
                }
            else:
                return {
                    "language": "json",
                    "structure": "scalar"
                }
        except json.JSONDecodeError as e:
            return {
                "language": "json",
                "error": f"JSON inválido: {str(e)}"
            }
    
    def _analyze_markdown(self, content: str) -> Dict[str, Any]:
        """
        Análise de Markdown
        
        Args:
            content: Conteúdo do arquivo
            
        Returns:
            Dict: Resultado da análise
        """
        # Detectar cabeçalhos
        headers = []
        header_pattern = r'^(#{1,6})\s+(.+)$'
        for i, line in enumerate(content.splitlines()):
            match = re.match(header_pattern, line)
            if match:
                headers.append({
                    "level": len(match.group(1)),
                    "text": match.group(2),
                    "lineno": i + 1
                })
        
        # Detectar links
        links = []
        link_pattern = r'\[([^\]]+)\]\(([^)]+)\)'
        for match in re.finditer(link_pattern, content):
            links.append({
                "text": match.group(1),
                "url": match.group(2)
            })
        
        # Detectar imagens
        images = []
        image_pattern = r'!\[([^\]]*)\]\(([^)]+)\)'
        for match in re.finditer(image_pattern, content):
            images.append({
                "alt": match.group(1),
                "url": match.group(2)
            })
        
        # Detectar blocos de código
        code_blocks = []
        code_pattern = r'```([a-zA-Z]*)\n(.*?)```'
        for match in re.finditer(code_pattern, content, re.DOTALL):
            code_blocks.append({
                "language": match.group(1),
                "code": match.group(2)
            })
        
        return {
            "language": "markdown",
            "headers": headers,
            "links": links,
            "images": images,
            "code_blocks": code_blocks
        }
    
    def _analyze_text(self, content: str) -> Dict[str, Any]:
        """
        Análise de texto simples
        
        Args:
            content: Conteúdo do arquivo
            
        Returns:
            Dict: Resultado da análise
        """
        lines = content.splitlines()
        
        # Estatísticas básicas
        word_count = len(content.split())
        char_count = len(content)
        
        # Detectar possível estrutura
        structure = "unknown"
        if any(line.startswith("# ") for line in lines):
            structure = "markdown"
        elif any(line.startswith("<!DOCTYPE") for line in lines):
            structure = "html"
        elif any(line.startswith("import ") or line.startswith("from ") for line in lines):
            structure = "python"
        elif any(line.startswith("function ") or line.startswith("class ") for line in lines):
            structure = "javascript"
        
        return {
            "language": "text",
            "word_count": word_count,
            "char_count": char_count,
            "lines_count": len(lines),
            "possible_structure": structure
        }
