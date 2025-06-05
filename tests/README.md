# Continuity Protocol Tests

This directory contains tests for the Continuity Protocol.

## Test Structure

- **Unit Tests** (`unit/`): Tests for individual components
  - `test_server.py`: Tests for the MCP server
  - `test_session_tools.py`: Tests for session management tools
  - `test_context_tools.py`: Tests for context management tools
  - `test_system_tools.py`: Tests for system management tools

- **Integration Tests** (`integration/`): Tests for component interactions
  - Tests for API endpoints
  - Tests for transport mechanisms
  - Tests for cross-component functionality

- **Performance Tests** (`performance/`): Tests for system performance
  - Load tests
  - Stress tests
  - Endurance tests

## Running Tests

To run all tests:

```bash
pytest
```

To run unit tests only:

```bash
pytest tests/unit/
```

To run with coverage:

```bash
pytest --cov=src.continuity_protocol
```

## CI/CD

Tests are automatically run in GitHub Actions for Python 3.8, 3.9, and 3.10.

## Writing Tests

When writing new tests:

1. Place unit tests in `unit/`
2. Place integration tests in `integration/`
3. Place performance tests in `performance/`
4. Use meaningful test names with `test_` prefix
5. Add clear docstrings explaining the test purpose
6. Use fixtures from `conftest.py` where appropriate