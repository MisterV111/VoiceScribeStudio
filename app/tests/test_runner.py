"""
Cross-Template Testing Suite - Test Runner

This module serves as the main orchestration component for running
automated tests across all script templates and parameter combinations.
"""

import os
import time
import json
import argparse
import logging
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

# Local imports
from app.tests.test_matrix import get_test_matrix, get_filtered_test_cases
from app.tests.validators import validate_script
from app.utils.llm_clients import generate_script, edit_script
from app.utils.test_logging import setup_test_logger, log_test_result

# Configure logging
logger = logging.getLogger("cross_template_testing")

class TestRunner:
    """Main orchestrator for the cross-template testing suite."""
    
    def __init__(self, output_dir=None, max_workers=4, force_fallback=False):
        """Initialize the test runner.
        
        Args:
            output_dir: Directory to store test results
            max_workers: Maximum number of parallel test executions
            force_fallback: Force fallback to Claude for all test cases
        """
        self.output_dir = output_dir or os.path.join('app', 'test_results', datetime.now().strftime('%Y%m%d_%H%M%S'))
        self.max_workers = max_workers
        self.force_fallback = force_fallback
        self.results = []
        
        # Ensure output directory exists
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Set up logging
        setup_test_logger(self.output_dir)
        
    def run_single_test(self, test_case):
        """Run a single test case.
        
        Args:
            test_case: Dictionary containing test parameters
            
        Returns:
            Dictionary with test results
        """
        test_id = f"{test_case['template']}_{test_case['subject']}_{test_case['length']}_{test_case['audience']}_{test_case['tone']}"
        logger.info(f"Starting test: {test_id}")
        
        start_time = time.time()
        result = {
            'test_id': test_id,
            'test_case': test_case,
            'timestamp': datetime.now().isoformat(),
            'success': False,
            'errors': [],
            'token_usage': {},
            'timing': {}
        }
        
        try:
            # Generate the script
            generation_start = time.time()
            script = generate_script(
                template=test_case['template'],
                subject=test_case['subject'],
                length=test_case['length'],
                audience=test_case['audience'],
                tone=test_case['tone'],
                force_fallback=self.force_fallback
            )
            generation_time = time.time() - generation_start
            result['timing']['generation'] = generation_time
            result['generated_script'] = script
            
            # Validate the script
            validation_start = time.time()
            validation_result = validate_script(script, test_case)
            validation_time = time.time() - validation_start
            result['timing']['validation'] = validation_time
            
            if validation_result['is_valid']:
                result['success'] = True
            else:
                result['success'] = False
                result['errors'].extend(validation_result['errors'])
                
            # Include validation details
            result['validation'] = validation_result
            
        except Exception as e:
            logger.error(f"Error running test {test_id}: {str(e)}")
            result['success'] = False
            result['errors'].append(str(e))
        
        total_time = time.time() - start_time
        result['timing']['total'] = total_time
        
        # Save individual test result
        self._save_test_result(result)
        
        # Log result
        log_test_result(result)
        
        return result
    
    def run_tests(self, filters=None):
        """Run all test cases or a filtered subset.
        
        Args:
            filters: Dictionary of filters to apply to test cases
            
        Returns:
            Dictionary with summary of test results
        """
        # Get test cases based on filters
        if filters:
            test_cases = get_filtered_test_cases(filters)
        else:
            test_cases = get_test_matrix()
            
        logger.info(f"Running {len(test_cases)} test cases")
        
        # Run tests in parallel
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_test = {executor.submit(self.run_single_test, test_case): test_case for test_case in test_cases}
            for future in as_completed(future_to_test):
                test_case = future_to_test[future]
                try:
                    result = future.result()
                    self.results.append(result)
                except Exception as e:
                    logger.error(f"Test execution failed: {str(e)}")
        
        # Generate summary
        summary = self._generate_summary()
        
        # Save summary
        self._save_summary(summary)
        
        return summary
    
    def _save_test_result(self, result):
        """Save an individual test result to a JSON file."""
        result_file = os.path.join(self.output_dir, f"{result['test_id']}.json")
        with open(result_file, 'w') as f:
            json.dump(result, f, indent=2)
    
    def _save_summary(self, summary):
        """Save the test summary to a JSON file."""
        summary_file = os.path.join(self.output_dir, "summary.json")
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
    
    def _generate_summary(self):
        """Generate a summary of test results."""
        total_tests = len(self.results)
        successful_tests = sum(1 for r in self.results if r['success'])
        
        template_stats = {}
        for result in self.results:
            template = result['test_case']['template']
            if template not in template_stats:
                template_stats[template] = {
                    'total': 0,
                    'success': 0,
                    'failure': 0,
                    'avg_generation_time': 0,
                    'token_usage': {}
                }
            
            template_stats[template]['total'] += 1
            if result['success']:
                template_stats[template]['success'] += 1
            else:
                template_stats[template]['failure'] += 1
                
            # Accumulate timing data for averaging later
            if 'timing' in result and 'generation' in result['timing']:
                template_stats[template]['avg_generation_time'] += result['timing']['generation']
        
        # Calculate averages
        for template, stats in template_stats.items():
            if stats['total'] > 0:
                stats['avg_generation_time'] /= stats['total']
        
        return {
            'timestamp': datetime.now().isoformat(),
            'total_tests': total_tests,
            'successful_tests': successful_tests,
            'success_rate': successful_tests / total_tests if total_tests > 0 else 0,
            'template_stats': template_stats
        }


def main():
    """Main entry point for running the test suite from the command line."""
    parser = argparse.ArgumentParser(description='Cross-Template Testing Suite')
    parser.add_argument('--templates', help='Comma-separated list of templates to test')
    parser.add_argument('--audience', help='Filter by audience level')
    parser.add_argument('--length', help='Filter by script length')
    parser.add_argument('--tone', help='Filter by tone')
    parser.add_argument('--force-fallback', action='store_true', help='Force fallback to secondary model')
    parser.add_argument('--max-workers', type=int, default=4, help='Maximum number of parallel test executions')
    parser.add_argument('--output-dir', help='Directory to store test results')
    
    args = parser.parse_args()
    
    # Prepare filters from command line arguments
    filters = {}
    if args.templates:
        filters['templates'] = args.templates.split(',')
    if args.audience:
        filters['audience'] = args.audience
    if args.length:
        filters['length'] = args.length
    if args.tone:
        filters['tone'] = args.tone
    
    # Create and run test runner
    runner = TestRunner(
        output_dir=args.output_dir,
        max_workers=args.max_workers,
        force_fallback=args.force_fallback
    )
    
    summary = runner.run_tests(filters if filters else None)
    
    # Print summary to console
    print("\n=== Test Summary ===")
    print(f"Total Tests: {summary['total_tests']}")
    print(f"Successful Tests: {summary['successful_tests']}")
    print(f"Success Rate: {summary['success_rate'] * 100:.2f}%")
    
    print("\nTemplate Performance:")
    for template, stats in summary['template_stats'].items():
        print(f"  {template}:")
        print(f"    Success Rate: {stats['success'] / stats['total'] * 100:.2f}% ({stats['success']}/{stats['total']})")
        print(f"    Avg Generation Time: {stats['avg_generation_time']:.2f}s")
    
    print(f"\nFull results saved to: {runner.output_dir}")


if __name__ == "__main__":
    main() 