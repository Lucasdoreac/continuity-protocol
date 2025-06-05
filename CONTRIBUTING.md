# Contributing to Continuity Protocol

Thank you for your interest in contributing to Continuity Protocol! This document provides guidelines and instructions for contributing to this project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Environment](#development-environment)
- [Branching Strategy](#branching-strategy)
- [Making Changes](#making-changes)
- [Testing](#testing)
- [Pull Requests](#pull-requests)
- [Code Style](#code-style)
- [Documentation](#documentation)

## Code of Conduct

This project adheres to a Code of Conduct that all contributors are expected to follow. Please read [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) before contributing.

## Getting Started

1. Fork the repository on GitHub
2. Clone your fork locally
3. Add the original repository as a remote called "upstream"
4. Create a new branch for your changes

```bash
# Clone your fork
git clone https://github.com/YOUR-USERNAME/continuity-protocol.git
cd continuity-protocol

# Add upstream remote
git remote add upstream https://github.com/continuity-protocol/continuity-protocol.git

# Create a new branch
git checkout -b feature/your-feature-name
```

## Development Environment

1. Create and activate a virtual environment
2. Install the package in development mode

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode with development dependencies
pip install -e ".[dev]"
```

## Branching Strategy

- `main`: The main branch contains the latest stable release
- `develop`: The development branch contains the latest changes
- Feature branches: Create a new branch for each feature or bugfix

Branch naming conventions:
- `feature/your-feature-name`: For new features
- `bugfix/issue-description`: For bug fixes
- `docs/what-you-documented`: For documentation changes
- `refactor/what-you-refactored`: For code refactoring

## Making Changes

1. Make sure you're working on the correct branch
2. Make your changes
3. Commit your changes with a clear commit message
4. Pull the latest changes from upstream
5. Push your changes to your fork

```bash
# Make sure you're on your branch
git checkout feature/your-feature-name

# Make your changes...

# Commit your changes
git add .
git commit -m "Add feature X"

# Pull latest changes from upstream develop branch
git pull upstream develop

# Push to your fork
git push origin feature/your-feature-name
```

## Testing

Before submitting a pull request, make sure all tests pass:

```bash
# Run all tests
pytest

# Run tests with coverage
pytest --cov=continuity_protocol

# Run tests for a specific module
pytest tests/unit/test_server.py
```

When adding new features, please add tests to cover your code.

## Pull Requests

1. Create a pull request from your feature branch to the `develop` branch
2. Fill out the pull request template
3. Request a review from a maintainer
4. Address any feedback or changes requested
5. Once approved, your pull request will be merged

## Code Style

This project uses:
- Black for code formatting
- isort for import sorting
- mypy for type checking

You can format your code with:

```bash
# Format code
black src tests

# Sort imports
isort src tests

# Check types
mypy src
```

These checks will also run automatically in the CI pipeline.

## Documentation

When adding new features, please update the documentation:

- Add docstrings to all functions, classes, and methods
- Update the API documentation if necessary
- Add examples for new features
- Update the architecture documentation if you change the system design

Documentation is written in Markdown and is located in the `docs/` directory.

## Thank You!

Your contributions help make Continuity Protocol better for everyone. We appreciate your time and effort!