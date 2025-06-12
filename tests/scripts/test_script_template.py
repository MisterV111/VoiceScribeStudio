"""
Script Template Test - Quick Copy Template

This is a simplified template for testing script templates in VoiceScribe Studio.
Copy this file and modify the parameters to test your specific template.
"""

from dotenv import load_dotenv
import os
from app.utils.llm_clients import generate_script
from app.utils.token_counter import token_tracker

# Load environment variables
load_dotenv()

# CUSTOMIZE THESE VALUES FOR YOUR TEST
TEMPLATE_NAME = "Your Template Name"  # e.g., "Music Lesson", "Corporate Training", etc.
TEST_PROMPT = "Test script about [your topic]"
TEST_SUBJECT = "Your Subject"
TEST_CONTEXT = "Additional context to provide for the script generation."

# Test different variations
TEST_AUDIENCES = ["general", "beginner", "advanced"]
TEST_LENGTHS = ["short", "medium", "long"]
TEST_TONES = ["informative", "conversational", "professional"]

# Expected keywords for validation (customize these based on your template)
EXPECTED_KEYWORDS = ["keyword1", "keyword2", "keyword3"]

def run_basic_test():
    """Run a basic test for the template"""
    print(f"Testing template: {TEMPLATE_NAME}")
    print("-" * 50)
    
    # Generate a script with basic parameters
    script = generate_script(
        prompt=TEST_PROMPT,
        subject=TEST_SUBJECT,
        length="medium",
        audience="general",
        tone="informative",
        template=TEMPLATE_NAME,
        context=TEST_CONTEXT,
        is_test=True  # Mark as test to avoid affecting analytics
    )
    
    # Validate the script
    if not script:
        print(f"❌ ERROR: Failed to generate script with template: {TEMPLATE_NAME}")
        return False
        
    print(f"✅ Script generated successfully ({len(script)} characters, ~{len(script.split())} words)")
    
    # Check for expected keywords
    missing_keywords = [kw for kw in EXPECTED_KEYWORDS if kw.lower() not in script.lower()]
    if missing_keywords:
        print(f"⚠️ WARNING: Script is missing expected keywords: {', '.join(missing_keywords)}")
    else:
        print(f"✅ All expected keywords found in the script")
    
    # Print a preview of the script
    print("\nScript Preview (first 300 characters):")
    print("-" * 50)
    print(script[:300] + "...")
    print("-" * 50)
    
    return True

def run_variation_tests():
    """Run tests with different parameter variations"""
    print("\nRunning variation tests...")
    
    # Test different audience types
    for audience in TEST_AUDIENCES:
        print(f"\nTesting with audience: {audience}")
        script = generate_script(
            prompt=TEST_PROMPT,
            subject=TEST_SUBJECT,
            length="medium",
            audience=audience,
            tone="informative",
            template=TEMPLATE_NAME,
            context=TEST_CONTEXT,
            is_test=True
        )
        if script:
            print(f"✅ {audience.capitalize()} audience script generated: ~{len(script.split())} words")
        else:
            print(f"❌ Failed to generate script for {audience} audience")
    
    # Test different lengths
    for length in TEST_LENGTHS:
        print(f"\nTesting with length: {length}")
        script = generate_script(
            prompt=TEST_PROMPT,
            subject=TEST_SUBJECT,
            length=length,
            audience="general",
            tone="informative",
            template=TEMPLATE_NAME,
            context=TEST_CONTEXT,
            is_test=True
        )
        if script:
            word_count = len(script.split())
            print(f"✅ {length.capitalize()} length script generated: ~{word_count} words")
        else:
            print(f"❌ Failed to generate script with {length} length")
    
    # Test different tones
    for tone in TEST_TONES:
        print(f"\nTesting with tone: {tone}")
        script = generate_script(
            prompt=TEST_PROMPT,
            subject=TEST_SUBJECT,
            length="medium",
            audience="general",
            tone=tone,
            template=TEMPLATE_NAME,
            context=TEST_CONTEXT,
            is_test=True
        )
        if script:
            print(f"✅ {tone.capitalize()} tone script generated: ~{len(script.split())} words")
        else:
            print(f"❌ Failed to generate script with {tone} tone")

def verify_token_tracking():
    """Verify that token tracking is working properly"""
    print("\nVerifying token tracking...")
    
    # Get recent usage data
    summary = token_tracker.get_usage_summary(days=1, include_tests=True)
    
    # Verify that tests were recorded
    if summary.get('error'):
        print(f"❌ Error retrieving token usage data: {summary.get('error')}")
        return False
        
    if summary.get('total_requests', 0) > 0:
        print(f"✅ Token tracking is working: {summary.get('total_requests', 0)} requests recorded")
        return True
    else:
        print("❌ No requests recorded in token tracking")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print(f"TEMPLATE TEST: {TEMPLATE_NAME}")
    print("=" * 50)
    
    # Run tests
    basic_test_passed = run_basic_test()
    
    if basic_test_passed:
        run_variation_tests()
        verify_token_tracking()
    
    print("\nTest complete!") 