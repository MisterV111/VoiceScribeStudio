#!/usr/bin/env python
"""
Cross-Template Testing Suite - Entry Point

This script is the main entry point for running the cross-template testing suite.
It can be run directly from the command line.
"""

import sys
import argparse
from app.tests.test_runner import TestRunner, main as test_main

if __name__ == "__main__":
    # If run directly, pass control to the main function in test_runner
    sys.exit(test_main()) 