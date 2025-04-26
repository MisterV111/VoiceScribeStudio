#!/usr/bin/env python3
"""
Test a few sample voices from our updated list to ensure they're working
"""

import os
import requests
import json
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get API key from environment variables or enter it directly
XI_API_KEY = os.getenv("ELEVENLABS_API_KEY", "")
if not XI_API_KEY:
    XI_API_KEY = input("Enter your ElevenLabs API Key: ")

# Voice IDs to test (sample from different categories)
VOICES_TO_TEST = [
    {"name": "Aria (New voice)", "id": "9BWtsMINqrJLrRacOk9x"},
    {"name": "Sarah (Previously Bella)", "id": "EXAVITQu4vr4xnSDxMaL"},
    {"name": "Dan Teacher - Hybrid", "id": "jn5Dym9tbXQdxJRlyYzZ"},
    {"name": "Dan Teacher - Neutral", "id": "CMtJJeUfoLE6mZYBmsFl"},
    {"name": "Dan Teacher - Upbeat", "id": "W14NZHmEOKlltX7Dhrac"},
    {"name": "Lily (Previously Adam)", "id": "pFZP5JQG7iQjIQuC4Bku"},
    {"name": "Charlotte (Previously Giovanni)", "id": "XB0fDUnXU5powFXDhCwa"}
]

# API endpoint for text-to-speech
BASE_URL = "https://api.elevenlabs.io/v1/text-to-speech"

# Set up the headers with your API key
headers = {
    "Accept": "audio/mpeg",
    "xi-api-key": XI_API_KEY,
    "Content-Type": "application/json"
}

# Text to convert to speech
data = {
    "text": "This is a test for our updated voice list in VoiceScribe Studio.",
    "model_id": "eleven_multilingual_v2",
    "voice_settings": {
        "stability": 0.5,
        "similarity_boost": 0.75
    }
}

print("Testing voice IDs from updated list...")

results = []

for voice in VOICES_TO_TEST:
    voice_name = voice["name"]
    voice_id = voice["id"]
    url = f"{BASE_URL}/{voice_id}"
    
    print(f"\nTesting voice: {voice_name} (ID: {voice_id})")
    print("Making API request...")
    
    try:
        # Make the POST request for speech synthesis
        response = requests.post(url, json=data, headers=headers)
        
        # Check if the request was successful
        if response.status_code == 200:
            print(f"✅ SUCCESS: Voice {voice_name} works!")
            
            # Save the audio to a file for testing
            output_file = f"test_voice_{voice_id}.mp3"
            with open(output_file, "wb") as f:
                f.write(response.content)
            
            print(f"Audio saved to {output_file}")
            results.append({"voice": voice_name, "status": "Success", "file": output_file})
        else:
            print(f"❌ FAILED: Voice {voice_name}")
            print(f"Error: {response.status_code}")
            print(response.text)
            results.append({"voice": voice_name, "status": "Failed", "error": response.text})
        
        # Add a delay to avoid rate limiting
        time.sleep(1)
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        results.append({"voice": voice_name, "status": "Error", "error": str(e)})
        
# Print summary of results
print("\n=== TEST SUMMARY ===")
print("=" * 80)
for result in results:
    status = "✅ " if result["status"] == "Success" else "❌ "
    print(f"{status}{result['voice']}")
print("=" * 80) 