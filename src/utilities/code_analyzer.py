"""
Code Analyzer - Analyzer for code files to extract context
"""

import os
import re
from typing import Dict, List, Any, Optional

class CodeAnalyzer:
    """Analyzer for code files to extract context."""
    
    def __init__(self):
        """Initialize the code analyzer."""
        self.language_handlers = {
            ".py": self._analyze_python,
            ".js": self._analyze_javascript,
            ".java": self._analyze_java,
            ".cs": self._analyze_csharp,
            ".cpp": self._analyze_cpp,
            ".c": self._analyze_c,
            ".go": self._analyze_go,
            ".rb": self._analyze_ruby,
            ".php": self._analyze_php,
            ".ts": self._analyze_typescript
        }
    
    def analyze_file(self, file_path: str) -> Dict[str, Any]:
        """
        Analyze a code file and extract context.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Dictionary with analysis results
        """
        if not os.path.exists(file_path):
            return {"error": f"File not found: {file_path}"}
        
        _, ext = os.path.splitext(file_path)
        
        if ext in self.language_handlers:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                return self.language_handlers[ext](content, file_path)
            except Exception as e:
                return {"error": f"Error analyzing file: {e}"}
        else:
            return {"error": f"Unsupported file type: {ext}"}
    
    def _analyze_python(self, content: str, file_path: str) -> Dict[str, Any]:
        """
        Analyze Python code.
        
        Args:
            content: File content
            file_path: Path to the file
            
        Returns:
            Dictionary with analysis results
        """
        result = {
            "language": "Python",
            "file_path": file_path,
            "imports": [],
            "classes": [],
            "functions": [],
            "variables": []
        }
        
        try:
            import ast
            
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for name in node.names:
                        result["imports"].append(name.name)
                elif isinstance(node, ast.ImportFrom):
                    module = node.module or ""
                    for name in node.names:
                        result["imports"].append(f"{module}.{name.name}")
                elif isinstance(node, ast.ClassDef):
                    class_info = {
                        "name": node.name,
                        "methods": []
                    }
                    for item in node.body:
                        if isinstance(item, ast.FunctionDef):
                            class_info["methods"].append(item.name)
                    result["classes"].append(class_info)
                elif isinstance(node, ast.FunctionDef):
                    # Check if this is a top-level function (not a method)
                    if not any(isinstance(parent, ast.ClassDef) for parent in ast.iter_child_nodes(tree) if node in ast.iter_child_nodes(parent)):
                        result["functions"].append(node.name)
                elif isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name):
                            result["variables"].append(target.id)
        except ImportError:
            # Fall back to regex if ast is not available
            result = self._analyze_python_regex(content, file_path)
        except Exception as e:
            result["parse_error"] = str(e)
        
        return result
    
    def _analyze_python_regex(self, content: str, file_path: str) -> Dict[str, Any]:
        """
        Analyze Python code using regex (fallback).
        
        Args:
            content: File content
            file_path: Path to the file
            
        Returns:
            Dictionary with analysis results
        """
        result = {
            "language": "Python",
            "file_path": file_path,
            "imports": [],
            "classes": [],
            "functions": [],
            "variables": []
        }
        
        # Extract imports
        import_regex = r'^\s*import\s+(.+?)(?:\s+as\s+.+)?$'
        from_regex = r'^\s*from\s+(.+?)\s+import\s+(.+?)(?:\s+as\s+.+)?$'
        
        for line in content.split('\n'):
            import_match = re.match(import_regex, line)
            if import_match:
                imports = import_match.group(1).split(',')
                result["imports"].extend([imp.strip() for imp in imports])
                continue
                
            from_match = re.match(from_regex, line)
            if from_match:
                module = from_match.group(1)
                imports = from_match.group(2).split(',')
                result["imports"].extend([f"{module}.{imp.strip()}" for imp in imports])
        
        # Extract classes
        class_regex = r'^\s*class\s+(\w+)'
        result["classes"] = [{"name": name, "methods": []} for name in re.findall(class_regex, content, re.MULTILINE)]
        
        # Extract functions
        function_regex = r'^\s*def\s+(\w+)'
        result["functions"] = re.findall(function_regex, content, re.MULTILINE)
        
        # Extract variables (simple cases only)
        var_regex = r'^\s*(\w+)\s*='
        result["variables"] = re.findall(var_regex, content, re.MULTILINE)
        
        return result
    
    def _analyze_javascript(self, content: str, file_path: str) -> Dict[str, Any]:
        """
        Analyze JavaScript code.
        
        Args:
            content: File content
            file_path: Path to the file
            
        Returns:
            Dictionary with analysis results
        """
        result = {
            "language": "JavaScript",
            "file_path": file_path,
            "imports": [],
            "classes": [],
            "functions": [],
            "variables": []
        }
        
        # Extract imports
        import_regex = r'import\s+.*?from\s+[\'"]([^\'"]+)[\'"]'
        require_regex = r'(?:const|let|var)\s+.*?=\s*require\([\'"]([^\'"]+)[\'"]\)'
        
        result["imports"] = re.findall(import_regex, content)
        result["imports"].extend(re.findall(require_regex, content))
        
        # Extract classes
        class_regex = r'class\s+(\w+)'
        result["classes"] = [{"name": name} for name in re.findall(class_regex, content)]
        
        # Extract functions
        function_regex = r'function\s+(\w+)'
        result["functions"] = re.findall(function_regex, content)
        
        # Extract arrow functions assigned to variables
        arrow_func_regex = r'(?:const|let|var)\s+(\w+)\s*=\s*\([^\)]*\)\s*=>'
        result["functions"].extend(re.findall(arrow_func_regex, content))
        
        # Extract variables
        var_regex = r'(?:var|let|const)\s+(\w+)\s*='
        result["variables"] = re.findall(var_regex, content)
        
        return result
    
    def _analyze_java(self, content: str, file_path: str) -> Dict[str, Any]:
        """
        Analyze Java code.
        
        Args:
            content: File content
            file_path: Path to the file
            
        Returns:
            Dictionary with analysis results
        """
        result = {
            "language": "Java",
            "file_path": file_path,
            "imports": [],
            "classes": [],
            "methods": [],
            "fields": []
        }
        
        # Extract package
        package_regex = r'package\s+([^;]+);'
        package_match = re.search(package_regex, content)
        if package_match:
            result["package"] = package_match.group(1)
        
        # Extract imports
        import_regex = r'import\s+([^;]+);'
        result["imports"] = re.findall(import_regex, content)
        
        # Extract classes
        class_regex = r'(?:public|private|protected)?\s*(?:abstract|final)?\s*class\s+(\w+)'
        result["classes"] = [{"name": name} for name in re.findall(class_regex, content)]
        
        # Extract methods
        method_regex = r'(?:public|private|protected)?\s*(?:static)?\s*(?:final)?\s*\w+\s+(\w+)\s*\([^\)]*\)'
        result["methods"] = re.findall(method_regex, content)
        
        # Extract fields
        field_regex = r'(?:public|private|protected)?\s*(?:static)?\s*(?:final)?\s*\w+\s+(\w+)\s*(?:=|;)'
        result["fields"] = re.findall(field_regex, content)
        
        return result
    
    def _analyze_csharp(self, content: str, file_path: str) -> Dict[str, Any]:
        """
        Analyze C# code.
        
        Args:
            content: File content
            file_path: Path to the file
            
        Returns:
            Dictionary with analysis results
        """
        result = {
            "language": "C#",
            "file_path": file_path,
            "usings": [],
            "namespaces": [],
            "classes": [],
            "methods": [],
            "properties": []
        }
        
        # Extract usings
        using_regex = r'using\s+([^;]+);'
        result["usings"] = re.findall(using_regex, content)
        
        # Extract namespaces
        namespace_regex = r'namespace\s+([^\s{]+)'
        result["namespaces"] = re.findall(namespace_regex, content)
        
        # Extract classes
        class_regex = r'(?:public|private|protected|internal)?\s*(?:abstract|sealed)?\s*class\s+(\w+)'
        result["classes"] = [{"name": name} for name in re.findall(class_regex, content)]
        
        # Extract methods
        method_regex = r'(?:public|private|protected|internal)?\s*(?:static)?\s*(?:virtual|override|abstract)?\s*\w+\s+(\w+)\s*\([^\)]*\)'
        result["methods"] = re.findall(method_regex, content)
        
        # Extract properties
        property_regex = r'(?:public|private|protected|internal)?\s*(?:static)?\s*(?:virtual|override|abstract)?\s*\w+\s+(\w+)\s*\{'
        result["properties"] = re.findall(property_regex, content)
        
        return result
    
    def _analyze_cpp(self, content: str, file_path: str) -> Dict[str, Any]:
        """
        Analyze C++ code.
        
        Args:
            content: File content
            file_path: Path to the file
            
        Returns:
            Dictionary with analysis results
        """
        result = {
            "language": "C++",
            "file_path": file_path,
            "includes": [],
            "classes": [],
            "functions": [],
            "variables": []
        }
        
        # Extract includes
        include_regex = r'#include\s+[<"]([^>"]+)[>"]'
        result["includes"] = re.findall(include_regex, content)
        
        # Extract classes
        class_regex = r'class\s+(\w+)'
        result["classes"] = [{"name": name} for name in re.findall(class_regex, content)]
        
        # Extract functions
        function_regex = r'(?:[\w:~]+)\s+(\w+)\s*\([^\)]*\)\s*(?:const)?\s*(?:noexcept)?\s*(?:override)?\s*(?:final)?\s*(?:=\s*(?:default|delete|0))?\s*(?:{\s*)?'
        result["functions"] = re.findall(function_regex, content)
        
        # Extract variables (simple cases only)
        var_regex = r'(?:int|float|double|char|bool|auto|string)\s+(\w+)\s*(?:=|;)'
        result["variables"] = re.findall(var_regex, content)
        
        return result
    
    def _analyze_c(self, content: str, file_path: str) -> Dict[str, Any]:
        """
        Analyze C code.
        
        Args:
            content: File content
            file_path: Path to the file
            
        Returns:
            Dictionary with analysis results
        """
        result = {
            "language": "C",
            "file_path": file_path,
            "includes": [],
            "functions": [],
            "structs": [],
            "variables": []
        }
        
        # Extract includes
        include_regex = r'#include\s+[<"]([^>"]+)[>"]'
        result["includes"] = re.findall(include_regex, content)
        
        # Extract functions
        function_regex = r'(?:\w+)\s+(\w+)\s*\([^\)]*\)\s*(?:{\s*)?'
        result["functions"] = re.findall(function_regex, content)
        
        # Extract structs
        struct_regex = r'struct\s+(\w+)'
        result["structs"] = re.findall(struct_regex, content)
        
        # Extract variables (simple cases only)
        var_regex = r'(?:int|float|double|char|void\s*\*|bool)\s+(\w+)\s*(?:=|;)'
        result["variables"] = re.findall(var_regex, content)
        
        return result
    
    def _analyze_go(self, content: str, file_path: str) -> Dict[str, Any]:
        """
        Analyze Go code.
        
        Args:
            content: File content
            file_path: Path to the file
            
        Returns:
            Dictionary with analysis results
        """
        result = {
            "language": "Go",
            "file_path": file_path,
            "imports": [],
            "structs": [],
            "functions": [],
            "variables": []
        }
        
        # Extract package
        package_regex = r'package\s+(\w+)'
        package_match = re.search(package_regex, content)
        if package_match:
            result["package"] = package_match.group(1)
        
        # Extract imports
        import_regex = r'import\s+(?:"([^"]+)"|[\(\s]+(?:"([^"]+)")+[\)\s]+)'
        for match in re.finditer(import_regex, content):
            if match.group(1):
                result["imports"].append(match.group(1))
            elif match.group(2):
                result["imports"].append(match.group(2))
        
        # Extract structs
        struct_regex = r'type\s+(\w+)\s+struct'
        result["structs"] = re.findall(struct_regex, content)
        
        # Extract functions
        function_regex = r'func\s+(?:\([^)]+\)\s+)?(\w+)'
        result["functions"] = re.findall(function_regex, content)
        
        # Extract variables (simple cases only)
        var_regex = r'var\s+(\w+)'
        result["variables"] = re.findall(var_regex, content)
        
        return result
    
    def _analyze_ruby(self, content: str, file_path: str) -> Dict[str, Any]:
        """
        Analyze Ruby code.
        
        Args:
            content: File content
            file_path: Path to the file
            
        Returns:
            Dictionary with analysis results
        """
        result = {
            "language": "Ruby",
            "file_path": file_path,
            "requires": [],
            "classes": [],
            "methods": [],
            "variables": []
        }
        
        # Extract requires
        require_regex = r'require\s+[\'"]([^\'"]+)[\'"]'
        result["requires"] = re.findall(require_regex, content)
        
        # Extract classes
        class_regex = r'class\s+(\w+)'
        result["classes"] = [{"name": name} for name in re.findall(class_regex, content)]
        
        # Extract methods
        method_regex = r'def\s+(\w+)'
        result["methods"] = re.findall(method_regex, content)
        
        # Extract variables (simple cases only)
        var_regex = r'@(\w+)'
        result["variables"] = re.findall(var_regex, content)
        
        return result
    
    def _analyze_php(self, content: str, file_path: str) -> Dict[str, Any]:
        """
        Analyze PHP code.
        
        Args:
            content: File content
            file_path: Path to the file
            
        Returns:
            Dictionary with analysis results
        """
        result = {
            "language": "PHP",
            "file_path": file_path,
            "namespace": None,
            "uses": [],
            "classes": [],
            "functions": [],
            "variables": []
        }
        
        # Extract namespace
        namespace_regex = r'namespace\s+([^;]+);'
        namespace_match = re.search(namespace_regex, content)
        if namespace_match:
            result["namespace"] = namespace_match.group(1)
        
        # Extract uses
        use_regex = r'use\s+([^;]+);'
        result["uses"] = re.findall(use_regex, content)
        
        # Extract classes
        class_regex = r'class\s+(\w+)'
        result["classes"] = [{"name": name} for name in re.findall(class_regex, content)]
        
        # Extract functions
        function_regex = r'function\s+(\w+)'
        result["functions"] = re.findall(function_regex, content)
        
        # Extract variables (simple cases only)
        var_regex = r'\$(\w+)'
        result["variables"] = list(set(re.findall(var_regex, content)))
        
        return result
    
    def _analyze_typescript(self, content: str, file_path: str) -> Dict[str, Any]:
        """
        Analyze TypeScript code.
        
        Args:
            content: File content
            file_path: Path to the file
            
        Returns:
            Dictionary with analysis results
        """
        result = {
            "language": "TypeScript",
            "file_path": file_path,
            "imports": [],
            "interfaces": [],
            "classes": [],
            "functions": [],
            "variables": []
        }
        
        # Extract imports
        import_regex = r'import\s+.*?from\s+[\'"]([^\'"]+)[\'"]'
        result["imports"] = re.findall(import_regex, content)
        
        # Extract interfaces
        interface_regex = r'interface\s+(\w+)'
        result["interfaces"] = re.findall(interface_regex, content)
        
        # Extract classes
        class_regex = r'class\s+(\w+)'
        result["classes"] = [{"name": name} for name in re.findall(class_regex, content)]
        
        # Extract functions
        function_regex = r'function\s+(\w+)'
        result["functions"] = re.findall(function_regex, content)
        
        # Extract arrow functions assigned to variables
        arrow_func_regex = r'(?:const|let|var)\s+(\w+)\s*=\s*\([^\)]*\)\s*=>'
        result["functions"].extend(re.findall(arrow_func_regex, content))
        
        # Extract variables
        var_regex = r'(?:var|let|const)\s+(\w+)\s*(?::|=)'
        result["variables"] = re.findall(var_regex, content)
        
        return result
