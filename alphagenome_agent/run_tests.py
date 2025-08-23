#!/usr/bin/env python3
"""Test runner for AlphaGenome Agent.

This script sets up the proper Python path and runs tests from the correct directory.
Usage:
    python run_tests.py                    # Run all tests
    python run_tests.py alphagenome        # Run AlphaGenome client tests only
    python run_tests.py cbioportal         # Run CBioPortal client tests only
"""

import sys
import os
from pathlib import Path

# Add src directory to Python path
src_dir = Path(__file__).parent / "src"
sys.path.insert(0, str(src_dir))

def run_alphagenome_tests():
    """Run AlphaGenome client tests."""
    from src.clients.tests.test_alphagenome_client import (
        test_alphagenome_client,
        test_alphagenome_client_error_handling
    )
    
    print("🔬 Running AlphaGenome Client Tests")
    print("=" * 50)
    
    # Test 1: Basic functionality
    success1 = test_alphagenome_client()
    
    # Test 2: Error handling  
    success2 = test_alphagenome_client_error_handling()
    
    # Summary
    print(f"\n🎯 AlphaGenome Test Results:")
    print(f"   Basic functionality: {'✅ PASS' if success1 else '❌ FAIL'}")
    print(f"   Error handling: {'✅ PASS' if success2 else '❌ FAIL'}")
    
    return success1 and success2

def run_cbioportal_tests():
    """Run CBioPortal client tests."""
    # Import the test module
    from src.clients.tests import test_cbioportal_client
    
    print("🔬 Running CBioPortal Client Tests")
    print("=" * 50)
    
    # Run the main function if it exists
    if hasattr(test_cbioportal_client, 'main'):
        return test_cbioportal_client.main()
    else:
        # Run individual test functions
        success = True
        for name in dir(test_cbioportal_client):
            if name.startswith('test_'):
                test_func = getattr(test_cbioportal_client, name)
                if callable(test_func):
                    try:
                        result = test_func()
                        if result is False:
                            success = False
                    except Exception as e:
                        print(f"❌ Test {name} failed: {e}")
                        success = False
        return success

def main():
    """Main test runner."""
    if len(sys.argv) > 1:
        test_target = sys.argv[1].lower()
        
        if test_target in ['alphagenome', 'ag']:
            success = run_alphagenome_tests()
        elif test_target in ['cbioportal', 'cbio']:
            success = run_cbioportal_tests()
        else:
            print(f"Unknown test target: {test_target}")
            print("Valid targets: alphagenome, cbioportal")
            sys.exit(1)
    else:
        # Run all tests
        print("🧪 Running All Tests")
        print("=" * 70)
        
        ag_success = run_alphagenome_tests()
        print("\n" + "=" * 70 + "\n")
        cbio_success = run_cbioportal_tests()
        
        success = ag_success and cbio_success
        
        print("\n" + "=" * 70)
        print("📊 Overall Test Summary:")
        print(f"   AlphaGenome tests: {'✅ PASS' if ag_success else '❌ FAIL'}")
        print(f"   CBioPortal tests: {'✅ PASS' if cbio_success else '❌ FAIL'}")
    
    if success:
        print("\n🎉 All tests passed!")
        sys.exit(0)
    else:
        print("\n💥 Some tests failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()