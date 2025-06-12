import os, sys, json, pandas as pd
sys.path.insert(0, os.getcwd())
from app.components.testing_dashboard import get_test_runs, get_run_summary, get_run_test_cases, get_test_results_table
TEST_RESULTS_DIR = os.path.join('app', 'test_results')
print('Checking test results...')
runs = get_test_runs()
print(f'Found {len(runs)} runs: {runs}')
if runs:
    # Get first run and summary
    run_id = runs[0]
    print(f'Testing with run_id: {run_id}')
    # Test get_run_summary function
    summary = get_run_summary(run_id)
    print(f'Summary: {summary is not None}')
    # Test get_test_results_table function
    results_table = get_test_results_table(run_id)
    print(f'Results table: {len(results_table)} rows')
