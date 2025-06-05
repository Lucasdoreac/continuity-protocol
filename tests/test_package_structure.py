"""
Basic tests to verify the package structure.

These tests don't rely on actual functionality, just verify that 
the package structure is correct.
"""

import os
import sys
import importlib

def test_project_structure():
    """Verify that the project structure is correct."""
    # Get the project root directory
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # Essential directories should exist
    assert os.path.isdir(os.path.join(project_root, "src")), "src directory missing"
    assert os.path.isdir(os.path.join(project_root, "tests")), "tests directory missing"
    assert os.path.isdir(os.path.join(project_root, "data")), "data directory missing"
    
    # Essential files should exist
    assert os.path.isfile(os.path.join(project_root, "setup.py")), "setup.py missing"
    assert os.path.isfile(os.path.join(project_root, "README.md")), "README.md missing"
    assert os.path.isfile(os.path.join(project_root, "requirements.txt")), "requirements.txt missing"
    
    # Package structure should be correct
    assert os.path.isdir(os.path.join(project_root, "src", "continuity_protocol")), "continuity_protocol package missing"
    assert os.path.isfile(os.path.join(project_root, "src", "continuity_protocol", "__init__.py")), "__init__.py missing"
    assert os.path.isfile(os.path.join(project_root, "src", "continuity_protocol", "server.py")), "server.py missing"

def test_package_importable():
    """Verify that the package can be imported."""
    # Try to import the package
    try:
        import src.continuity_protocol
        # Successfully imported
        assert True
    except ImportError:
        try:
            # Try without the src prefix
            import continuity_protocol
            # Successfully imported
            assert True
        except ImportError:
            # Neither import worked
            assert False, "Failed to import continuity_protocol package"