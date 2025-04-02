# Tests Directory

This directory contains test scripts and files for VoiceScribe Studio.

## Available Tests

- `test_deepseek.py` - Tests for DeepSeek API connectivity and script generation
- `test_claude.py` - Tests for Anthropic Claude API connectivity and fallback functionality
- `test_elevenlabs.py` - Tests for ElevenLabs API connectivity and voice synthesis
- `debug_elevenlabs.py` - Debugging script for ElevenLabs API issues

## Cross-Template Testing Suite

VoiceScribe Studio includes a comprehensive cross-template testing suite for validating script generation across all templates and models. This testing system is accessible through:

1. Command-line: Run tests via the `app.tests.run_tests` module
2. Web interface: Access via the "Test Suite" button in the main application

### Web Interface Access
- URL: http://localhost:7861/ (when application is running)
- Username: `admin`
- Password: `testingsuite`

### Features
- Automated testing of all templates with various parameter combinations
- Integration with both DeepSeek R1 (primary) and Claude 3.7 Sonnet (fallback) models
- Forced fallback testing scenarios to validate model resilience
- Formatted test results with color-coded pass/fail indicators
- Detailed validation results for troubleshooting
- Script output inspection and comparison tools
- Interactive dashboard with filtering capabilities

## Running Tests

To run a test:

```bash
# Basic API tests
python -m tests.test_deepseek
python -m tests.test_claude
python -m tests.test_elevenlabs

# Cross-Template Testing Suite
python -m app.tests.run_tests                                # Run all tests with DeepSeek (primary)
python -m app.tests.run_tests --templates "Technical Tutorial"  # Test specific template
python -m app.tests.run_tests --force-fallback                # Test with Claude fallback model
python -m app.tests.run_tests --audience "Expert"             # Test with specific audience level
```

## Test Assets

This directory also contains test assets like sample audio files used for testing.

## Test Results

Test results are stored in the `app/tests/results` directory and can be viewed through the testing dashboard interface. The dashboard provides:

- Summary statistics of test runs
- Detailed view of individual test cases
- Ability to filter results by template, model, or test status
- Export capabilities for test reports

