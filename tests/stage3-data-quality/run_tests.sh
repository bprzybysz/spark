#!/bin/bash

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
# Get the project root directory (two levels up from script)
PROJECT_ROOT="$( cd "$SCRIPT_DIR/../.." && pwd )"

# Change to project root
cd "$PROJECT_ROOT"

# Set up Python environment
export PYTHONPATH="$PYTHONPATH:$PROJECT_ROOT"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

# Function to run tests
run_test() {
    echo -e "${GREEN}Running $1...${NC}"
    python -m pytest "$1" -v --capture=tee-sys
    if [ $? -ne 0 ]; then
        echo -e "${RED}$1 failed${NC}"
        exit 1
    fi
    echo -e "${GREEN}$1 passed${NC}\n"
}

# Create test data directory if it doesn't exist
mkdir -p "$SCRIPT_DIR/test_data"

# Run tests in order
run_test tests/stage3-data-quality/test_stage3_utils.py
run_test tests/stage3-data-quality/test_stage3_data_quality.py

# Run all tests together for coverage report
echo -e "${GREEN}Running all tests with coverage...${NC}"
python -m pytest tests/stage3-data-quality/ -v --cov=src.stages.stage3_data_quality --cov-report=term-missing 