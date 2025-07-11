#!/bin/bash
# Automated test runner for RumiAI v2
# NO HUMAN INTERVENTION REQUIRED

echo "🚀 Running RumiAI v2 Automated Tests"
echo "===================================="

# Set Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Run all tests
python3 tests/run_tests.py

# Exit with test status
exit $?