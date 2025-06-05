# Integration Tests

This directory contains integration tests for the Continuity Protocol.

Integration tests verify that different components of the system work together correctly.

## Running Integration Tests

To run the integration tests:

```bash
pytest tests/integration
```

## Test Categories

- **API Tests**: Verify the REST API functionality
- **Transport Tests**: Test different transport mechanisms (stdio, HTTP)
- **Client Tests**: Test different client implementations
- **End-to-End Tests**: Full system tests with real data flow