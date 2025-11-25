#!/bin/bash

# Test Runner Script for Hackathon AI Agent System
# This script runs all tests and provides clear feedback

echo "╔═══════════════════════════════════════════════════════════╗"
echo "║     Hackathon AI Agent System - Test Runner              ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Track test results
TESTS_PASSED=0
TESTS_FAILED=0

# Function to run a test
run_test() {
    local test_name=$1
    local test_file=$2
    local required=$3
    
    echo ""
    echo "─────────────────────────────────────────────────────────"
    echo -e "${BLUE}Running: ${test_name}${NC}"
    echo "─────────────────────────────────────────────────────────"
    
    if [ ! -f "$test_file" ]; then
        echo -e "${YELLOW}⚠️  Test file not found: ${test_file}${NC}"
        if [ "$required" = "yes" ]; then
            TESTS_FAILED=$((TESTS_FAILED + 1))
        fi
        return 1
    fi
    
    python "$test_file"
    local exit_code=$?
    
    if [ $exit_code -eq 0 ]; then
        echo ""
        echo -e "${GREEN}✅ ${test_name} PASSED${NC}"
        TESTS_PASSED=$((TESTS_PASSED + 1))
        return 0
    else
        echo ""
        echo -e "${RED}❌ ${test_name} FAILED${NC}"
        TESTS_FAILED=$((TESTS_FAILED + 1))
        return 1
    fi
}

# Change to Code directory
if [ -d "Code" ]; then
    cd Code
    echo "Changed to Code directory"
elif [ -f "src/llm/__init__.py" ]; then
    echo "Already in Code directory"
else
    echo -e "${RED}❌ Error: Cannot find Code directory${NC}"
    exit 1
fi

echo ""
echo "Current directory: $(pwd)"
echo ""

# Check Python
echo "Checking Python installation..."
if command -v python &> /dev/null; then
    PYTHON_VERSION=$(python --version)
    echo -e "${GREEN}✅ Python found: ${PYTHON_VERSION}${NC}"
else
    echo -e "${RED}❌ Python not found. Please install Python 3.8+${NC}"
    exit 1
fi

# Check dependencies
echo ""
echo "Checking dependencies..."
python -c "import langchain" 2>/dev/null
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ langchain installed${NC}"
else
    echo -e "${YELLOW}⚠️  langchain not installed. Run: pip install -r requirements.txt${NC}"
fi

# Check for .env file
echo ""
echo "Checking configuration..."
if [ -f ".env" ]; then
    echo -e "${GREEN}✅ .env file found${NC}"
    
    # Check for API keys
    if grep -q "OPENAI_API_KEY=sk-" .env 2>/dev/null; then
        echo -e "${GREEN}✅ OpenAI API key configured${NC}"
    else
        echo -e "${YELLOW}⚠️  OpenAI API key not configured (optional for Ollama tests)${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  .env file not found. Some tests may skip.${NC}"
    echo "   Create .env from .env.example if needed"
fi

# Check Ollama
echo ""
echo "Checking Ollama..."
if command -v ollama &> /dev/null; then
    echo -e "${GREEN}✅ Ollama installed${NC}"
    
    # Check if Ollama is running
    curl -s http://localhost:11434/api/tags > /dev/null 2>&1
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Ollama service running${NC}"
        
        # Check for models
        MODELS=$(ollama list 2>/dev/null | grep -v "NAME" | wc -l)
        if [ $MODELS -gt 0 ]; then
            echo -e "${GREEN}✅ Ollama models found (${MODELS} models)${NC}"
        else
            echo -e "${YELLOW}⚠️  No Ollama models found. Run: ollama pull llama2${NC}"
        fi
    else
        echo -e "${YELLOW}⚠️  Ollama not running. Start with: ollama serve${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  Ollama not installed (optional)${NC}"
    echo "   Install from: https://ollama.ai"
fi

echo ""
echo "═══════════════════════════════════════════════════════════"
echo "                    RUNNING TESTS                          "
echo "═══════════════════════════════════════════════════════════"

# Test 1: Config Loader (if exists)
if [ -f "tests/test_config_loader.py" ]; then
    run_test "Config Loader Tests" "tests/test_config_loader.py" "yes"
fi

# Test 2: Ollama Provider
if [ -f "tests/test_ollama_provider.py" ]; then
    run_test "Ollama Provider Tests" "tests/test_ollama_provider.py" "no"
fi

# Test 3: OpenAI Provider (requires API key)
if [ -f "tests/test_openai_provider.py" ]; then
    if grep -q "OPENAI_API_KEY=sk-" .env 2>/dev/null; then
        run_test "OpenAI Provider Tests" "tests/test_openai_provider.py" "no"
    else
        echo ""
        echo "─────────────────────────────────────────────────────────"
        echo -e "${YELLOW}⚠️  Skipping OpenAI tests (no API key configured)${NC}"
        echo "─────────────────────────────────────────────────────────"
    fi
fi

# Test 4: CSV Tools (when implemented)
if [ -f "tests/test_csv_tools.py" ]; then
    run_test "CSV Tools Tests" "tests/test_csv_tools.py" "yes"
fi

# Summary
echo ""
echo "═══════════════════════════════════════════════════════════"
echo "                    TEST SUMMARY                           "
echo "═══════════════════════════════════════════════════════════"
echo ""

TOTAL_TESTS=$((TESTS_PASSED + TESTS_FAILED))

echo -e "${GREEN}Passed: ${TESTS_PASSED}${NC}"
echo -e "${RED}Failed: ${TESTS_FAILED}${NC}"
echo "Total:  ${TOTAL_TESTS}"
echo ""

if [ $TESTS_FAILED -eq 0 ] && [ $TESTS_PASSED -gt 0 ]; then
    echo -e "${GREEN}╔═══════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║                  🎉 ALL TESTS PASSED! 🎉                  ║${NC}"
    echo -e "${GREEN}╚═══════════════════════════════════════════════════════════╝${NC}"
    exit 0
elif [ $TESTS_PASSED -eq 0 ] && [ $TESTS_FAILED -eq 0 ]; then
    echo -e "${YELLOW}╔═══════════════════════════════════════════════════════════╗${NC}"
    echo -e "${YELLOW}║              ⚠️  NO TESTS WERE RUN ⚠️                      ║${NC}"
    echo -e "${YELLOW}╚═══════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo "Possible reasons:"
    echo "  • Test files not found"
    echo "  • Dependencies not installed"
    echo "  • Configuration incomplete"
    exit 1
else
    echo -e "${RED}╔═══════════════════════════════════════════════════════════╗${NC}"
    echo -e "${RED}║                  ❌ SOME TESTS FAILED ❌                   ║${NC}"
    echo -e "${RED}╚═══════════════════════════════════════════════════════════╝${NC}"
    exit 1
fi
