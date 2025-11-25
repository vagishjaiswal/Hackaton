#!/usr/bin/env python
"""
Test Runner for Hackathon AI Agent System
Cross-platform test execution with colored output and detailed reporting.

Usage:
    python run_tests.py              # Run all tests
    python run_tests.py --ollama     # Run only Ollama tests
    python run_tests.py --openai     # Run only OpenAI tests
    python run_tests.py --verbose    # Verbose output
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path
from typing import List, Tuple


# ANSI color codes (works on most terminals)
class Colors:
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    BOLD = '\033[1m'
    NC = '\033[0m'  # No Color


def print_header(title: str):
    """Print a formatted header."""
    print()
    print("═" * 60)
    print(f"  {title}")
    print("═" * 60)
    print()


def print_section(title: str):
    """Print a section divider."""
    print()
    print("─" * 60)
    print(f"{Colors.BLUE}{title}{Colors.NC}")
    print("─" * 60)


def print_success(message: str):
    """Print success message."""
    print(f"{Colors.GREEN}✅ {message}{Colors.NC}")


def print_error(message: str):
    """Print error message."""
    print(f"{Colors.RED}❌ {message}{Colors.NC}")


def print_warning(message: str):
    """Print warning message."""
    print(f"{Colors.YELLOW}⚠️  {message}{Colors.NC}")


def check_python():
    """Check Python installation."""
    print("Checking Python installation...")
    version = sys.version.split()[0]
    print_success(f"Python found: {version}")
    
    # Check version
    major, minor = sys.version_info[:2]
    if major < 3 or (major == 3 and minor < 8):
        print_error("Python 3.8+ required")
        return False
    return True


def check_dependencies():
    """Check if required dependencies are installed."""
    print()
    print("Checking dependencies...")
    
    required = [
        ('langchain', 'langchain'),
        ('langchain_openai', 'langchain-openai'),
        ('langchain_community', 'langchain-community'),
        ('tenacity', 'tenacity'),
        ('pydantic', 'pydantic'),
    ]
    
    all_installed = True
    for module, package in required:
        try:
            __import__(module)
            print_success(f"{package} installed")
        except ImportError:
            print_warning(f"{package} not installed")
            all_installed = False
    
    if not all_installed:
        print()
        print_warning("Some dependencies missing. Run: pip install -r requirements.txt")
    
    return all_installed


def check_env_file():
    """Check for .env file and API keys."""
    print()
    print("Checking configuration...")
    
    env_file = Path('.env')
    if not env_file.exists():
        print_warning(".env file not found (optional)")
        return False
    
    print_success(".env file found")
    
    # Check for API keys
    with open(env_file) as f:
        content = f.read()
    
    has_openai = 'OPENAI_API_KEY=sk-' in content
    if has_openai:
        print_success("OpenAI API key configured")
    else:
        print_warning("OpenAI API key not configured (optional for Ollama)")
    
    return True


def check_ollama():
    """Check if Ollama is installed and running."""
    print()
    print("Checking Ollama...")
    
    # Check if ollama command exists
    try:
        result = subprocess.run(
            ['ollama', 'list'],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0:
            print_success("Ollama installed and running")
            
            # Count models
            models = [line for line in result.stdout.split('\n') 
                     if line and 'NAME' not in line]
            if models:
                print_success(f"Found {len(models)} Ollama model(s)")
                return True
            else:
                print_warning("No Ollama models found. Run: ollama pull llama2")
                return False
        else:
            print_warning("Ollama not running. Start with: ollama serve")
            return False
            
    except FileNotFoundError:
        print_warning("Ollama not installed (optional)")
        print("        Install from: https://ollama.ai")
        return False
    except subprocess.TimeoutExpired:
        print_warning("Ollama command timed out")
        return False


def run_test(test_name: str, test_file: Path, verbose: bool = False) -> Tuple[bool, str]:
    """
    Run a single test file.
    
    Returns:
        Tuple of (success, output)
    """
    print_section(f"Running: {test_name}")
    
    if not test_file.exists():
        print_warning(f"Test file not found: {test_file}")
        return False, "File not found"
    
    try:
        result = subprocess.run(
            [sys.executable, str(test_file)],
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )
        
        if verbose or result.returncode != 0:
            print(result.stdout)
            if result.stderr:
                print(result.stderr)
        
        if result.returncode == 0:
            print()
            print_success(f"{test_name} PASSED")
            return True, result.stdout
        else:
            print()
            print_error(f"{test_name} FAILED")
            return False, result.stdout + result.stderr
            
    except subprocess.TimeoutExpired:
        print_error(f"{test_name} TIMED OUT")
        return False, "Test timed out after 5 minutes"
    except Exception as e:
        print_error(f"{test_name} ERROR: {e}")
        return False, str(e)


def main():
    """Main test runner."""
    parser = argparse.ArgumentParser(
        description='Run tests for Hackathon AI Agent System'
    )
    parser.add_argument(
        '--ollama', 
        action='store_true',
        help='Run only Ollama tests'
    )
    parser.add_argument(
        '--openai',
        action='store_true',
        help='Run only OpenAI tests'
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Verbose output'
    )
    
    args = parser.parse_args()
    
    # Print header
    print_header("Hackathon AI Agent System - Test Runner")
    
    # Change to Code directory if needed
    if Path('Code').exists():
        os.chdir('Code')
        print("Changed to Code directory")
    elif Path('src/llm/__init__.py').exists():
        print("Already in Code directory")
    else:
        print_error("Cannot find Code directory")
        return 1
    
    print(f"Current directory: {os.getcwd()}")
    
    # Run checks
    if not check_python():
        return 1
    
    deps_ok = check_dependencies()
    env_ok = check_env_file()
    ollama_ok = check_ollama()
    
    # Determine which tests to run
    tests_dir = Path('tests')
    all_tests = []
    
    if args.ollama or (not args.openai and not args.ollama):
        if ollama_ok:
            ollama_test = tests_dir / 'test_ollama_provider.py'
            if ollama_test.exists():
                all_tests.append(('Ollama Provider Tests', ollama_test))
        else:
            print_warning("Skipping Ollama tests (Ollama not available)")
    
    if args.openai or (not args.openai and not args.ollama):
        if env_ok:
            openai_test = tests_dir / 'test_openai_provider.py'
            if openai_test.exists():
                all_tests.append(('OpenAI Provider Tests', openai_test))
        else:
            print_warning("Skipping OpenAI tests (no API key)")
    
    # Add other tests
    if not args.openai and not args.ollama:
        csv_test = tests_dir / 'test_csv_tools.py'
        if csv_test.exists():
            all_tests.append(('CSV Tools Tests', csv_test))
    
    if not all_tests:
        print()
        print_error("No tests to run!")
        print()
        print("Possible reasons:")
        print("  • Test files not found")
        print("  • Dependencies not installed")
        print("  • Ollama not running (for Ollama tests)")
        print("  • No API key configured (for OpenAI tests)")
        return 1
    
    # Run tests
    print_header("RUNNING TESTS")
    
    results = []
    for test_name, test_file in all_tests:
        success, output = run_test(test_name, test_file, args.verbose)
        results.append((test_name, success))
    
    # Print summary
    print_header("TEST SUMMARY")
    
    passed = sum(1 for _, success in results if success)
    failed = len(results) - passed
    
    print(f"{Colors.GREEN}Passed: {passed}{Colors.NC}")
    print(f"{Colors.RED}Failed: {failed}{Colors.NC}")
    print(f"Total:  {len(results)}")
    print()
    
    # Print detailed results
    if results:
        print("Test Results:")
        for test_name, success in results:
            status = f"{Colors.GREEN}✅ PASSED{Colors.NC}" if success else f"{Colors.RED}❌ FAILED{Colors.NC}"
            print(f"  {test_name}: {status}")
        print()
    
    # Final verdict
    if failed == 0 and passed > 0:
        print(f"{Colors.GREEN}{'═' * 60}{Colors.NC}")
        print(f"{Colors.GREEN}  🎉 ALL TESTS PASSED! 🎉{Colors.NC}")
        print(f"{Colors.GREEN}{'═' * 60}{Colors.NC}")
        return 0
    elif passed == 0 and failed == 0:
        print(f"{Colors.YELLOW}{'═' * 60}{Colors.NC}")
        print(f"{Colors.YELLOW}  ⚠️  NO TESTS WERE RUN ⚠️{Colors.NC}")
        print(f"{Colors.YELLOW}{'═' * 60}{Colors.NC}")
        return 1
    else:
        print(f"{Colors.RED}{'═' * 60}{Colors.NC}")
        print(f"{Colors.RED}  ❌ SOME TESTS FAILED ❌{Colors.NC}")
        print(f"{Colors.RED}{'═' * 60}{Colors.NC}")
        return 1


if __name__ == '__main__':
    sys.exit(main())
