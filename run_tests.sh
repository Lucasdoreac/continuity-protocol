#!/bin/bash
# Test runner script for CONTINUITY Protocol

set -e

# Create required directories if they don't exist
mkdir -p data/contexts/default
mkdir -p data/contexts/_context_history
mkdir -p data/sessions
mkdir -p data/llmops
mkdir -p data/temp

# Set Python path
export PYTHONPATH=$PWD

# Show usage information
show_help() {
  echo "CONTINUITY Protocol Test Runner"
  echo "Usage: $0 [options]"
  echo ""
  echo "Options:"
  echo "  --all            Run all tests"
  echo "  --unit           Run all unit tests"
  echo "  --integration    Run integration tests"
  echo "  --coverage       Generate coverage report"
  echo "  --server         Run only server tests"
  echo "  --tools          Run only tools tests"
  echo "  --verbose        Run with verbose output"
  echo "  --help           Show this help message"
  echo ""
  echo "Examples:"
  echo "  $0 --all --verbose   Run all tests with verbose output"
  echo "  $0 --unit --coverage Run unit tests with coverage report"
}

# Default options
RUN_ALL=0
RUN_UNIT=0
RUN_INTEGRATION=0
RUN_COVERAGE=0
RUN_SERVER=0
RUN_TOOLS=0
VERBOSE=0

# Process command line arguments
while [[ $# -gt 0 ]]; do
  case "$1" in
    --all)
      RUN_ALL=1
      ;;
    --unit)
      RUN_UNIT=1
      ;;
    --integration)
      RUN_INTEGRATION=1
      ;;
    --coverage)
      RUN_COVERAGE=1
      ;;
    --server)
      RUN_SERVER=1
      ;;
    --tools)
      RUN_TOOLS=1
      ;;
    --verbose)
      VERBOSE=1
      ;;
    --help)
      show_help
      exit 0
      ;;
    *)
      echo "Unknown option: $1"
      show_help
      exit 1
      ;;
  esac
  shift
done

# If no specific test type is specified, run all tests
if [ $RUN_ALL -eq 0 ] && [ $RUN_UNIT -eq 0 ] && [ $RUN_INTEGRATION -eq 0 ] && [ $RUN_SERVER -eq 0 ] && [ $RUN_TOOLS -eq 0 ]; then
  RUN_ALL=1
fi

# Set up command options
PYTEST_OPTS=""
if [ $VERBOSE -eq 1 ]; then
  PYTEST_OPTS="-v"
fi

# Function to run specific tests
run_tests() {
  test_files=$1
  echo "Running tests: $test_files"
  if [ $RUN_COVERAGE -eq 1 ]; then
    pytest --cov=src.continuity_protocol $test_files $PYTEST_OPTS
  else
    pytest $test_files $PYTEST_OPTS
  fi
}

# Basic package structure tests always run
echo "=== Running basic package structure tests ==="
run_tests "tests/test_package_structure.py"

# Run tests based on options
if [ $RUN_ALL -eq 1 ] || [ $RUN_UNIT -eq 1 ] || [ $RUN_SERVER -eq 1 ]; then
  echo ""
  echo "=== Running server tests ==="
  run_tests "tests/unit/test_server.py tests/unit/test_server_advanced.py"
fi

if [ $RUN_ALL -eq 1 ] || [ $RUN_UNIT -eq 1 ] || [ $RUN_TOOLS -eq 1 ]; then
  echo ""
  echo "=== Running tools tests ==="
  run_tests "tests/unit/test_context_tools.py tests/unit/test_session_tools.py tests/unit/test_system_tools.py tests/unit/test_tools_combined.py"
fi

if [ $RUN_ALL -eq 1 ] || [ $RUN_INTEGRATION -eq 1 ]; then
  echo ""
  echo "=== Running integration tests ==="
  run_tests "tests/integration/test_full_server_workflow.py"
fi

# If coverage is enabled and we're running all tests, generate a comprehensive report
if [ $RUN_COVERAGE -eq 1 ] && [ $RUN_ALL -eq 1 ]; then
  echo ""
  echo "=== Generating comprehensive coverage report ==="
  pytest --cov=src.continuity_protocol --cov-report=html tests/
  echo "Coverage report generated in htmlcov/ directory"
fi

echo ""
echo "All requested tests completed."