#!/usr/bin/env python
"""
Cross-Template Testing Suite - Entry Point

This script is the main entry point for running the cross-template testing suite.
It can be run directly from the command line.
"""

import sys
import os
import argparse
from app.tests.test_runner import TestRunner, main as test_main
from app.tests.filter_presets import APPROACHES, get_interactive_filters

def print_available_approaches():
    """Print information about available testing approaches."""
    print("\n=== Available Testing Approaches ===")
    for approach, description in APPROACHES.items():
        print(f"  {approach}: {description}")
    print("\nFor more information, run: python -m app.tests.run_tests --help")

if __name__ == "__main__":
    # Check for special commands
    if len(sys.argv) > 1:
        if sys.argv[1] == "--show-approaches":
            print_available_approaches()
            sys.exit(0)
        elif sys.argv[1] == "--interactive" and len(sys.argv) == 2:
            # Start in interactive mode
            filters = get_interactive_filters()
            if filters:
                runner = TestRunner()
                runner.run_tests(approach=filters['approach'], **filters['kwargs'])
            sys.exit(0)
    
    # If run directly, pass control to the main function in test_runner
    sys.exit(test_main()) 