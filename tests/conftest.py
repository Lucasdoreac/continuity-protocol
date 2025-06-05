"""
Configuration for pytest.

This module contains fixtures and configuration for pytest.
"""

import sys
import os
import pytest
import logging
import shutil
import tempfile

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("continuity-protocol-tests")

# Add src directory to path for imports
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, "src"))

# Try to import key modules to verify setup
try:
    import src.continuity_protocol
    logger.info("Successfully imported src.continuity_protocol")
except ImportError as e:
    logger.warning(f"Failed to import src.continuity_protocol: {e}")
    try:
        import continuity_protocol
        logger.info("Successfully imported continuity_protocol")
    except ImportError as e2:
        logger.warning(f"Failed to import continuity_protocol: {e2}")

class MockModule:
    """Mock module for tests when real imports fail."""
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

# Mock modules if needed for tests to run
try:
    import psutil
except ImportError:
    sys.modules['psutil'] = MockModule(
        Process=lambda: MockModule(
            memory_info=lambda: MockModule(rss=1000000),
            pid=12345
        ),
        cpu_percent=lambda: 50.0,
        virtual_memory=lambda: MockModule(percent=60.0),
        disk_usage=lambda: MockModule(percent=70.0)
    )
    logger.warning("Using mock psutil module")

@pytest.fixture(scope="session")
def temp_dir():
    """Create a temporary directory for tests."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)

@pytest.fixture(scope="session")
def test_data_dir(temp_dir):
    """Create a data directory structure for tests."""
    # Create necessary subdirectories
    os.makedirs(os.path.join(temp_dir, "contexts", "default"), exist_ok=True)
    os.makedirs(os.path.join(temp_dir, "contexts", "_context_history"), exist_ok=True)
    os.makedirs(os.path.join(temp_dir, "sessions"), exist_ok=True)
    os.makedirs(os.path.join(temp_dir, "llmops"), exist_ok=True)
    os.makedirs(os.path.join(temp_dir, "temp"), exist_ok=True)
    
    return temp_dir

@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """
    Setup the test environment.
    
    This fixture:
    - Ensures src directory is in the Python path
    - Creates necessary data directories
    """
    # Print diagnostic information
    logger.info(f"Python path: {sys.path}")
    logger.info(f"Project root: {project_root}")
    logger.info(f"Current working directory: {os.getcwd()}")
    
    # Set up data directories
    data_dir = os.path.join(project_root, "data")
    logger.info(f"Setting up data directories in {data_dir}")
    
    # Ensure data directories exist
    dirs_to_create = [
        os.path.join(data_dir, "contexts", "default"),
        os.path.join(data_dir, "contexts", "_context_history"),
        os.path.join(data_dir, "sessions"),
        os.path.join(data_dir, "llmops"),
        os.path.join(data_dir, "temp")
    ]
    
    for directory in dirs_to_create:
        try:
            os.makedirs(directory, exist_ok=True)
            logger.info(f"Created directory: {directory}")
        except Exception as e:
            logger.error(f"Failed to create directory {directory}: {e}")
    
    yield