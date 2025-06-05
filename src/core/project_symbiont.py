"""
Project Symbiont - Establishes symbiotic relationship with projects
"""

import os
import json
import logging
import subprocess
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple, Set


class ProjectSymbiont:
    """
    Establishes a symbiotic relationship with projects,
    becoming part of the project ecosystem.
    """
    
    def __init__(self, memory_fusion):
        """
        Initialize the Project Symbiont.
        
        Args:
            memory_fusion: The MemoryFusion instance to use for storing project data
        """
        self.memory_fusion = memory_fusion
        self.active_symbiosis = {}
        self.logger = logging.getLogger("continuity.project_symbiont")
    
    def establish_symbiosis(self, project_path: str, project_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Establishes symbiosis with a project.
        
        Args:
            project_path: Path to the project
            project_name: Optional name for the project. If None, the directory name is used.
            
        Returns:
            Dictionary containing project data
        """
        project_path = os.path.abspath(project_path)
        if not os.path.exists(project_path):
            raise FileNotFoundError(f"Project path does not exist: {project_path}")
            
        project_name = project_name or os.path.basename(project_path)
        
        self.logger.info(f"Establishing symbiosis with project: {project_name} at {project_path}")
        
        # Extract project DNA
        project_dna = self._extract_project_dna(project_path)
        
        # Establish symbiosis
        self.active_symbiosis[project_path] = {
            "name": project_name,
            "path": project_path,
            "dna": project_dna,
            "symbiosis_established": datetime.now().isoformat(),
            "neural_connections": self._establish_neural_connections(project_dna)
        }
        
        # Fuse with memory
        self.memory_fusion.fuse_project(project_path, self.active_symbiosis[project_path])
        
        return self.active_symbiosis[project_path]
    
    def _extract_project_dna(self, project_path: str) -> Dict[str, Any]:
        """
        Extracts the DNA of a project (structure, dependencies, patterns).
        
        Args:
            project_path: Path to the project
            
        Returns:
            Dictionary containing project DNA
        """
        dna = {
            "structure": self._analyze_project_structure(project_path),
            "git_info": self._get_git_info(project_path),
            "language_distribution": self._analyze_language_distribution(project_path),
            "dependencies": self._extract_dependencies(project_path),
            "key_files": self._identify_key_files(project_path),
            "extraction_time": datetime.now().isoformat()
        }
        
        return dna
    
    def _analyze_project_structure(self, project_path: str) -> Dict[str, Any]:
        """
        Analyzes the structure of a project.
        
        Args:
            project_path: Path to the project
            
        Returns:
            Dictionary containing project structure information
        """
        structure = {
            "directories": [],
            "files": [],
            "file_count": 0,
            "directory_count": 0,
            "total_size_bytes": 0
        }
        
        # Skip these directories
        skip_dirs = {'.git', '.github', 'node_modules', 'venv', '__pycache__', '.vscode', '.idea'}
        
        # Walk through the project
        for root, dirs, files in os.walk(project_path):
            # Skip directories in skip_dirs
            dirs[:] = [d for d in dirs if d not in skip_dirs]
            
            # Get relative path
            rel_path = os.path.relpath(root, project_path)
            if rel_path != '.':
                structure["directories"].append(rel_path)
            
            # Process files
            for file in files:
                file_path = os.path.join(root, file)
                rel_file_path = os.path.join(rel_path, file) if rel_path != '.' else file
                
                # Skip large files and binary files
                try:
                    if os.path.getsize(file_path) > 1024 * 1024:  # Skip files larger than 1MB
                        continue
                        
                    structure["files"].append(rel_file_path)
                    structure["file_count"] += 1
                    structure["total_size_bytes"] += os.path.getsize(file_path)
                except Exception as e:
                    self.logger.warning(f"Error processing file {file_path}: {e}")
            
            structure["directory_count"] += 1
        
        return structure
    
    def _get_git_info(self, project_path: str) -> Dict[str, Any]:
        """
        Gets Git information for a project.
        
        Args:
            project_path: Path to the project
            
        Returns:
            Dictionary containing Git information
        """
        git_info = {
            "is_git_repo": False,
            "branch": None,
            "last_commit": None,
            "remote_url": None
        }
        
        try:
            # Check if it's a git repository
            result = subprocess.run(
                ["git", "rev-parse", "--is-inside-work-tree"],
                cwd=project_path,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=False
            )
            
            if result.returncode != 0:
                return git_info
                
            git_info["is_git_repo"] = True
            
            # Get current branch
            result = subprocess.run(
                ["git", "branch", "--show-current"],
                cwd=project_path,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=False
            )
            
            if result.returncode == 0:
                git_info["branch"] = result.stdout.strip()
            
            # Get last commit
            result = subprocess.run(
                ["git", "log", "-1", "--pretty=format:%h - %s (%an, %ar)"],
                cwd=project_path,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=False
            )
            
            if result.returncode == 0:
                git_info["last_commit"] = result.stdout.strip()
            
            # Get remote URL
            result = subprocess.run(
                ["git", "config", "--get", "remote.origin.url"],
                cwd=project_path,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=False
            )
            
            if result.returncode == 0:
                git_info["remote_url"] = result.stdout.strip()
                
        except Exception as e:
            self.logger.warning(f"Error getting git info: {e}")
        
        return git_info
    
    def _analyze_language_distribution(self, project_path: str) -> Dict[str, int]:
        """
        Analyzes the distribution of programming languages in a project.
        
        Args:
            project_path: Path to the project
            
        Returns:
            Dictionary mapping language extensions to file counts
        """
        language_counts = {}
        
        # Skip these directories
        skip_dirs = {'.git', '.github', 'node_modules', 'venv', '__pycache__', '.vscode', '.idea'}
        
        # Walk through the project
        for root, dirs, files in os.walk(project_path):
            # Skip directories in skip_dirs
            dirs[:] = [d for d in dirs if d not in skip_dirs]
            
            # Count file extensions
            for file in files:
                _, ext = os.path.splitext(file)
                if ext:
                    ext = ext.lower()
                    language_counts[ext] = language_counts.get(ext, 0) + 1
        
        return language_counts
    
    def _extract_dependencies(self, project_path: str) -> Dict[str, List[str]]:
        """
        Extracts dependencies from common dependency files.
        
        Args:
            project_path: Path to the project
            
        Returns:
            Dictionary mapping dependency file types to lists of dependencies
        """
        dependencies = {}
        
        # Check for package.json (Node.js)
        package_json_path = os.path.join(project_path, 'package.json')
        if os.path.exists(package_json_path):
            try:
                with open(package_json_path, 'r', encoding='utf-8') as f:
                    package_data = json.load(f)
                    
                node_deps = []
                if 'dependencies' in package_data:
                    node_deps.extend([f"{dep}@{ver}" for dep, ver in package_data['dependencies'].items()])
                if 'devDependencies' in package_data:
                    node_deps.extend([f"{dep}@{ver}" for dep, ver in package_data['devDependencies'].items()])
                    
                dependencies['node'] = node_deps
            except Exception as e:
                self.logger.warning(f"Error parsing package.json: {e}")
        
        # Check for requirements.txt (Python)
        requirements_path = os.path.join(project_path, 'requirements.txt')
        if os.path.exists(requirements_path):
            try:
                with open(requirements_path, 'r', encoding='utf-8') as f:
                    python_deps = [line.strip() for line in f if line.strip() and not line.startswith('#')]
                dependencies['python'] = python_deps
            except Exception as e:
                self.logger.warning(f"Error parsing requirements.txt: {e}")
        
        # Check for pom.xml (Java/Maven)
        pom_path = os.path.join(project_path, 'pom.xml')
        if os.path.exists(pom_path):
            dependencies['java'] = ["Maven project detected - dependencies not parsed"]
        
        # Check for build.gradle (Java/Gradle)
        gradle_path = os.path.join(project_path, 'build.gradle')
        if os.path.exists(gradle_path):
            dependencies['java'] = ["Gradle project detected - dependencies not parsed"]
        
        return dependencies
    
    def _identify_key_files(self, project_path: str) -> List[str]:
        """
        Identifies key files in a project.
        
        Args:
            project_path: Path to the project
            
        Returns:
            List of key file paths (relative to project root)
        """
        key_files = []
        
        # Common key files to look for
        common_key_files = [
            'README.md',
            'package.json',
            'requirements.txt',
            'setup.py',
            'Dockerfile',
            'docker-compose.yml',
            '.gitignore',
            'Makefile',
            'main.py',
            'index.js',
            'app.py',
            'server.js',
            'config.json',
            '.env.example'
        ]
        
        for file in common_key_files:
            file_path = os.path.join(project_path, file)
            if os.path.exists(file_path) and os.path.isfile(file_path):
                key_files.append(file)
        
        return key_files
    
    def _establish_neural_connections(self, project_dna: Dict[str, Any]) -> Dict[str, Any]:
        """
        Establishes neural connections based on project DNA.
        
        Args:
            project_dna: Project DNA dictionary
            
        Returns:
            Dictionary containing neural connection information
        """
        # This is a placeholder for more advanced neural connection logic
        return {
            "connection_strength": len(project_dna.get("structure", {}).get("files", [])) / 100,
            "connection_type": "symbiotic",
            "established": datetime.now().isoformat()
        }
    
    def update_project_state(self, project_path: str, current_file: Optional[str] = None, 
                            current_focus: Optional[str] = None) -> Dict[str, Any]:
        """
        Updates the state of a project.
        
        Args:
            project_path: Path to the project
            current_file: Optional path to the current file being edited
            current_focus: Optional description of the current focus
            
        Returns:
            Updated project state dictionary
        """
        project_path = os.path.abspath(project_path)
        
        if project_path not in self.active_symbiosis:
            raise ValueError(f"No active symbiosis for project: {project_path}")
        
        project_state = self.active_symbiosis[project_path]
        
        # Update state
        if current_file:
            project_state["current_file"] = current_file
            
        if current_focus:
            project_state["current_focus"] = current_focus
            
        project_state["last_updated"] = datetime.now().isoformat()
        
        # Update git info if it's a git repo
        if project_state.get("dna", {}).get("git_info", {}).get("is_git_repo", False):
            project_state["dna"]["git_info"] = self._get_git_info(project_path)
        
        # Fuse with memory
        self.memory_fusion.fuse_project(project_path, project_state)
        
        return project_state
    
    def get_project_state(self, project_path: str) -> Dict[str, Any]:
        """
        Gets the current state of a project.
        
        Args:
            project_path: Path to the project
            
        Returns:
            Project state dictionary
        """
        project_path = os.path.abspath(project_path)
        
        if project_path not in self.active_symbiosis:
            raise ValueError(f"No active symbiosis for project: {project_path}")
            
        return self.active_symbiosis[project_path]
    
    def list_active_projects(self) -> List[Dict[str, Any]]:
        """
        Lists all active projects.
        
        Returns:
            List of project state dictionaries
        """
        return list(self.active_symbiosis.values())
    
    def terminate_symbiosis(self, project_path: str) -> None:
        """
        Terminates symbiosis with a project.
        
        Args:
            project_path: Path to the project
        """
        project_path = os.path.abspath(project_path)
        
        if project_path not in self.active_symbiosis:
            raise ValueError(f"No active symbiosis for project: {project_path}")
            
        # Save final state
        final_state = self.active_symbiosis[project_path]
        final_state["symbiosis_terminated"] = datetime.now().isoformat()
        
        # Fuse with memory
        self.memory_fusion.fuse_project(project_path, final_state)
        
        # Remove from active symbiosis
        del self.active_symbiosis[project_path]
        
        self.logger.info(f"Symbiosis terminated for project: {final_state.get('name', project_path)}")
