"""
Cross-Template Testing Suite - Results Dashboard

This module provides a web interface for running tests and viewing results
from the cross-template testing suite.
"""

import os
import json
import glob
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import gradio as gr

from app.tests.test_runner import TestRunner
from app.tests.filter_presets import (
    APPROACHES, get_approach_description, apply_approach_filters, 
    filter_test_cases_by_approach, estimate_test_count, estimate_time_and_tokens
)
from app.tests.test_matrix import TEMPLATES, LENGTH_OPTIONS, AUDIENCE_LEVELS, TONE_VARIATIONS

# Constants
TEST_RESULTS_DIR = os.path.join('app', 'test_results')
CHART_COLORS = ["#4285F4", "#34A853", "#FBBC05", "#EA4335", "#8334A5"]

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
    if not os.path.exists(summary_path):
        return None
        
    with open(summary_path, 'r') as f:
        return json.load(f)

def get_run_test_cases(run_id):
    """Get all test cases for a test run.
    
    Args:
        run_id: ID of the test run (folder name)
        
    Returns:
        List of test case data dictionaries
    """
    run_dir = os.path.join(TEST_RESULTS_DIR, run_id)
    if not os.path.exists(run_dir):
        return []
        
    test_cases = []
    for file_path in glob.glob(os.path.join(run_dir, "*.json")):
        # Skip summary file
        if os.path.basename(file_path) == "summary.json":
            continue
            
        with open(file_path, 'r') as f:
            test_case = json.load(f)
            test_cases.append(test_case)
            
    return test_cases

def run_tests_from_ui(approach, template=None, parameter=None, parameter_values=None, 
                      sample_size=5, sample_strategy="balanced", max_workers=4):
    """Run tests with the specified configuration.
    
    Args:
        approach: Testing approach to use
        template: Template to focus on (for template-focused approach)
        parameter: Parameter to test (for parameter-sensitivity approach)
        parameter_values: Values to test for the parameter
        sample_size: Number of test cases to sample
        sample_strategy: Sampling strategy (for sample-based approach)
        max_workers: Maximum number of parallel test executions
        
    Returns:
        Path to results folder and summary data
    """
    # Prepare kwargs based on the approach
    kwargs = {}
    if approach == "template-focused" and template:
        kwargs["template"] = template
    elif approach == "parameter-sensitivity" and parameter:
        kwargs["parameter"] = parameter
        if parameter_values:
            kwargs["values"] = parameter_values.split(",")
    elif approach == "sample-based":
        kwargs["sample_size"] = sample_size
        kwargs["strategy"] = sample_strategy
    
    # Create test runner
    runner = TestRunner(max_workers=max_workers)
    
    # Run tests
    summary = runner.run_tests(approach=approach, **kwargs)
    
    # Return results
    return runner.output_dir, summary

def create_summary_charts(summary):
    """Create summary charts for a test run.
    
    Args:
        summary: Test run summary data
        
    Returns:
        List of matplotlib figures
    """
    figures = []
    
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
        bars = ax.bar(templates, success_rates, color=CHART_COLORS[:len(templates)])
        ax.set_ylim(0, 100)
        ax.set_xlabel('Template')
        ax.set_ylabel('Success Rate (%)')
        ax.set_title('Success Rate by Template')
        
        # Add value labels
        for bar in bars:
            height = bar.get_height()
            ax.annotate(f'{height:.1f}%',
                        xy=(bar.get_x() + bar.get_width() / 2, height),
                        xytext=(0, 3),
                        textcoords="offset points",
                        ha='center', va='bottom')
        
        plt.xticks(rotation=45)
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
        bars = ax.bar(templates, times, color=CHART_COLORS[1:len(templates)+1])
        ax.set_xlabel('Template')
        ax.set_ylabel('Average Generation Time (s)')
        ax.set_title('Generation Time by Template')
        
        # Add value labels
        for bar in bars:
            height = bar.get_height()
            ax.annotate(f'{height:.2f}s',
                        xy=(bar.get_x() + bar.get_width() / 2, height),
                        xytext=(0, 3),
                        textcoords="offset points",
                        ha='center', va='bottom')
        
        plt.xticks(rotation=45)
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

def view_test_details(test_id, run_id):
    """Get detailed information for a specific test case.
    
    Args:
        test_id: ID of the test case
        run_id: ID of the test run
        
    Returns:
        Dictionary with test details
    """
    if not test_id or not run_id:
        return {}
        
    file_path = os.path.join(TEST_RESULTS_DIR, run_id, f"{test_id}.json")
    if not os.path.exists(file_path):
        return {}
        
    with open(file_path, 'r') as f:
        return json.load(f)

def create_testing_dashboard():
    """Create the testing dashboard UI.
    
    Returns:
        Gradio Blocks interface
    """
    with gr.Blocks(title="Cross-Template Testing Suite") as dashboard:
        gr.Markdown("# Cross-Template Testing Suite Dashboard")
        
        with gr.Tabs():
            # Run New Tests Tab
            with gr.TabItem("Run New Tests"):
                with gr.Row():
                    with gr.Column(scale=1):
                        gr.Markdown("### Test Configuration")
                        
                        approach = gr.Dropdown(
                            choices=list(APPROACHES.keys()),
                            value="sample-based",
                            label="Testing Approach"
                        )
                        
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
                        if parameter_values_value:
                            kwargs["values"] = parameter_values_value.split(",")
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
                                     sample_size_value, sample_strategy_value, max_workers_value):
                    progress_output_value = "Starting tests..."
                    yield progress_output_value
                    
                    try:
                        output_dir, summary = run_tests_from_ui(
                            approach_value, template_value, parameter_value, parameter_values_value,
                            sample_size_value, sample_strategy_value, max_workers_value
                        )
                        
                        # Generate basic summary for progress output
                        success_rate = summary['success_rate'] * 100
                        progress_output_value = f"""
                        ## Test Run Complete
                        
                        - **Output Directory**: {output_dir}
                        - **Total Tests**: {summary['total_tests']}
                        - **Successful Tests**: {summary['successful_tests']}
                        - **Success Rate**: {success_rate:.1f}%
                        
                        View detailed results in the "View Results" tab.
                        """
                    except Exception as e:
                        progress_output_value = f"Error running tests: {str(e)}"
                    
                    yield progress_output_value
                
                run_btn.click(
                    fn=run_tests_wrapper,
                    inputs=[approach, template, parameter, parameter_values, sample_size, sample_strategy, max_workers],
                    outputs=[progress_output]
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
                                height=600
                            )
                            
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
                    
                    with gr.TabItem("Test Details"):
                        test_selector = gr.Dropdown(label="Select Test Case")
                        
                        with gr.Tabs():
                            with gr.TabItem("Test Case Configuration"):
                                test_config = gr.JSON(label="Test Configuration")
                            
                            with gr.TabItem("Generated Script"):
                                script_text = gr.Textbox(
                                    label="Generated Script",
                                    lines=20
                                )
                            
                            with gr.TabItem("Validation Results"):
                                validation_results = gr.JSON(label="Validation Results")
                
                # Handle run selection
                def update_run_data(run_id):
                    if not run_id:
                        return [None, None, pd.DataFrame(), []]
                    
                    # Get summary data
                    summary = get_run_summary(run_id)
                    if not summary:
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
                    
                    - **Run ID**: {run_id}
                    - **Timestamp**: {timestamp}
                    - **Total Tests**: {total_tests}
                    - **Successful Tests**: {successful_tests} ({success_rate:.1f}%)
                    - **Tests with Warnings**: {warnings_count}
                    """
                    
                    # Create charts
                    chart_figs = create_summary_charts(summary)
                    chart_images = []
                    for fig in chart_figs:
                        # Convert to image
                        chart_images.append(fig)
                    
                    # Get test results table
                    results_df = get_test_results_table(run_id)
                    
                    # Get test case IDs
                    test_ids = results_df['Test ID'].tolist() if not results_df.empty else []
                    
                    return [summary_text, chart_images, results_df, test_ids]
                
                def update_run_list_fn():
                    runs, run_labels = update_run_list()
                    return gr.Dropdown(choices=run_labels, value=run_labels[0] if run_labels else None)
                
                refresh_btn.click(
                    fn=update_run_list_fn,
                    inputs=[],
                    outputs=[run_dropdown]
                )
                
                run_dropdown.change(
                    fn=update_run_data,
                    inputs=[run_dropdown],
                    outputs=[summary_md, chart_gallery, results_table, test_selector]
                )
                
                # Handle test selection
                def update_test_details(test_id, run_id):
                    if not test_id or not run_id:
                        return [None, "", None]
                    
                    # Get test details
                    details = view_test_details(test_id, run_id.split(' - ')[0] if ' - ' in run_id else run_id)
                    if not details:
                        return [None, "", None]
                    
                    # Extract relevant information
                    config = details.get('test_case', {})
                    script = details.get('generated_script', '')
                    validation = details.get('validation', {})
                    
                    return [config, script, validation]
                
                test_selector.change(
                    fn=update_test_details,
                    inputs=[test_selector, run_dropdown],
                    outputs=[test_config, script_text, validation_results]
                )
                
                # Handle table filtering
                def filter_results_table(df, template_filter, success_filter):
                    if df.empty:
                        return df
                    
                    filtered_df = df.copy()
                    
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
                    
                    return filtered_df
                
                # Set up filtering
                filter_template.change(
                    fn=filter_results_table,
                    inputs=[results_table, filter_template, filter_success],
                    outputs=[results_table]
                )
                
                filter_success.change(
                    fn=filter_results_table,
                    inputs=[results_table, filter_template, filter_success],
                    outputs=[results_table]
                )
        
        # Initial data load
        dashboard.load(
            fn=update_run_list_fn,
            inputs=[],
            outputs=[run_dropdown]
        )
    
    return dashboard

def mount_testing_dashboard(app):
    """Mount the testing dashboard to the main Gradio application.
    
    Args:
        app: The main Gradio application
        
    Returns:
        Updated Gradio application
    """
    testing_dashboard = create_testing_dashboard()
    
    # Create a route for the testing dashboard
    @app.route("/testing")
    def testing_route():
        return testing_dashboard
    
    return app 