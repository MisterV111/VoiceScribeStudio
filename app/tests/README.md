# VoiceScribe Studio Cross-Template Testing Suite

This directory contains the automated testing suite for validating script generation across all templates in VoiceScribe Studio.

## Overview

The Cross-Template Testing Suite tests script generation quality, consistency, and performance across all templates and parameter combinations. It provides objective metrics and validation to ensure that:

- All templates maintain high quality regardless of parameter settings
- Generated scripts meet expected structure and content requirements
- Template markers are not present in final output
- Scripts are appropriate for the target audience
- Requested tone is maintained throughout the script

## Usage

### Running Tests

From the project root, you can run the test suite with:

```bash
# Run all tests
python -m app.tests.run_tests

# Run tests for specific templates
python -m app.tests.run_tests --templates "Technical Tutorial,Marketing"

# Run tests with specific parameters
python -m app.tests.run_tests --audience beginner --length short

# Force fallback to Claude (secondary model)
python -m app.tests.run_tests --force-fallback
```

### Accessing Results

Test results are saved to the `app/test_results/[timestamp]` directory with:

- Individual JSON files for each test case
- A summary JSON file with aggregate metrics
- Detailed logs in the `test_run.log` file

## Components

The testing suite consists of several key components:

1. **Test Runner** (`test_runner.py`): Orchestrates the test execution
2. **Test Matrix** (`test_matrix.py`): Defines all test cases and parameters
3. **Validators** (`validators.py`): Validates script output against expectations
4. **Test Logging** (`../utils/test_logging.py`): Provides structured logging

## Test Cases

The test matrix covers all combinations of:

- Templates (Business Training, Marketing, General Education, Technical Tutorial, Music Lesson)
- Length options (short, medium, long)
- Audience levels (beginner, intermediate, expert)
- Tone variations (informative, conversational, persuasive, enthusiastic, professional)
- Subject matter (5 subjects per template)

## Validation Criteria

Each script is validated against several criteria:

- Word count within expected range
- Presence of expected sections
- Inclusion of template-specific keywords
- Absence of template markers
- Appropriate language for target audience
- Consistency with requested tone

## Adding New Tests

To add new test cases:

1. Update `test_matrix.py` with new templates, subjects, or parameters
2. Add template-specific validation in `validators.py` if needed
3. Run the tests to verify the new cases 