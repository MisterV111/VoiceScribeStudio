"""
Cross-Template Testing Suite - Test Logging

This module provides logging functions for the testing suite.
"""

import os
import json
import logging
from datetime import datetime

def setup_test_logger(output_dir):
    """Set up a logger for the testing suite.
    
    Args:
        output_dir: Directory to store log files
    
    Returns:
        Configured logger
    """
    logger = logging.getLogger("cross_template_testing")
    logger.setLevel(logging.INFO)
    
    # Clear existing handlers
    if logger.handlers:
        logger.handlers.clear()
    
    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # Create file handler
    log_file = os.path.join(output_dir, "test_run.log")
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.DEBUG)
    
    # Create formatters
    console_format = logging.Formatter('%(levelname)s - %(message)s')
    file_format = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    
    # Add formatters to handlers
    console_handler.setFormatter(console_format)
    file_handler.setFormatter(file_format)
    
    # Add handlers to logger
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    
    logger.info(f"Test logging initialized. Log file: {log_file}")
    return logger

def log_test_result(result):
    """Log a test result with appropriate level.
    
    Args:
        result: Dictionary with test result
    """
    logger = logging.getLogger("cross_template_testing")
    
    # Create a simplified version of the result for logging
    log_data = {
        'test_id': result['test_id'],
        'success': result['success'],
        'errors': result['errors'],
        'warnings': result.get('warnings', []),
    }
    
    # Add timing information if available
    if 'timing' in result:
        log_data['generation_time'] = result['timing'].get('generation', 0)
        log_data['total_time'] = result['timing'].get('total', 0)
    
    # Add validation metrics if available
    if 'validation' in result and 'metrics' in result['validation']:
        log_data['metrics'] = result['validation']['metrics']
    
    # Log with appropriate level
    if result['success']:
        logger.info(f"✅ PASS: {result['test_id']}")
        logger.debug(f"Details: {json.dumps(log_data)}")
    elif result.get('warnings', []):
        logger.warning(f"⚠️ WARN: {result['test_id']} - {', '.join(result['warnings'])}")
        logger.debug(f"Details: {json.dumps(log_data)}")
    else:
        logger.error(f"❌ FAIL: {result['test_id']} - {', '.join(result['errors'])}")
        logger.debug(f"Details: {json.dumps(log_data)}")

def log_test_summary(summary):
    """Log a summary of test results.
    
    Args:
        summary: Dictionary with test summary
    """
    logger = logging.getLogger("cross_template_testing")
    
    logger.info(f"Test run completed at {datetime.now().isoformat()}")
    logger.info(f"Total tests: {summary['total_tests']}")
    logger.info(f"Successful tests: {summary['successful_tests']}")
    logger.info(f"Success rate: {summary['success_rate'] * 100:.2f}%")
    
    # Log template-specific stats
    for template, stats in summary['template_stats'].items():
        success_rate = stats['success'] / stats['total'] * 100 if stats['total'] > 0 else 0
        logger.info(f"Template '{template}': {success_rate:.2f}% success rate ({stats['success']}/{stats['total']})")
    
    # Log details about failures if any
    if summary['total_tests'] > summary['successful_tests']:
        logger.warning(f"Failed tests: {summary['total_tests'] - summary['successful_tests']}")
        
    logger.info(f"Detailed results saved to {summary.get('output_dir', 'test_results')}")

def log_error(message, exception=None):
    """Log an error.
    
    Args:
        message: Error message
        exception: Optional exception object
    """
    logger = logging.getLogger("cross_template_testing")
    
    if exception:
        logger.error(f"{message}: {str(exception)}")
    else:
        logger.error(message) 