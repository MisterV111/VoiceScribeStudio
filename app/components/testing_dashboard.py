"""
Cross-Template Testing Suite - Results Dashboard

This module provides a web interface for running tests and viewing results
from the cross-template testing suite.
"""

import os
import json
import glob
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend to avoid threading issues
import matplotlib.pyplot as plt
from datetime import datetime
import gradio as gr
import time
import threading

from app.tests.test_runner import TestRunner
from app.tests.filter_presets import (
    APPROACHES, get_approach_description, apply_approach_filters, 
    filter_test_cases_by_approach, estimate_test_count, estimate_time_and_tokens
)
from app.tests.test_matrix import TEMPLATES, LENGTH_OPTIONS, AUDIENCE_LEVELS, TONE_VARIATIONS

# Constants
TEST_RESULTS_DIR = os.path.join('app', 'test_results')
CHART_COLORS = ["#4285F4", "#34A853", "#FBBC05", "#EA4335", "#8334A5"]

def format_test_configuration(config):
    """Format test case configuration as readable markdown.
    
    Args:
        config: Test case configuration dictionary
        
    Returns:
        Markdown formatted string with configuration details
    """
    if not config:
        return "No test configuration available."
    
    md_lines = []
    
    # Title with template name and icon
    template = config.get('template', 'Unknown')
    md_lines.append(f"## 📝 Test Configuration: {template}")
    md_lines.append("")
    
    # Basic information in a table-like format
    md_lines.append("### 📊 Basic Information")
    md_lines.append("")
    md_lines.append("| Parameter | Value |")
    md_lines.append("| --- | --- |")
    md_lines.append(f"| **Subject** | {config.get('subject', 'N/A')} |")
    md_lines.append(f"| **Length** | {config.get('length', 'N/A')} |")
    md_lines.append(f"| **Audience** | {config.get('audience', 'N/A')} |")
    md_lines.append(f"| **Tone** | {config.get('tone', 'N/A')} |")
    md_lines.append("")
    
    # Word count requirements
    min_words = config.get('min_words', 'N/A')
    max_words = config.get('max_words', 'N/A')
    md_lines.append("### 📏 Length Requirements")
    md_lines.append("")
    md_lines.append(f"**Min Words:** `{min_words}`")
    md_lines.append(f"**Max Words:** `{max_words}`")
    md_lines.append("")
    
    # Additional parameters
    md_lines.append("### 🔍 Additional Parameters")
    md_lines.append("")
    
    # Filter out the basic parameters we've already displayed
    basic_params = {'template', 'subject', 'length', 'audience', 'tone', 'min_words', 'max_words'}
    additional_params = {k: v for k, v in config.items() if k not in basic_params}
    
    if additional_params:
        for key, value in additional_params.items():
            # Format the key name for better readability
            readable_key = key.replace('_', ' ').title()
            
            # Special handling for section markers and keywords
            if key == 'expected_sections':
                md_lines.append(f"**{readable_key}:** 📑")
                md_lines.append("")
                for item in value:
                    md_lines.append(f"- {item}")
                md_lines.append("")
            elif key == 'section_markers':
                md_lines.append(f"**{readable_key}:** 🏷️")
                md_lines.append("")
                for item in value:
                    md_lines.append(f"- `{item}`")
                md_lines.append("")
            elif key == 'keywords':
                md_lines.append(f"**{readable_key}:** 🔑")
                md_lines.append("")
                for item in value:
                    md_lines.append(f"- `{item}`")
                md_lines.append("")
            # Handle different value types
            elif isinstance(value, dict):
                md_lines.append(f"**{readable_key}:**")
                md_lines.append("")
                for sub_key, sub_value in value.items():
                    readable_sub_key = sub_key.replace('_', ' ').title()
                    md_lines.append(f"- **{readable_sub_key}:** `{sub_value}`")
                md_lines.append("")
            elif isinstance(value, list):
                md_lines.append(f"**{readable_key}:**")
                md_lines.append("")
                for item in value:
                    md_lines.append(f"- {item}")
                md_lines.append("")
            else:
                md_lines.append(f"**{readable_key}:** `{value}`")
                md_lines.append("")
    else:
        md_lines.append("No additional parameters.")
    
    return "\n".join(md_lines)

def format_validation_results(validation):
    """Format validation results as markdown for better readability.
    
    Args:
        validation: Validation data dictionary from test case
        
    Returns:
        Markdown formatted string with validation results
    """
    if not validation:
        return "No validation results available."
    
    md_lines = []
    
    # Overall status with icon
    success = validation.get('is_valid', False)
    status_icon = "✅" if success else "❌"
    md_lines.append(f"## {status_icon} Overall Result: {'PASSED' if success else 'FAILED'}")
    md_lines.append("")
    
    # Word count with icon
    word_count = validation.get('metrics', {}).get('word_count', 0)
    md_lines.append(f"**📊 Word Count:** `{word_count}`")
    md_lines.append("")
    
    # Add errors section with better formatting
    errors = validation.get('errors', [])
    if errors:
        md_lines.append(f"### ❌ Errors ({len(errors)})")
        md_lines.append("")
        for i, error in enumerate(errors, 1):
            md_lines.append(f"{i}. **{error}**")
        md_lines.append("")
    
    # Add warnings section with better formatting
    warnings = validation.get('warnings', [])
    if warnings:
        md_lines.append(f"### ⚠️ Warnings ({len(warnings)})")
        md_lines.append("")
        for i, warning in enumerate(warnings, 1):
            md_lines.append(f"{i}. {warning}")
        md_lines.append("")
    
    # Add check results in a more readable format
    checks = validation.get('checks', {})
    if checks:
        md_lines.append("### 🔍 Validation Checks")
        md_lines.append("")
        
        # First show failed checks
        failed_checks = {k: v for k, v in checks.items() if not v.get('pass', False)}
        if failed_checks:
            md_lines.append("#### Failed Checks")
            md_lines.append("")
            for check_name, check_result in failed_checks.items():
                readable_name = check_name.replace('check_', '').replace('_', ' ').title()
                check_desc = check_result.get('message', readable_name)
                md_lines.append(f"- ❌ **{readable_name}**: {check_desc}")
            md_lines.append("")
        
        # Then show passed checks
        passed_checks = {k: v for k, v in checks.items() if v.get('pass', False)}
        if passed_checks:
            md_lines.append("#### Passed Checks")
            md_lines.append("")
            for check_name, check_result in passed_checks.items():
                readable_name = check_name.replace('check_', '').replace('_', ' ').title()
                check_desc = check_result.get('message', readable_name)
                md_lines.append(f"- ✅ **{readable_name}**: {check_desc}")
            md_lines.append("")
    
    return "\n".join(md_lines)

def get_test_runs():
    """Get list of available test runs.
    
    Returns:
        List of test run folders sorted by date (newest first)
    """
    if not os.path.exists(TEST_RESULTS_DIR):
        return []
        
    runs = [d for d in os.listdir(TEST_RESULTS_DIR) 
            if os.path.isdir(os.path.join(TEST_RESULTS_DIR, d))]
    
    # Sort by date (newest first)
    runs.sort(reverse=True)
    
    return runs

def get_run_summary(run_id):
    """Get summary data for a test run.
    
    Args:
        run_id: ID of the test run (folder name)
        
    Returns:
        Dictionary with summary data or None if not found
    """
    summary_path = os.path.join(TEST_RESULTS_DIR, run_id, "summary.json")
    print(f"Attempting to read summary from: {summary_path}")
    
    if not os.path.exists(summary_path):
        print(f"Summary file not found: {summary_path}")
        return None
        
    try:
        with open(summary_path, 'r') as f:
            summary = json.load(f)
            print(f"Loaded summary for run {run_id}: {len(summary)} keys")
            return summary
    except Exception as e:
        print(f"Error loading summary file: {e}")
        return None

def get_run_test_cases(run_id):
    """Get all test cases for a test run.
    
    Args:
        run_id: ID of the test run (folder name)
        
    Returns:
        List of test case data dictionaries
    """
    run_dir = os.path.join(TEST_RESULTS_DIR, run_id)
    print(f"Looking for test cases in: {run_dir}")
    
    if not os.path.exists(run_dir):
        print(f"Test run directory not found: {run_dir}")
        return []
        
    test_cases = []
    json_files = glob.glob(os.path.join(run_dir, "*.json"))
    print(f"Found {len(json_files)} JSON files in {run_dir}")
    
    for file_path in json_files:
        # Skip summary file
        if os.path.basename(file_path) == "summary.json":
            continue
            
        try:
            with open(file_path, 'r') as f:
                test_case = json.load(f)
                test_cases.append(test_case)
        except Exception as e:
            print(f"Error loading test case file {file_path}: {e}")
            
    print(f"Loaded {len(test_cases)} test cases from {run_dir}")
    return test_cases

def run_tests_from_ui(approach_value, template_value, parameter_value, parameter_values_value, 
                   sample_size_value, sample_strategy_value, max_workers_value, force_fallback_value):
    """Run tests with the specified parameters.
    
    Args:
        approach_value: Testing approach to use
        template_value: Template for template-focused approach
        parameter_value: Parameter for parameter-sensitivity approach
        parameter_values_value: Parameter values for parameter-sensitivity approach
        sample_size_value: Sample size for sample-based approach
        sample_strategy_value: Sample strategy for sample-based approach
        max_workers_value: Maximum number of parallel workers
        force_fallback_value: Whether to force fallback to Claude model
        
    Returns:
        Tuple of (output directory, summary dictionary)
    """
    # Prepare kwargs based on the approach
    if approach_value == "template-focused":
        kwargs = {"template": template_value}
    elif approach_value == "parameter-sensitivity":
        kwargs = {"parameter": parameter_value}
        # Only split and add values if parameter_values_value is not empty
        if parameter_values_value and parameter_values_value.strip():
            kwargs["values"] = parameter_values_value.split(",")
        # If empty string, don't include values key (will use defaults)
    elif approach_value == "sample-based":
        kwargs = {"sample_size": sample_size_value, "strategy": sample_strategy_value}
    else:
        kwargs = {}
    
    # Create and run test runner
    runner = TestRunner(
        max_workers=max_workers_value,
        force_fallback=force_fallback_value
    )
    
    summary = runner.run_tests(approach=approach_value, **kwargs)
    
    return runner.output_dir, summary

def create_summary_charts(summary):
    """Create summary charts for a test run.
    
    Args:
        summary: Test run summary data
        
    Returns:
        List of matplotlib figures
    """
    figures = []
    
    # Set a modern style
    plt.style.use('seaborn-v0_8-pastel')
    
    # Custom color palette
    success_colors = ["#4285F4", "#34A853", "#FBBC05", "#EA4335", "#8334A5", "#00A4BD"]
    time_colors = ["#3498db", "#2ecc71", "#f1c40f", "#e74c3c", "#9b59b6", "#1abc9c"]
    
    # Success rate by template
    if 'template_stats' in summary:
        # Get data
        templates = []
        success_rates = []
        for template, stats in summary['template_stats'].items():
            templates.append(template)
            if 'success_rate' in stats:
                success_rates.append(stats['success_rate'] * 100)
            else:
                success_rates.append(stats['success'] / stats['total'] * 100 if stats['total'] > 0 else 0)
        
        # Create chart
        fig, ax = plt.subplots(figsize=(10, 6))
        bars = ax.bar(templates, success_rates, color=success_colors[:len(templates)])
        ax.set_ylim(0, 105)  # Add some room at the top for annotations
        ax.set_xlabel('Template', fontsize=12, fontweight='bold')
        ax.set_ylabel('Success Rate (%)', fontsize=12, fontweight='bold')
        ax.set_title('Success Rate by Template', fontsize=14, fontweight='bold')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.grid(axis='y', linestyle='--', alpha=0.7)
        
        # Add value labels
        for bar in bars:
            height = bar.get_height()
            ax.annotate(f'{height:.1f}%',
                        xy=(bar.get_x() + bar.get_width() / 2, height),
                        xytext=(0, 3),
                        textcoords="offset points",
                        ha='center', va='bottom',
                        fontsize=10, fontweight='bold')
        
        plt.xticks(rotation=30, ha='right', fontsize=10)
        plt.tight_layout()
        figures.append(fig)
    
    # Generation time by template
    if 'template_stats' in summary:
        # Get data
        templates = []
        times = []
        for template, stats in summary['template_stats'].items():
            templates.append(template)
            times.append(stats['avg_generation_time'])
        
        # Create chart
        fig, ax = plt.subplots(figsize=(10, 6))
        bars = ax.bar(templates, times, color=time_colors[:len(templates)])
        ax.set_xlabel('Template', fontsize=12, fontweight='bold')
        ax.set_ylabel('Average Generation Time (s)', fontsize=12, fontweight='bold')
        ax.set_title('Generation Time by Template', fontsize=14, fontweight='bold')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.grid(axis='y', linestyle='--', alpha=0.7)
        
        # Add value labels
        for bar in bars:
            height = bar.get_height()
            ax.annotate(f'{height:.2f}s',
                        xy=(bar.get_x() + bar.get_width() / 2, height),
                        xytext=(0, 3),
                        textcoords="offset points",
                        ha='center', va='bottom',
                        fontsize=10, fontweight='bold')
        
        plt.xticks(rotation=30, ha='right', fontsize=10)
        plt.tight_layout()
        figures.append(fig)
    
    # Add warnings/errors distribution chart (pie chart)
    if 'total_tests' in summary and summary['total_tests'] > 0:
        # Calculate data
        successful_no_warnings = summary.get('successful_tests', 0) - summary.get('warnings_count', 0)
        warnings_count = summary.get('warnings_count', 0)
        errors_count = summary.get('total_tests', 0) - summary.get('successful_tests', 0)
        
        # Only create chart if we have valid data
        if successful_no_warnings >= 0:  # Ensure we don't have negative values
            labels = ['Clean Success', 'Success with Warnings', 'Failures']
            sizes = [successful_no_warnings, warnings_count, errors_count]
            colors = ['#34A853', '#FBBC05', '#EA4335']
            
            # Remove any empty categories
            filtered_data = [(label, size, color) for label, size, color in zip(labels, sizes, colors) if size > 0]
            if filtered_data:
                labels, sizes, colors = zip(*filtered_data)
                
                fig, ax = plt.subplots(figsize=(10, 6))
                wedges, texts, autotexts = ax.pie(
                    sizes, 
                    labels=labels, 
                    colors=colors,
                    autopct='%1.1f%%', 
                    startangle=90,
                    wedgeprops={'edgecolor': 'w', 'linewidth': 1.5}
                )
                
                # Equal aspect ratio ensures that pie is drawn as a circle
                ax.axis('equal')  
                ax.set_title('Test Results Distribution', fontsize=14, fontweight='bold')
                
                # Style the label and percentage text
                for text in texts:
                    text.set_fontsize(11)
                for autotext in autotexts:
                    autotext.set_fontsize(10)
                    autotext.set_fontweight('bold')
                    
                plt.tight_layout()
                figures.append(fig)
    
    # Add word count vs expected length chart
    if 'template_stats' in summary:
        test_cases = []
        for run_dir in os.listdir(TEST_RESULTS_DIR):
            if run_dir == summary.get('output_dir', '').split('/')[-1]:
                for file_path in glob.glob(os.path.join(TEST_RESULTS_DIR, run_dir, "*.json")):
                    if os.path.basename(file_path) != "summary.json":
                        with open(file_path, 'r') as f:
                            data = json.load(f)
                            if 'test_case' in data and 'validation' in data and 'metrics' in data['validation']:
                                test_cases.append(data)
        
        if test_cases:
            # Extract word count and expected range data
            labels = [f"{tc['test_case']['template']}-{tc['test_case']['subject'][:10]}..." for tc in test_cases]
            word_counts = [tc['validation']['metrics'].get('word_count', 0) for tc in test_cases]
            min_words = [tc['test_case'].get('min_words', 0) for tc in test_cases]
            max_words = [tc['test_case'].get('max_words', 0) for tc in test_cases]
            
            # Create chart
            fig, ax = plt.subplots(figsize=(12, 6))
            x = range(len(labels))
            ax.bar(x, word_counts, color='#4285F4', alpha=0.7, label='Actual Word Count')
            
            # Add min/max lines
            for i, (min_val, max_val) in enumerate(zip(min_words, max_words)):
                ax.plot([i-0.4, i+0.4], [min_val, min_val], 'r--', alpha=0.7)
                ax.plot([i-0.4, i+0.4], [max_val, max_val], 'r--', alpha=0.7)
            
            ax.set_xticks(x)
            ax.set_xticklabels(labels, rotation=45, ha='right', fontsize=9)
            ax.set_xlabel('Test Cases', fontsize=12, fontweight='bold')
            ax.set_ylabel('Word Count', fontsize=12, fontweight='bold')
            ax.set_title('Word Count vs Expected Length Range', fontsize=14, fontweight='bold')
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.grid(axis='y', linestyle='--', alpha=0.7)
            
            # Add a legend explaining the red lines
            from matplotlib.lines import Line2D
            custom_lines = [Line2D([0], [0], color='r', linestyle='--', lw=2)]
            ax.legend(custom_lines, ['Min/Max Word Limits'], loc='upper right')
            
            plt.tight_layout()
            figures.append(fig)
    
    return figures

def update_run_list():
    """Update the list of available test runs.
    
    Returns:
        List of run IDs, list of run labels
    """
    runs = get_test_runs()
    run_labels = []
    
    for run_id in runs:
        summary = get_run_summary(run_id)
        if summary:
            # Format timestamp
            ts = summary.get('timestamp', '')
            try:
                dt = datetime.fromisoformat(ts)
                ts_formatted = dt.strftime('%Y-%m-%d %H:%M:%S')
            except:
                ts_formatted = ts
                
            label = f"{run_id} - {ts_formatted} - {summary.get('total_tests', 0)} tests"
        else:
            label = run_id
            
        run_labels.append(label)
    
    return runs, run_labels

def get_test_results_table(run_id):
    """Get a DataFrame of test results for the specified run.
    
    Args:
        run_id: ID of the test run
        
    Returns:
        DataFrame with test results
    """
    test_cases = get_run_test_cases(run_id)
    if not test_cases:
        return pd.DataFrame()
    
    # Extract key information
    rows = []
    for tc in test_cases:
        test_case = tc.get('test_case', {})
        row = {
            'Test ID': tc.get('test_id', ''),
            'Template': test_case.get('template', ''),
            'Subject': test_case.get('subject', ''),
            'Length': test_case.get('length', ''),
            'Audience': test_case.get('audience', ''),
            'Tone': test_case.get('tone', ''),
            'Success': tc.get('success', False),
            'Warnings': len(tc.get('warnings', [])),
            'Errors': len(tc.get('errors', [])),
            'Generation Time': tc.get('timing', {}).get('generation', 0),
            'Word Count': tc.get('validation', {}).get('metrics', {}).get('word_count', 0)
        }
        rows.append(row)
    
    return pd.DataFrame(rows)

def create_testing_dashboard():
    """Create the testing dashboard UI.
    
    Returns:
        Gradio Blocks interface
    """
    # Add custom CSS for better markdown styling
    custom_css = """
    .md-content h2 {
        margin-top: 1.5rem;
        padding-bottom: 0.5rem;
        border-bottom: 1px solid rgba(0,0,0,0.1);
    }
    .md-content h3 {
        margin-top: 1.2rem;
        color: #444;
    }
    .md-content h4 {
        margin-top: 1rem;
        color: #555;
    }
    .md-content table {
        margin: 1rem 0;
        border-collapse: collapse;
        width: 100%;
    }
    .md-content th, .md-content td {
        padding: 0.5rem;
        border: 1px solid #ddd;
    }
    .md-content th {
        background-color: #f5f5f5;
    }
    .md-content code {
        background-color: #f0f0f0;
        padding: 0.1rem 0.3rem;
        border-radius: 3px;
        font-size: 0.9rem;
    }
    """
    
    with gr.Blocks(title="Cross-Template Testing Suite", css=custom_css) as dashboard:
        gr.Markdown("# Cross-Template Testing Suite Dashboard")
        
        with gr.Tabs():
            # Run New Tests Tab
            with gr.TabItem("Run New Tests"):
                with gr.Row():
                    with gr.Column(scale=2):
                        gr.Markdown("## Test Configuration")
                        
                        # Testing approach selection
                        approach = gr.Dropdown(
                            choices=list(APPROACHES.keys()),
                            value="sample-based",
                            label="Testing Approach"
                        )
                        approach_description = gr.Markdown()
                        
                        # Add a progress tracking section
                        gr.Markdown("### Test Progress")
                        with gr.Row():
                            test_progress = gr.Progress()
                        
                        progress_status = gr.Markdown("No test running")
                        
                        # Template-focused group
                        with gr.Group(visible=False) as template_group:
                            template = gr.Dropdown(
                                choices=TEMPLATES,
                                label="Template to Focus On"
                            )
                            
                        with gr.Group(visible=False) as parameter_group:
                            parameter = gr.Dropdown(
                                choices=["length", "audience", "tone"],
                                label="Parameter to Test"
                            )
                            parameter_values = gr.Textbox(
                                label="Parameter Values (comma-separated, leave empty for all)"
                            )
                            
                        with gr.Group(visible=False) as sample_group:
                            sample_size = gr.Slider(
                                minimum=1,
                                maximum=50,
                                value=5,
                                step=1,
                                label="Number of Test Cases to Sample"
                            )
                            sample_strategy = gr.Dropdown(
                                choices=["balanced", "random"],
                                value="balanced",
                                label="Sampling Strategy"
                            )
                            
                        max_workers = gr.Slider(
                            minimum=1,
                            maximum=8,
                            value=4,
                            step=1,
                            label="Maximum Parallel Workers"
                        )
                        
                        force_fallback = gr.Checkbox(
                            label="Force Claude Fallback",
                            value=False,
                            info="Force tests to use Claude instead of DeepSeek"
                        )
                        
                        estimate_btn = gr.Button("Estimate Resources")
                        run_btn = gr.Button("Run Tests", variant="primary")
                        
                    with gr.Column(scale=1):
                        gr.Markdown("### Resource Estimates")
                        
                        approach_desc = gr.Markdown()
                        test_count = gr.Number(label="Estimated Number of Tests", precision=0)
                        time_estimate = gr.Textbox(label="Estimated Execution Time")
                        token_estimate = gr.Number(label="Estimated Token Usage", precision=0)
                        cost_estimate = gr.Dataframe(
                            headers=["Model", "Estimated Cost ($)"],
                            label="Estimated Cost"
                        )
                        
                        with gr.Accordion("Description", open=False):
                            gr.Markdown("""
                            This panel allows you to configure and run tests with the Cross-Template Testing Suite.
                            
                            1. Select a testing approach
                            2. Configure approach-specific parameters
                            3. Estimate resources to see the impact of your configuration
                            4. Run the tests when you're satisfied with the configuration
                            
                            The results will appear in the "View Results" tab after the tests complete.
                            """)
                
                progress_output = gr.Markdown()
                
                # Handle approach selection to show/hide relevant groups
                def update_approach_groups(approach_value):
                    return {
                        template_group: approach_value == "template-focused",
                        parameter_group: approach_value == "parameter-sensitivity",
                        sample_group: approach_value == "sample-based"
                    }
                
                approach.change(
                    fn=update_approach_groups,
                    inputs=[approach],
                    outputs=[template_group, parameter_group, sample_group]
                )
                
                # Handle approach description
                def update_approach_desc(approach_value):
                    return f"**{approach_value}**: {get_approach_description(approach_value)}"
                
                approach.change(
                    fn=update_approach_desc,
                    inputs=[approach],
                    outputs=[approach_desc]
                )
                
                # Handle resource estimation
                def estimate_resources(approach_value, template_value, parameter_value, 
                                      parameter_values_value, sample_size_value, sample_strategy_value):
                    # Prepare kwargs based on the approach
                    kwargs = {}
                    if approach_value == "template-focused" and template_value:
                        kwargs["template"] = template_value
                    elif approach_value == "parameter-sensitivity" and parameter_value:
                        kwargs["parameter"] = parameter_value
                        # Only split and add values if parameter_values_value is not empty
                        if parameter_values_value and parameter_values_value.strip():
                            kwargs["values"] = parameter_values_value.split(",")
                        # If empty string, don't include values key (will use defaults)
                    elif approach_value == "sample-based":
                        kwargs["sample_size"] = sample_size_value
                        kwargs["strategy"] = sample_strategy_value
                    
                    # Apply filters and estimate
                    filters = apply_approach_filters(approach_value, **kwargs)
                    test_count_value = estimate_test_count(filters)
                    estimates = estimate_time_and_tokens(test_count_value)
                    
                    # Prepare cost dataframe
                    cost_df = pd.DataFrame([
                        ["DeepSeek", f"${estimates['tokens']['estimated_cost_deepseek']:.2f}"],
                        ["Claude", f"${estimates['tokens']['estimated_cost_claude']:.2f}"]
                    ], columns=["Model", "Estimated Cost ($)"])
                    
                    return [
                        test_count_value, 
                        estimates['time']['formatted'],
                        estimates['tokens']['total'],
                        cost_df
                    ]
                
                estimate_btn.click(
                    fn=estimate_resources,
                    inputs=[approach, template, parameter, parameter_values, sample_size, sample_strategy],
                    outputs=[test_count, time_estimate, token_estimate, cost_estimate]
                )
                
                # Handle running tests
                def run_tests_wrapper(approach_value, template_value, parameter_value, parameter_values_value, 
                                     sample_size_value, sample_strategy_value, max_workers_value, force_fallback_value,
                                     progress=gr.Progress()):
                    progress_output_value = "Starting tests..."
                    yield progress_output_value, "Initializing test run..."
                    
                    try:
                        # First, calculate estimated test count and time
                        if approach_value == "template-focused":
                            kwargs = {"template": template_value}
                        elif approach_value == "parameter-sensitivity":
                            kwargs = {"parameter": parameter_value}
                            # Only split and add values if parameter_values_value is not empty
                            if parameter_values_value and parameter_values_value.strip():
                                kwargs["values"] = parameter_values_value.split(",")
                            # If empty string, don't include values key (will use defaults)
                        elif approach_value == "sample-based":
                            kwargs = {"sample_size": sample_size_value, "strategy": sample_strategy_value}
                        else:
                            kwargs = {}
                            
                        test_filters = apply_approach_filters(approach_value, **kwargs)
                        test_count = estimate_test_count(test_filters)
                        estimates = estimate_time_and_tokens(test_count)
                        total_estimated_seconds = estimates['time']['total_seconds']
                        
                        # Set up custom test runner that reports progress
                        class ProgressReportingTestRunner(TestRunner):
                            def __init__(self, *args, **kwargs):
                                super().__init__(*args, **kwargs)
                                self.completed_tests = 0
                                self.start_time = time.time()
                                self.total_tests = test_count
                            
                            def run_single_test(self, test_case):
                                result = super().run_single_test(test_case)
                                self.completed_tests += 1
                                return result
                                
                            def get_progress_info(self):
                                elapsed_time = time.time() - self.start_time
                                completion_percentage = self.completed_tests / self.total_tests if self.total_tests > 0 else 0
                                
                                # Calculate estimated time remaining
                                if self.completed_tests > 0 and completion_percentage > 0:
                                    avg_time_per_test = elapsed_time / self.completed_tests
                                    estimated_total_time = avg_time_per_test * self.total_tests
                                    estimated_remaining = max(0, estimated_total_time - elapsed_time)
                                    
                                    # Format the time in a more readable way
                                    if estimated_remaining >= 3600:  # More than an hour
                                        hours = int(estimated_remaining // 3600)
                                        mins = int((estimated_remaining % 3600) // 60)
                                        secs = int(estimated_remaining % 60)
                                        remaining_formatted = f"{hours}h {mins}m {secs}s"
                                    elif estimated_remaining >= 60:  # More than a minute
                                        mins = int(estimated_remaining // 60)
                                        secs = int(estimated_remaining % 60)
                                        remaining_formatted = f"{mins}m {secs}s"
                                    else:  # Less than a minute
                                        remaining_formatted = f"{int(estimated_remaining)}s"
                                else:
                                    if total_estimated_seconds > 0:
                                        remaining_estimate = total_estimated_seconds * (1 - completion_percentage)
                                        if remaining_estimate >= 3600:
                                            hours = int(remaining_estimate // 3600)
                                            mins = int((remaining_estimate % 3600) // 60)
                                            secs = int(remaining_estimate % 60)
                                            remaining_formatted = f"{hours}h {mins}m {secs}s"
                                        elif remaining_estimate >= 60:
                                            mins = int(remaining_estimate // 60)
                                            secs = int(remaining_estimate % 60)
                                            remaining_formatted = f"{mins}m {secs}s"
                                        else:
                                            remaining_formatted = f"{int(remaining_estimate)}s"
                                    else:
                                        remaining_formatted = "Calculating..."
                                
                                return {
                                    'completed': self.completed_tests,
                                    'total': self.total_tests,
                                    'percentage': completion_percentage,
                                    'elapsed': elapsed_time,
                                    'remaining_formatted': remaining_formatted
                                }
                        
                        # Create test runner with progress reporting
                        runner = ProgressReportingTestRunner(
                            max_workers=max_workers_value,
                            force_fallback=force_fallback_value
                        )
                        
                        # Run tests with progress updates
                        thread = threading.Thread(
                            target=lambda: runner.run_tests(approach=approach_value, **kwargs)
                        )
                        thread.start()
                        
                        # Update progress while tests are running
                        last_completed = 0
                        while thread.is_alive():
                            # Sleep briefly to avoid excessive updates
                            time.sleep(0.5)
                            
                            # Get progress info
                            progress_info = runner.get_progress_info()
                            completed = progress_info['completed']
                            total = progress_info['total']
                            percentage = progress_info['percentage']
                            remaining_formatted = progress_info['remaining_formatted']
                            
                            # Only update UI if there's a change
                            if completed > last_completed:
                                last_completed = completed
                                # Update progress bar without showing percentage
                                progress(percentage, desc=f"Running tests ({completed}/{total})")
                                # Make time remaining more prominent with simpler formatting
                                status_text = f"**Completed {completed}/{total} tests**\n\n**Time remaining:** {remaining_formatted}"
                                yield progress_output_value, status_text
                        
                        # Get final summary
                        summary = runner._generate_summary()
                        summary['source'] = approach_value
                        summary['output_dir'] = runner.output_dir
                        
                        # Generate basic summary for progress output
                        success_rate = summary['success_rate'] * 100
                        progress_output_value = f"""
                        ## Test Run Complete
                        
                        - **Output Directory**: {runner.output_dir}
                        - **Total Tests**: {summary['total_tests']}
                        - **Successful Tests**: {summary['successful_tests']}
                        - **Success Rate**: {success_rate:.1f}%
                        
                        View detailed results in the "View Results" tab.
                        """
                        yield progress_output_value, "Test run complete!"
                        
                    except Exception as e:
                        progress_output_value = f"Error running tests: {str(e)}"
                        yield progress_output_value, "Error running tests!"
                
                run_btn.click(
                    fn=run_tests_wrapper,
                    inputs=[approach, template, parameter, parameter_values, sample_size, sample_strategy, max_workers, force_fallback],
                    outputs=[progress_output, progress_status]
                )
            
            # View Results Tab
            with gr.TabItem("View Results"):
                with gr.Row():
                    with gr.Column(scale=1):
                        refresh_btn = gr.Button("Refresh Run List")
                        run_dropdown = gr.Dropdown(label="Select Test Run")
                    
                    with gr.Column(scale=2):
                        summary_md = gr.Markdown()
                
                with gr.Tabs():
                    with gr.TabItem("Results Summary"):
                        with gr.Row():
                            chart_gallery = gr.Gallery(
                                label="Summary Charts",
                                show_label=True,
                                elem_id="chart_gallery",
                                columns=2,
                                rows=2,
                                height="auto",
                                object_fit="contain",
                                preview=True
                            )
                            
                            # Add a small explanation of the charts
                            with gr.Column(scale=1):
                                gr.Markdown("""
                                ### Charts Explanation
                                
                                - **Success Rate by Template**: Shows the percentage of tests that passed for each template
                                - **Generation Time by Template**: Shows the average time taken to generate scripts for each template
                                - **Test Results Distribution**: Breakdown of clean successes, tests with warnings, and failures
                                - **Word Count vs Expected Length**: Compares actual word count to the min/max requirements
                                
                                Use the filters in the Test Results Table tab to explore the data in more detail.
                                """)
                    
                    with gr.TabItem("Test Results Table"):
                        results_table = gr.DataFrame(
                            label="Test Results",
                            interactive=False
                        )
                        
                        with gr.Row():
                            filter_template = gr.Dropdown(
                                choices=["All"] + TEMPLATES,
                                value="All",
                                label="Filter by Template"
                            )
                            filter_success = gr.Dropdown(
                                choices=["All", "Success", "Warning", "Error"],
                                value="All",
                                label="Filter by Status"
                            )
                        
                        # Add a message area for filter status
                        filter_status = gr.Markdown("", elem_id="filter_status")
                    
                    with gr.TabItem("Test Details"):
                        test_selector = gr.Dropdown(label="Select Test Case")
                        
                        with gr.Tabs():
                            with gr.TabItem("Test Case Configuration"):
                                # Human-readable configuration summary
                                with gr.Column(elem_id="config-summary-box"):
                                    gr.Markdown("### 📝 Test Configuration Details")
                                    config_summary = gr.Markdown(elem_classes=["md-content"])
                                
                                # Add separator
                                gr.Markdown("---")
                                
                                # Raw configuration data
                                with gr.Accordion("Raw Configuration Data", open=False):
                                    test_config = gr.JSON(label="Test Configuration")
                            
                            with gr.TabItem("Generated Script"):
                                script_text = gr.Textbox(
                                    label="Generated Script",
                                    lines=25
                                )
                            
                            with gr.TabItem("Validation Results"):
                                # Human-readable validation summary
                                with gr.Column(elem_id="validation-summary-box"):
                                    gr.Markdown("### 🔍 Validation Results")
                                    validation_summary = gr.Markdown(elem_classes=["md-content"])
                                
                                # Add separator
                                gr.Markdown("---")
                                
                                # Raw validation data
                                with gr.Accordion("Raw Validation Data", open=False):
                                    validation_results = gr.JSON(label="Validation Results")
                
                # Handle run selection
                def update_run_data(run_id):
                    print(f"update_run_data called with run_id: {run_id}")
                    if not run_id:
                        print("No run_id provided")
                        return [None, None, pd.DataFrame(), []]
                    
                    # Extract just the run ID from the dropdown label if needed
                    clean_run_id = run_id.split(' - ')[0] if ' - ' in run_id else run_id
                    print(f"Cleaned run_id: {clean_run_id}")
                    
                    # Get summary data
                    summary = get_run_summary(clean_run_id)
                    if not summary:
                        print(f"No summary found for run_id: {clean_run_id}")
                        return [None, None, pd.DataFrame(), []]
                    
                    # Create summary markdown
                    timestamp = summary.get('timestamp', '')
                    try:
                        dt = datetime.fromisoformat(timestamp)
                        timestamp = dt.strftime('%Y-%m-%d %H:%M:%S')
                    except:
                        pass
                    
                    total_tests = summary.get('total_tests', 0)
                    successful_tests = summary.get('successful_tests', 0)
                    success_rate = summary.get('success_rate', 0) * 100
                    warnings_count = summary.get('warnings_count', 0)
                    
                    summary_text = f"""
                    ## Test Run Summary
                    
                    - **Run ID**: {clean_run_id}
                    - **Timestamp**: {timestamp}
                    - **Total Tests**: {total_tests}
                    - **Successful Tests**: {successful_tests} ({success_rate:.1f}%)
                    - **Tests with Warnings**: {warnings_count}
                    """
                    
                    # Create charts
                    print(f"Creating charts for run_id: {clean_run_id}")
                    chart_figs = create_summary_charts(summary)
                    chart_images = []
                    
                    # Convert matplotlib figures to images
                    import io
                    from PIL import Image
                    
                    for fig in chart_figs:
                        buf = io.BytesIO()
                        fig.savefig(buf, format='png', dpi=100)
                        buf.seek(0)
                        img = Image.open(buf)
                        chart_images.append(img)
                        plt.close(fig)  # Close figure to avoid memory leaks
                    
                    print(f"Created {len(chart_images)} charts")
                    
                    # Get test results table
                    results_df = get_test_results_table(clean_run_id)
                    print(f"Got test results table with {len(results_df)} rows")
                    
                    # Get test case IDs
                    test_ids = results_df['Test ID'].tolist() if not results_df.empty else []
                    print(f"Found {len(test_ids)} test IDs")
                    
                    # Explicitly handle the update for the test_selector dropdown
                    test_selector_update = gr.Dropdown(choices=test_ids, value=test_ids[0] if test_ids else None, 
                                                     label="Select Test Case")
                    
                    return [
                        summary_text, 
                        chart_images, 
                        results_df, 
                        test_selector_update # Return the updated component configuration
                    ]
                
                def update_run_list_fn():
                    """Update the list of available test runs.
                    
                    Returns:
                        Updated Dropdown component with test runs
                    """
                    runs, run_labels = update_run_list()
                    print(f"Found {len(runs)} test runs: {runs}")
                    print(f"Run labels: {run_labels}")
                    
                    # Handle the case where there are no runs yet
                    if not run_labels:
                        # Create dropdown without placeholder
                        return gr.Dropdown(choices=[], value=None, label="Select Test Run")
                    
                    dropdown = gr.Dropdown(choices=run_labels, value=run_labels[0] if run_labels else None, label="Select Test Run")
                    print(f"Returning dropdown with {len(run_labels)} choices")
                    return dropdown
                
                refresh_btn.click(
                    fn=update_run_list_fn,
                    inputs=[],
                    outputs=[run_dropdown]
                )
                
                # When run is selected, reset filters first then update data
                def run_dropdown_change(run_id):
                    # Reset filters to All first
                    filt_template = gr.Dropdown(value="All")
                    filt_success = gr.Dropdown(value="All")
                    
                    # Then get the updated data
                    summary_text, charts, results_df, test_selector_update = update_run_data(run_id)
                    
                    # Update filter status
                    filter_msg = f"Showing all {len(results_df)} results. No filters applied." if not results_df.empty else ""
                    
                    return [filt_template, filt_success, summary_text, charts, results_df, test_selector_update, filter_msg]
                
                run_dropdown.change(
                    fn=run_dropdown_change,
                    inputs=[run_dropdown],
                    outputs=[filter_template, filter_success, summary_md, chart_gallery, results_table, test_selector, filter_status]
                )
                
                # Handle test selection
                def update_test_details(test_id, run_id):
                    print(f"update_test_details called with test_id: {test_id}, run_id: {run_id}")
                    if not test_id or not run_id:
                        return [None, "", "", None, ""]
                    
                    # Extract the clean run ID from the dropdown label if needed
                    clean_run_id = run_id.split(' - ')[0] if ' - ' in run_id else run_id
                    
                    # Get test details
                    file_path = os.path.join(TEST_RESULTS_DIR, clean_run_id, f"{test_id}.json")
                    if not os.path.exists(file_path):
                        return [None, "", "", None, ""]
                    
                    with open(file_path, 'r') as f:
                        details = json.load(f)
                    
                    # Extract relevant information
                    config = details.get('test_case', {})
                    script = details.get('generated_script', '')
                    validation = details.get('validation', {})
                    
                    # Format test configuration for better readability
                    config_md = format_test_configuration(config)
                    print(f"Generated config summary with {len(config_md)} characters")
                    
                    # Format validation results
                    validation_md = format_validation_results(validation)
                    print(f"Generated validation summary with {len(validation_md)} characters")
                    
                    return [config, script, validation_md, validation, config_md]
                
                test_selector.change(
                    fn=update_test_details,
                    inputs=[test_selector, run_dropdown],
                    outputs=[test_config, script_text, validation_summary, validation_results, config_summary]
                )
                
                # Handle table filtering
                def filter_results_table(df, template_filter, success_filter):
                    if df.empty:
                        return [df, "No data available to filter."]
                    
                    # Get the original dataframe if this is a filtered one
                    # This ensures we always filter from the complete dataset
                    if hasattr(df, '_original_df'):
                        original_df = df._original_df
                    else:
                        # First time filtering, store the original
                        original_df = df.copy()
                    
                    # Start with the original dataframe
                    filtered_df = original_df.copy()
                    
                    # Filter by template
                    if template_filter != "All":
                        filtered_df = filtered_df[filtered_df['Template'] == template_filter]
                    
                    # Filter by success status
                    if success_filter == "Success":
                        filtered_df = filtered_df[filtered_df['Success'] == True]
                    elif success_filter == "Warning":
                        filtered_df = filtered_df[(filtered_df['Success'] == True) & (filtered_df['Warnings'] > 0)]
                    elif success_filter == "Error":
                        filtered_df = filtered_df[filtered_df['Success'] == False]
                    
                    # Store a reference to the original dataframe
                    filtered_df._original_df = original_df
                    
                    # Create status message
                    status_msg = ""
                    if filtered_df.empty and not original_df.empty:
                        status_msg = f"⚠️ No results match the filter: Template={template_filter}, Status={success_filter}"
                    else:
                        filter_desc = []
                        if template_filter != "All":
                            filter_desc.append(f"Template: {template_filter}")
                        if success_filter != "All":
                            filter_desc.append(f"Status: {success_filter}")
                        
                        if filter_desc:
                            status_msg = f"Showing {len(filtered_df)} of {len(original_df)} results. Filters: {', '.join(filter_desc)}"
                        else:
                            status_msg = f"Showing all {len(filtered_df)} results. No filters applied."
                    
                    return [filtered_df, status_msg]
                
                # Set up filtering
                filter_template.change(
                    fn=filter_results_table,
                    inputs=[results_table, filter_template, filter_success],
                    outputs=[results_table, filter_status]
                )
                
                filter_success.change(
                    fn=filter_results_table,
                    inputs=[results_table, filter_template, filter_success],
                    outputs=[results_table, filter_status]
                )
        
        # Initial data load for test runs list
        dashboard.load(
            fn=update_run_list_fn,
            inputs=[],
            outputs=[run_dropdown]
        )
        
        # Automatically trigger the first run selection to load data
        def auto_load_first_run():
            runs, run_labels = update_run_list()
            if run_labels:
                return run_dropdown_change(run_labels[0])
            else:
                return [gr.Dropdown(value="All"), gr.Dropdown(value="All"), None, None, pd.DataFrame(), None, "No test runs found."]
        
        # Schedule the automatic load after UI is ready
        dashboard.load(
            fn=auto_load_first_run,
            inputs=[],
            outputs=[filter_template, filter_success, summary_md, chart_gallery, results_table, test_selector, filter_status]
        )
    
    return dashboard 