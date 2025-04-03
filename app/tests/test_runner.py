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
from app.tests.test_matrix import get_test_matrix, get_filtered_test_cases, get_sample_test_cases
from app.tests.validators import validate_script
from app.tests.filter_presets import (
    APPROACHES, get_approach_description, apply_approach_filters, 
    filter_test_cases_by_approach, get_interactive_filters,
    estimate_test_count, estimate_time_and_tokens
)
from app.utils.llm_clients import generate_script, edit_script_with_claude as edit_script
from app.utils.test_logging import setup_test_logger, log_test_result, log_test_summary
from app.utils.token_counter import token_tracker

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
            'warnings': [],
            'token_usage': {},
            'timing': {}
        }
        
        try:
            # Generate the script
            generation_start = time.time()
            script_result = generate_script(
                prompt=test_case['subject'], 
                template=test_case['template'],
                subject=test_case['subject'],
                length=test_case['length'],
                audience=test_case['audience'],
                tone=test_case['tone'],
                force_fallback=self.force_fallback,
                is_test=True
            )
            
            # Handle the new return format (dict with content and metrics)
            if isinstance(script_result, dict) and "content" in script_result:
                script = script_result["content"]
                result['token_usage'] = script_result.get("token_metrics", {})
                result['model_used'] = script_result.get("model_used", "unknown")
                result['is_fallback'] = script_result.get("is_fallback", False)
            else:
                # Fallback for backward compatibility
                script = script_result
            
            generation_time = time.time() - generation_start
            result['timing']['generation'] = generation_time
            result['generated_script'] = script
            
            # Validate the script
            validation_start = time.time()
            validation_result = validate_script(script, test_case)
            validation_time = time.time() - validation_start
            result['timing']['validation'] = validation_time
            
            # Consider test as successful if we have a valid script (even with warnings)
            # Tests fail only if they have hard errors (typically only template markers)
            if validation_result['is_valid']:
                result['success'] = True
            else:
                result['success'] = False
                result['errors'].extend(validation_result['errors'])
            
            # Include warnings
            if validation_result.get('warnings', []):
                result['warnings'].extend(validation_result['warnings'])
                
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
    
    def run_tests(self, test_cases=None, filters=None, approach=None, **kwargs):
        """Run tests based on provided test cases, filters, or approach.
        
        Args:
            test_cases: List of test cases to run (highest priority)
            filters: Dictionary of filters to apply to test cases (medium priority)
            approach: Testing approach to use (lowest priority)
            **kwargs: Additional parameters for the approach
            
        Returns:
            Dictionary with summary of test results
        """
        # Determine which test cases to run
        if test_cases is not None:
            # Use explicitly provided test cases
            cases_to_run = test_cases
            source = "explicitly provided test cases"
        elif filters is not None:
            # Apply filters to get test cases
            cases_to_run = get_filtered_test_cases(filters)
            source = "filtered test cases"
        elif approach is not None:
            # Use a predefined testing approach
            cases_to_run = filter_test_cases_by_approach(approach, **kwargs)
            source = f"'{approach}' approach"
        else:
            # Default to sample test cases for safety
            cases_to_run = get_sample_test_cases(5)
            source = "default sample test cases"
            
        logger.info(f"Running {len(cases_to_run)} test cases from {source}")
        
        # Estimate time and token usage
        estimates = estimate_time_and_tokens(len(cases_to_run))
        logger.info(f"Estimated execution time: {estimates['time']['formatted']}")
        logger.info(f"Estimated token usage: {estimates['tokens']['total']:,} tokens")
        
        # Run tests in parallel
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_test = {executor.submit(self.run_single_test, test_case): test_case for test_case in cases_to_run}
            for future in as_completed(future_to_test):
                test_case = future_to_test[future]
                try:
                    result = future.result()
                    self.results.append(result)
                except Exception as e:
                    logger.error(f"Test execution failed: {str(e)}")
        
        # Generate summary
        summary = self._generate_summary()
        summary['source'] = source
        summary['output_dir'] = self.output_dir
        
        # Save summary
        self._save_summary(summary)
        
        # Log summary
        log_test_summary(summary)
        
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
                    'warnings': 0,
                    'avg_generation_time': 0,
                    'token_usage': {}
                }
            
            template_stats[template]['total'] += 1
            if result['success']:
                template_stats[template]['success'] += 1
            else:
                template_stats[template]['failure'] += 1
                
            if result.get('warnings', []):
                template_stats[template]['warnings'] += 1
                
            # Accumulate timing data for averaging later
            if 'timing' in result and 'generation' in result['timing']:
                template_stats[template]['avg_generation_time'] += result['timing']['generation']
        
        # Calculate averages
        for template, stats in template_stats.items():
            if stats['total'] > 0:
                stats['avg_generation_time'] /= stats['total']
                stats['success_rate'] = stats['success'] / stats['total']
        
        return {
            'timestamp': datetime.now().isoformat(),
            'total_tests': total_tests,
            'successful_tests': successful_tests,
            'success_rate': successful_tests / total_tests if total_tests > 0 else 0,
            'template_stats': template_stats,
            'warnings_count': sum(1 for r in self.results if r.get('warnings', []))
        }


def main():
    """Main entry point for running the test suite from the command line."""
    parser = argparse.ArgumentParser(description='Cross-Template Testing Suite')
    
    # Basic filtering options
    filter_group = parser.add_argument_group('Basic Filtering Options')
    filter_group.add_argument('--templates', help='Comma-separated list of templates to test')
    filter_group.add_argument('--audience', help='Filter by audience level')
    filter_group.add_argument('--length', help='Filter by script length')
    filter_group.add_argument('--tone', help='Filter by tone')
    
    # Advanced options
    advanced_group = parser.add_argument_group('Advanced Options')
    advanced_group.add_argument('--force-fallback', action='store_true', help='Force fallback to Claude model')
    advanced_group.add_argument('--max-workers', type=int, default=4, help='Maximum number of parallel test executions')
    advanced_group.add_argument('--output-dir', help='Directory to store test results')
    advanced_group.add_argument('--estimate-only', action='store_true', help='Only estimate test count and resources, no execution')
    
    # Testing approach options
    approach_group = parser.add_argument_group('Testing Approach Options')
    approach_group.add_argument('--approach', choices=APPROACHES.keys(), help='Testing approach to use')
    approach_group.add_argument('--approach-param', action='append', nargs=2, metavar=('KEY', 'VALUE'), 
                             help='Parameters for the testing approach (can be specified multiple times)')
    approach_group.add_argument('--interactive', action='store_true', help='Use interactive mode for selecting filters')
    approach_group.add_argument('--sample-size', type=int, help='Number of test cases to sample (for sample-based approach)')
    approach_group.add_argument('--sample-strategy', choices=['balanced', 'random'], default='balanced', 
                             help='Sampling strategy (for sample-based approach)')
    
    args = parser.parse_args()
    
    # Handle interactive mode
    if args.interactive:
        filter_selection = get_interactive_filters()
        if not filter_selection:
            return 1
        
        approach = filter_selection['approach']
        kwargs = filter_selection['kwargs']
    else:
        # Prepare filters based on command line arguments
        filters = {}
        if args.templates:
            filters['templates'] = args.templates.split(',')
        if args.audience:
            filters['audience'] = args.audience
        if args.length:
            filters['length'] = args.length
        if args.tone:
            filters['tone'] = args.tone
        
        # Prepare approach parameters
        approach = args.approach
        kwargs = {}
        
        if args.approach_param:
            for key, value in args.approach_param:
                # Try to convert numeric values
                try:
                    if '.' in value:
                        kwargs[key] = float(value)
                    else:
                        kwargs[key] = int(value)
                except ValueError:
                    kwargs[key] = value
        
        # Special handling for sample-based approach
        if approach == 'sample-based' or (not approach and args.sample_size):
            approach = 'sample-based'
            kwargs['sample_size'] = args.sample_size or 5
            kwargs['strategy'] = args.sample_strategy
    
    # Determine what test cases to run
    if approach:
        test_filters = apply_approach_filters(approach, **kwargs)
        test_source = f"'{approach}' approach"
    else:
        test_filters = filters
        test_source = "command-line filters"
    
    # Estimate test count and resources
    test_count = estimate_test_count(test_filters)
    estimates = estimate_time_and_tokens(test_count)
    
    print("\n=== Test Execution Estimates ===")
    print(f"Source: {test_source}")
    print(f"Number of test cases: {test_count}")
    print(f"Estimated time: {estimates['time']['formatted']}")
    print(f"Estimated token usage: {estimates['tokens']['total']:,}")
    print(f"Estimated cost (DeepSeek): ${estimates['tokens']['estimated_cost_deepseek']:.2f}")
    print(f"Estimated cost (Claude): ${estimates['tokens']['estimated_cost_claude']:.2f}")
    
    # If only estimating, exit here
    if args.estimate_only:
        print("\nEstimate-only mode. Exiting without running tests.")
        return 0
    
    if test_count > 100:
        proceed = input(f"\nWarning: You are about to run {test_count} tests, which may take a long time and consume significant resources. Proceed? (y/n): ").lower()
        if proceed != 'y':
            print("Test execution cancelled.")
            return 1
    
    # Create and run test runner
    runner = TestRunner(
        output_dir=args.output_dir,
        max_workers=args.max_workers,
        force_fallback=args.force_fallback
    )
    
    if approach:
        summary = runner.run_tests(approach=approach, **kwargs)
    else:
        summary = runner.run_tests(filters=filters)
    
    # Print summary to console
    print("\n=== Test Summary ===")
    print(f"Total Tests: {summary['total_tests']}")
    print(f"Successful Tests: {summary['successful_tests']}")
    print(f"Success Rate: {summary['success_rate'] * 100:.2f}%")
    
    print("\nTemplate Performance:")
    for template, stats in summary['template_stats'].items():
        print(f"  {template}:")
        print(f"    Success Rate: {stats['success_rate'] * 100:.2f}% ({stats['success']}/{stats['total']})")
        print(f"    Avg Generation Time: {stats['avg_generation_time']:.2f}s")
    
    print(f"\nFull results saved to: {runner.output_dir}")
    
    # Return success if all tests passed
    return 0 if summary['success_rate'] == 1.0 else 1


if __name__ == "__main__":
    main() 