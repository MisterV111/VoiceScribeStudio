"""
Cross-Template Testing Suite - Filter Presets

This module provides predefined filter configurations for different testing approaches.
"""

import random
from itertools import product
from app.tests.test_matrix import (
    TEMPLATES, LENGTH_OPTIONS, AUDIENCE_LEVELS, TONE_VARIATIONS, 
    TEMPLATE_SUBJECTS, get_test_matrix, get_filtered_test_cases
)

# Dictionary of available testing approaches
APPROACHES = {
    "template-focused": "Comprehensive testing of one template with all parameters",
    "parameter-sensitivity": "Test how different parameters affect output quality",
    "sample-based": "Test representative samples across templates",
    "full-matrix": "Test all possible combinations (warning: resource intensive)"
}

def get_approach_description(approach):
    """Get the description for a testing approach.
    
    Args:
        approach: Name of the testing approach
        
    Returns:
        Description string or None if approach not found
    """
    return APPROACHES.get(approach)

def estimate_test_count(filters):
    """Estimate how many tests will be run with the provided filters.
    
    Args:
        filters: Dictionary of filters to apply
        
    Returns:
        Estimated number of test cases
    """
    # Get base counts
    template_count = len(filters.get('templates', TEMPLATES))
    
    # Subject count depends on templates
    if 'templates' in filters:
        subject_count = sum(len(TEMPLATE_SUBJECTS.get(t, [])) for t in filters['templates'])
    else:
        subject_count = sum(len(subjects) for subjects in TEMPLATE_SUBJECTS.values())
    
    # If subjects are explicitly specified, use that count
    if 'subjects' in filters:
        subject_count = len(filters['subjects'])
        
    # Parameter counts
    length_count = len(filters.get('lengths', [filters.get('length')] if filters.get('length') else LENGTH_OPTIONS))
    audience_count = len(filters.get('audiences', [filters.get('audience')] if filters.get('audience') else AUDIENCE_LEVELS))
    tone_count = len(filters.get('tones', [filters.get('tone')] if filters.get('tone') else TONE_VARIATIONS))
    
    # Handle sampling
    if 'sample_size' in filters and filters['sample_size'] > 0:
        # For sampling, estimate based on sample size
        return min(filters['sample_size'], template_count * subject_count * length_count * audience_count * tone_count)
    
    # For balanced sampling, each template gets equal representation
    if filters.get('balanced', False):
        if 'max_per_template' in filters:
            return template_count * min(filters['max_per_template'], subject_count * length_count * audience_count * tone_count)
    
    # Default full calculation
    return template_count * subject_count * length_count * audience_count * tone_count

def estimate_time_and_tokens(test_count, avg_time_per_test=10, avg_tokens_per_test=1000):
    """Estimate time and token usage for a given number of tests.
    
    Args:
        test_count: Number of tests to run
        avg_time_per_test: Average time per test in seconds
        avg_tokens_per_test: Average tokens per test
        
    Returns:
        Dictionary with time and token estimates
    """
    total_time_seconds = test_count * avg_time_per_test
    total_tokens = test_count * avg_tokens_per_test
    
    # Calculate time in hours, minutes, seconds
    hours = total_time_seconds // 3600
    minutes = (total_time_seconds % 3600) // 60
    seconds = total_time_seconds % 60
    
    # Calculate token cost (approximate)
    # Using $0.14 per 1M tokens for input (DeepSeek)
    # $3 per 1M tokens for input (Claude)
    deepseek_cost = (total_tokens / 1000000) * 0.14
    claude_cost = (total_tokens / 1000000) * 3.0
    
    return {
        'test_count': test_count,
        'time': {
            'total_seconds': total_time_seconds,
            'hours': hours,
            'minutes': minutes,
            'seconds': seconds,
            'formatted': f"{int(hours)}h {int(minutes)}m {int(seconds)}s"
        },
        'tokens': {
            'total': total_tokens,
            'estimated_cost_deepseek': deepseek_cost,
            'estimated_cost_claude': claude_cost
        }
    }

def get_template_focused_filters(template, max_tests=None):
    """Get filters for template-focused testing.
    
    Args:
        template: The template to focus on
        max_tests: Maximum number of tests to run (will sample if needed)
        
    Returns:
        Dictionary with filters
    """
    if template not in TEMPLATES:
        raise ValueError(f"Unknown template: {template}. Available templates: {', '.join(TEMPLATES)}")
    
    # Basic template filter
    filters = {
        'templates': [template]
    }
    
    # If max_tests is provided, sample the parameters
    if max_tests and max_tests > 0:
        # Calculate how many tests would be run without sampling
        subjects = TEMPLATE_SUBJECTS[template]
        total_combinations = len(subjects) * len(LENGTH_OPTIONS) * len(AUDIENCE_LEVELS) * len(TONE_VARIATIONS)
        
        # If we need sampling
        if total_combinations > max_tests:
            filters['sample_size'] = max_tests
    
    return filters

def get_parameter_sensitivity_filters(parameter, values=None, templates=None, max_per_template=5):
    """Get filters for parameter sensitivity testing.
    
    Args:
        parameter: The parameter to test sensitivity for
        values: List of values to test (default: all possible values)
        templates: List of templates to test (default: all templates)
        max_per_template: Maximum tests per template
        
    Returns:
        Dictionary with filters
    """
    # Parameter validation
    if parameter not in ['length', 'audience', 'tone']:
        raise ValueError(f"Unknown parameter: {parameter}. Available parameters: length, audience, tone")
    
    # Default to all templates if not specified
    if not templates:
        templates = TEMPLATES
    elif not isinstance(templates, list):
        templates = [templates]
    
    # Get the available values for the parameter
    if parameter == 'length':
        all_values = LENGTH_OPTIONS
    elif parameter == 'audience':
        all_values = AUDIENCE_LEVELS
    elif parameter == 'tone':
        all_values = TONE_VARIATIONS
    
    # Use provided values or all possible values
    if not values:
        values = all_values
    elif not isinstance(values, list):
        values = [values]
    
    # Validate values
    for value in values:
        if value not in all_values:
            raise ValueError(f"Invalid {parameter} value: {value}. Available values: {', '.join(all_values)}")
    
    # Create filters
    filters = {
        'templates': templates,
        'max_per_template': max_per_template,
        'balanced': True
    }
    
    # If testing a specific parameter, only vary that parameter
    if parameter == 'length':
        filters['lengths'] = values
        # Fix other parameters to mid-range values
        filters['audience'] = 'intermediate'
        filters['tone'] = 'informative'
    elif parameter == 'audience':
        filters['audiences'] = values
        # Fix other parameters to mid-range values
        filters['length'] = 'medium'
        filters['tone'] = 'informative'
    elif parameter == 'tone':
        filters['tones'] = values
        # Fix other parameters to mid-range values
        filters['length'] = 'medium'
        filters['audience'] = 'intermediate'
    
    return filters

def get_sample_based_filters(sample_size=5, strategy="balanced"):
    """Get filters for sample-based testing.
    
    Args:
        sample_size: Number of test cases to sample
        strategy: Sampling strategy (balanced, random)
        
    Returns:
        Dictionary with filters
    """
    if strategy == "balanced":
        # Ensure equal representation across templates
        per_template = max(1, sample_size // len(TEMPLATES))
        return {
            'balanced': True,
            'max_per_template': per_template,
            'total_samples': sample_size
        }
    elif strategy == "random":
        # Random sampling across all test cases
        return {
            'sample_size': sample_size,
            'random': True
        }
    else:
        raise ValueError(f"Unknown sampling strategy: {strategy}. Available strategies: balanced, random")

def get_full_matrix_filters():
    """Get filters for running the full test matrix.
    
    Returns:
        Empty dictionary (no filters)
    """
    return {}

def apply_approach_filters(approach, **kwargs):
    """Apply filters based on the selected testing approach.
    
    Args:
        approach: Name of the testing approach
        **kwargs: Additional parameters for the approach
        
    Returns:
        Dictionary with filters
    """
    if approach == "template-focused":
        required_params = ['template']
        for param in required_params:
            if param not in kwargs:
                raise ValueError(f"Missing required parameter for {approach} approach: {param}")
        return get_template_focused_filters(
            template=kwargs['template'],
            max_tests=kwargs.get('max_tests')
        )
    elif approach == "parameter-sensitivity":
        required_params = ['parameter']
        for param in required_params:
            if param not in kwargs:
                raise ValueError(f"Missing required parameter for {approach} approach: {param}")
        return get_parameter_sensitivity_filters(
            parameter=kwargs['parameter'],
            values=kwargs.get('values'),
            templates=kwargs.get('templates'),
            max_per_template=kwargs.get('max_per_template', 5)
        )
    elif approach == "sample-based":
        return get_sample_based_filters(
            sample_size=kwargs.get('sample_size', 5),
            strategy=kwargs.get('strategy', 'balanced')
        )
    elif approach == "full-matrix":
        return get_full_matrix_filters()
    else:
        raise ValueError(f"Unknown testing approach: {approach}. Available approaches: {', '.join(APPROACHES.keys())}")

def filter_test_cases_by_approach(approach, get_all_test_cases=False, **kwargs):
    """Get test cases filtered by the selected testing approach.
    
    Args:
        approach: Name of the testing approach
        get_all_test_cases: Whether to generate all test cases first (may be memory intensive)
        **kwargs: Additional parameters for the approach
        
    Returns:
        List of filtered test cases
    """
    # Get filters for the selected approach
    filters = apply_approach_filters(approach, **kwargs)
    
    # Apply sampling if needed
    sample_size = filters.pop('sample_size', None)
    max_per_template = filters.pop('max_per_template', None)
    balanced = filters.pop('balanced', False)
    random_sampling = filters.pop('random', False)
    
    # Get all test cases first if requested or needed for random sampling
    if get_all_test_cases or random_sampling:
        all_test_cases = get_filtered_test_cases(filters)
        
        # Apply random sampling if required
        if random_sampling and sample_size:
            # Randomly sample the requested number of test cases
            return random.sample(all_test_cases, min(sample_size, len(all_test_cases)))
    
    # For balanced sampling, we need to handle it specially
    if balanced and max_per_template:
        result = []
        
        # Get templates to sample from
        templates = filters.get('templates', TEMPLATES)
        
        # For each template, sample the requested number of test cases
        for template in templates:
            template_filters = dict(filters)
            template_filters['templates'] = [template]
            
            # Get test cases for this template
            template_cases = get_filtered_test_cases(template_filters)
            
            # Randomly sample the requested number of test cases
            sampled = random.sample(template_cases, min(max_per_template, len(template_cases)))
            result.extend(sampled)
        
        return result
    
    # Default: just apply the filters directly
    return get_filtered_test_cases(filters)

def get_interactive_filters():
    """Interactive menu for selecting test filters.
    
    Returns:
        Dictionary with user-selected filters
    """
    print("\n=== Cross-Template Testing Suite - Interactive Filter Selection ===\n")
    
    # Select testing approach
    print("Available testing approaches:")
    for i, (approach, description) in enumerate(APPROACHES.items(), 1):
        print(f"{i}. {approach}: {description}")
    
    approach_idx = int(input("\nSelect testing approach (1-4): ")) - 1
    selected_approach = list(APPROACHES.keys())[approach_idx]
    
    kwargs = {}
    
    # Handle approach-specific parameters
    if selected_approach == "template-focused":
        print("\nAvailable templates:")
        for i, template in enumerate(TEMPLATES, 1):
            print(f"{i}. {template}")
        
        template_idx = int(input("\nSelect template (1-5): ")) - 1
        kwargs['template'] = TEMPLATES[template_idx]
        
        max_tests = input("\nMaximum number of tests (leave blank for all): ")
        if max_tests.strip():
            kwargs['max_tests'] = int(max_tests)
            
    elif selected_approach == "parameter-sensitivity":
        print("\nParameter to test sensitivity for:")
        parameters = ['length', 'audience', 'tone']
        for i, param in enumerate(parameters, 1):
            print(f"{i}. {param}")
        
        param_idx = int(input("\nSelect parameter (1-3): ")) - 1
        kwargs['parameter'] = parameters[param_idx]
        
    elif selected_approach == "sample-based":
        sample_size = input("\nNumber of test cases to sample (default: 5): ")
        if sample_size.strip():
            kwargs['sample_size'] = int(sample_size)
        
        print("\nSampling strategy:")
        strategies = ['balanced', 'random']
        for i, strategy in enumerate(strategies, 1):
            print(f"{i}. {strategy}")
        
        strategy_idx = int(input("\nSelect strategy (1-2): ")) - 1
        kwargs['strategy'] = strategies[strategy_idx]
    
    # Show test count estimate
    filters = apply_approach_filters(selected_approach, **kwargs)
    test_count = estimate_test_count(filters)
    estimates = estimate_time_and_tokens(test_count)
    
    print("\n=== Test Execution Estimates ===")
    print(f"Number of test cases: {test_count}")
    print(f"Estimated time: {estimates['time']['formatted']}")
    print(f"Estimated token usage: {estimates['tokens']['total']:,}")
    print(f"Estimated cost (DeepSeek): ${estimates['tokens']['estimated_cost_deepseek']:.2f}")
    print(f"Estimated cost (Claude): ${estimates['tokens']['estimated_cost_claude']:.2f}")
    
    proceed = input("\nProceed with these filters? (y/n): ").lower()
    if proceed != 'y':
        print("Filter selection cancelled.")
        return None
    
    return {
        'approach': selected_approach,
        'kwargs': kwargs
    }

# Example usage:
# filters = apply_approach_filters("template-focused", template="Music Lesson", max_tests=10)
# test_cases = filter_test_cases_by_approach("sample-based", sample_size=5, strategy="balanced") 