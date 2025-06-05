from setuptools import setup, find_packages

# Read version from __init__.py
with open("src/continuity_protocol/__init__.py", "r") as f:
    for line in f:
        if line.startswith("__version__"):
            version = line.split("=")[1].strip().strip('"').strip("'")
            break

# Read long description from README.md
with open("README.md", "r") as f:
    long_description = f.read()

setup(
    name="continuity-protocol",
    version=version,
    description="A Model Context Protocol (MCP) implementation for conversation continuity and context preservation",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="MCP Continuity Team",
    author_email="noreply@example.com",
    url="https://github.com/continuity-protocol/continuity-protocol",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    include_package_data=True,
    python_requires=">=3.8",
    install_requires=[
        "psutil>=5.9.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=3.0.0",
            "black>=22.0.0",
            "isort>=5.10.0",
            "mypy>=0.950",
        ],
        "http": [
            "fastapi>=0.85.0",
            "uvicorn>=0.18.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "continuity-server=continuity_protocol.server:run_server",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    keywords="mcp, continuity, context, llm, ai, model, protocol",
)