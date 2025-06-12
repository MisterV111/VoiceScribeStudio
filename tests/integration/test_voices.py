#!/usr/bin/env python
'''
Voice Test Script

This script tests all voices in the VoiceScribe Studio library by
generating a short audio clip for each voice and recording whether
the generation was successful or not.
'''

import os
import sys
import time
import tempfile
from dotenv import load_dotenv

# Add the parent directory to the path so we can import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables
load_dotenv()

# Import necessary functions from the app
from app.utils.tts_clients import generate_audio
from app.main import load_voices

# Define a test script - short enough to be economical, but long enough to test voice characteristics
TEST_SCRIPT = """
Welcome to VoiceScribe Studio! This is a short test to verify that this voice is functioning correctly.
I'll demonstrate a few characteristics of my voice, including some basic inflection and emotion.
Is this voice working as expected? Let me know if you can hear this clearly.
Thank you for testing our voice library, and have a wonderful day!
"""

def test_voice(voice_id, voice_name):
    """
    Test a single voice by generating a short audio clip.
    
    Args:
        voice_id (str): The ID of the voice to test
        voice_name (str): The name of the voice for logging
        
    Returns:
        tuple: (success (bool), error_message (str or None))
    """
    print(f"Testing voice: {voice_name} (ID: {voice_id})")
    
    # Create a temporary output path
    with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as temp_file:
        output_path = temp_file.name
    
    try:
        # Generate audio with the voice
        start_time = time.time()
        audio_bytes, file_path, is_premium = generate_audio(
            script=TEST_SCRIPT,
            voice_id=voice_id,
            output_path=output_path,
            stability=0.5,
            similarity=0.75,
            style=0.0,
            speed=1.0,
            use_speaker_boost=False
        )
        elapsed_time = time.time() - start_time
        
        # Check if generation was successful
        if audio_bytes and file_path:
            print(f"✅ SUCCESS: {voice_name} - Generated in {elapsed_time:.2f} seconds")
            # Clean up temporary file
            try:
                os.remove(file_path)
            except:
                pass
            return True, None
        else:
            error_msg = f"❌ FAILED: {voice_name} - No audio generated"
            print(error_msg)
            return False, error_msg
    except Exception as e:
        error_msg = f"❌ FAILED: {voice_name} - Error: {str(e)}"
        print(error_msg)
        return False, error_msg
    finally:
        # Clean up temporary file if it exists
        try:
            if os.path.exists(output_path):
                os.remove(output_path)
        except:
            pass

def run_voice_tests():
    """
    Test all voices in the library and log the results.
    """
    # Get all voices from the app
    preset_voice_names, preset_voice_ids, _, _ = load_voices()
    
    # Create a results directory
    results_dir = "test_results"
    os.makedirs(results_dir, exist_ok=True)
    
    # Generate a timestamp for the results file
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    results_file = os.path.join(results_dir, f"voice_test_results_{timestamp}.txt")
    
    # Prepare results tracking
    successful_voices = []
    failed_voices = []
    
    # Log the start of testing
    print(f"\n{'='*80}\nSTARTING VOICE TESTS\n{'='*80}")
    print(f"Testing {len(preset_voice_ids)} voices...")
    
    # Test each voice
    for i, (voice_name, voice_id) in enumerate(zip(preset_voice_names, preset_voice_ids)):
        print(f"\nTest {i+1}/{len(preset_voice_ids)}")
        success, error = test_voice(voice_id, voice_name)
        
        if success:
            successful_voices.append(voice_name)
        else:
            failed_voices.append((voice_name, error))
        
        # Add a small delay between tests to avoid rate limiting
        if i < len(preset_voice_ids) - 1:
            time.sleep(1)
    
    # Log the summary
    print(f"\n{'='*80}\nTEST SUMMARY\n{'='*80}")
    print(f"Total voices tested: {len(preset_voice_ids)}")
    print(f"Successful: {len(successful_voices)} ({len(successful_voices)/len(preset_voice_ids)*100:.1f}%)")
    print(f"Failed: {len(failed_voices)} ({len(failed_voices)/len(preset_voice_ids)*100:.1f}%)")
    
    # Write results to file
    with open(results_file, 'w') as f:
        f.write(f"VOICE TEST RESULTS - {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"{'='*80}\n\n")
        
        f.write(f"Total voices tested: {len(preset_voice_ids)}\n")
        f.write(f"Successful: {len(successful_voices)} ({len(successful_voices)/len(preset_voice_ids)*100:.1f}%)\n")
        f.write(f"Failed: {len(failed_voices)} ({len(failed_voices)/len(preset_voice_ids)*100:.1f}%)\n\n")
        
        f.write("SUCCESSFUL VOICES:\n")
        f.write(f"{'-'*80}\n")
        for voice in successful_voices:
            f.write(f"✅ {voice}\n")
        
        f.write("\nFAILED VOICES:\n")
        f.write(f"{'-'*80}\n")
        for voice, error in failed_voices:
            f.write(f"❌ {voice}: {error}\n")
    
    print(f"\nDetailed results saved to: {results_file}")
    return successful_voices, failed_voices, results_file

if __name__ == "__main__":
    successful, failed, results_file = run_voice_tests()
    
    # Print the successful and failed voices
    print("\nSUCCESSFUL VOICES:")
    for voice in successful:
        print(f"✅ {voice}")
    
    print("\nFAILED VOICES:")
    for voice, error in failed:
        print(f"❌ {voice}") 