from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="mcp-continuity-service",
    version="1.0.0",
    author="MCP Continuity Team",
    author_email="contact@mcp-continuity.dev",
    description="Professional continuity service for LLMs with MCP integration",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/mcp-continuity/mcp-continuity-service",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.9",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "mcp-continuity=src.cli:main",
            "mcp-continuity-server=src.api.main:run_server",
            "mcp-continuity-ui=frontend.streamlit_app:main"
        ]
    },
    include_package_data=True,
    package_data={
        "": ["*.txt", "*.md", "*.yml", "*.yaml", "*.json"],
    },
    keywords="ai, llm, continuity, mcp, context, memory, agents",
    project_urls={
        "Bug Reports": "https://github.com/mcp-continuity/mcp-continuity-service/issues",
        "Source": "https://github.com/mcp-continuity/mcp-continuity-service",
        "Documentation": "https://docs.mcp-continuity.dev",
    },
)
