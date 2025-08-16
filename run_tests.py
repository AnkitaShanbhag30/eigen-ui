#!/usr/bin/env python3
"""
Test runner for eigen-ui
Runs different levels of tests based on scope:
- unit: Individual function/module tests (fast)
- integration: Module interaction tests (medium)
- comprehensive: End-to-end workflow tests (slow)
- all: All tests
"""

import sys
import os
import argparse
import subprocess
from pathlib import Path

def run_tests(test_type, verbose=False):
    """Run tests of the specified type"""
    
    # Add app directory to path
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))
    
    if test_type == "unit":
        print("🧪 Running Unit Tests (fast)...")
        test_path = "tests/unit"
        pytest_args = ["-v" if verbose else "-q", test_path]
        
    elif test_type == "integration":
        print("🔗 Running Integration Tests (medium)...")
        test_path = "tests/integration"
        pytest_args = ["-v" if verbose else "-q", test_path]
        
    elif test_type == "comprehensive":
        print("🚀 Running Comprehensive Tests (slow)...")
        test_path = "tests/comprehensive"
        pytest_args = ["-v" if verbose else "-q", test_path]
        
    elif test_type == "all":
        print("🎯 Running All Tests...")
        test_path = "tests"
        pytest_args = ["-v" if verbose else "-q", test_path]
        
    else:
        print(f"❌ Unknown test type: {test_type}")
        return False
    
    # Check if pytest is available
    try:
        import pytest
    except ImportError:
        print("❌ pytest not available. Installing...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pytest"])
        import pytest
    
    # Run the tests
    try:
        result = pytest.main(pytest_args)
        return result == 0
    except Exception as e:
        print(f"❌ Error running tests: {e}")
        return False

def run_specific_test(test_file):
    """Run a specific test file"""
    print(f"🎯 Running specific test: {test_file}")
    
    if not os.path.exists(test_file):
        print(f"❌ Test file not found: {test_file}")
        return False
    
    try:
        result = pytest.main(["-v", test_file])
        return result == 0
    except Exception as e:
        print(f"❌ Error running test: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Run eigen-ui tests")
    parser.add_argument(
        "type",
        choices=["unit", "integration", "comprehensive", "all"],
        help="Type of tests to run"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Verbose output"
    )
    parser.add_argument(
        "--file", "-f",
        help="Run a specific test file"
    )
    
    args = parser.parse_args()
    
    if args.file:
        success = run_specific_test(args.file)
    else:
        success = run_tests(args.type, args.verbose)
    
    if success:
        print("\n🎉 All tests passed!")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
