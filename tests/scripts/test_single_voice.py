#!/usr/bin/env python3
"""
Test a single voice ID to see if it works even though it's not listed in the API
"""

import os
import requests
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get API key from environment variables or enter it directly
XI_API_KEY = os.getenv("ELEVENLABS_API_KEY", "")
if not XI_API_KEY:
    XI_API_KEY = input("Enter your ElevenLabs API Key: ")

# Test a "missing" voice ID from our app
# Dorothy - Mature & Warm
VOICE_ID = "ThT5KcBeYPX3keUQqHPh"

# API endpoint for text-to-speech
url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}"

# Set up the headers with your API key
headers = {
    "Accept": "audio/mpeg",
    "xi-api-key": XI_API_KEY,
    "Content-Type": "application/json"
}

# Text to convert to speech
data = {
    "text": "This is a test to see if this voice ID still works even though it's not listed in the API.",
    "model_id": "eleven_multilingual_v2",
    "voice_settings": {
        "stability": 0.5,
        "similarity_boost": 0.75
    }
}

print(f"Testing voice ID: {VOICE_ID}")
print("Making API request...")

try:
    # Make the POST request for speech synthesis
    response = requests.post(url, json=data, headers=headers)
    
    # Check if the request was successful
    if response.status_code == 200:
        print(f"Success! Voice ID {VOICE_ID} still works.")
        
        # Save the audio to a file for testing
        output_file = f"test_voice_{VOICE_ID}.mp3"
        with open(output_file, "wb") as f:
            f.write(response.content)
        
        print(f"Audio saved to {output_file}")
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        
except Exception as e:
    print(f"Error: {e}") 