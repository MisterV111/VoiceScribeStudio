#!/usr/bin/env python3
"""
Temporary script to fetch all available voices from ElevenLabs API
and compare with the voices in our app
"""

import os
import requests
import json
from dotenv import load_dotenv

# Load environment variables (to get API key)
load_dotenv()

# Voices in our app (from app/main.py)
APP_VOICES = {
    "Adam - Deep & Authoritative": "pFZP5JQG7iQjIQuC4Bku",
    "Antoni - Polish American Male": "ErXwobaYiN019PkySvjV",
    "Arnold - Crisp & Rough": "VR6AewLTigWG4xSOukaG",
    "Bella - Soft & Breathy": "EXAVITQu4vr4xnSDxMaL",
    "Callum - British Male": "N2lVS1w4EtoT3dr4eOWO",
    "Charlie - Casual American": "IKne3meq5aSn9XLyUdCD",
    "Clyde - Friendly & Engaging": "2EiwWnXFnvU5JabPnv8n",
    "Dan Teacher - Hybrid": "jn5Dym9tbXQdxJRlyYzZ",
    "Dan Teacher - Neutral": "CMtJJeUfoLE6mZYBmsFl",
    "Dan Teacher - Upbeat": "W14NZHmEOKlltX7Dhrac",
    "Daniel - British Male": "GBv7mTt0atIp3Br8iCZE",
    "Dorothy - Mature & Warm": "ThT5KcBeYPX3keUQqHPh",
    "Emily - Professional & Helpful": "LcfcDJNUP1GQjkzn1xUU",
    "Ethan - Young American": "g5CIjZEefAph4nQFvHAz",
    "Fin - Irish Male": "D38z5RcWu1voky8WS1ja",
    "Freya - Professional Female": "jsCqWAovK2LkecY7zXl4",
    "Giovanni - Italian Male": "XB0fDUnXU5powFXDhCwa",
    "Grace - Gentle & Soft": "oWAxZDx7w5VEj9dCyTzz",
    "Harry - British Teen": "SOYHLrjzK2X1ezoPC6cr",
    "Joseph - Deep & Resonant": "Zlb1dXrM653N07WRdFW3",
    "Josh - Gentle & Calm": "TxGEqnHWrfWFTfGW9XjX",
    "Liam - North American Male": "TX3LPaxmHKxFdv7VOQHJ",
    "Lily - British Received Pronunciation": "zrHiDhphv9ZnVXBqCLjz",
    "Lucy - American Teen": "ZQe5CZNOzWyzPSCn5a3c",
    "Matilda - British Teen": "MF3mGyEYCl7XYWbV9V6O",
    "Michael - British Male": "flq6f7yk4E4fJM5XTYuZ",
    "Nicole - Expressive & Emotional": "piTKgcLEGmPE4e6mEKli",
    "Oswald - Old American Male": "zcAOhNBS3c14rBihAFp1",
    "Rebecca - British Female": "t0jbNlBVZ17f02VDIeMI",
    "Sam - Raspy & Gritty": "yoZ06aMxZJJ28mfd3POQ",
    "Sarah - NPR Presenter": "pMsXgVXv3BLzUgSXRplE",
    "Serena - British Female": "onwK4e9ZLuTAKqWW03F9",
}

# Get API key from environment variables or enter it directly
XI_API_KEY = os.getenv("ELEVENLABS_API_KEY", "")
if not XI_API_KEY:
    XI_API_KEY = input("Enter your ElevenLabs API Key: ")

# API endpoint to get all voices
url = "https://api.elevenlabs.io/v1/voices?with_premade=true"

# Set up the headers with your API key
headers = {
    "Accept": "application/json",
    "xi-api-key": XI_API_KEY,
    "Content-Type": "application/json"
}

print("Fetching voices from ElevenLabs API...")

try:
    # Make the GET request
    response = requests.get(url, headers=headers)
    
    # Check if the request was successful
    if response.status_code == 200:
        # Parse the JSON response
        data = response.json()
        
        # Check subscription information
        subscription_url = "https://api.elevenlabs.io/v1/user/subscription"
        subscription_response = requests.get(subscription_url, headers=headers)
        if subscription_response.status_code == 200:
            subscription_data = subscription_response.json()
            print("\n== ACCOUNT INFORMATION ==")
            print(f"Tier: {subscription_data.get('tier', 'Unknown')}")
            print(f"Full subscription data: {json.dumps(subscription_data, indent=2)}")
            print("=" * 80)
        
        # Create a dictionary of voices from API
        api_voices = {voice['name']: voice['voice_id'] for voice in data['voices']}
        
        # Print total number of voices
        print(f"\nFound {len(data['voices'])} voices in API")
        print(f"Found {len(APP_VOICES)} voices in our app")
        
        print("\n== AVAILABLE VOICES FROM API ==")
        print("=" * 80)
        print(f"{'VOICE NAME':<40} {'VOICE ID':<40}")
        print("=" * 80)
        
        # Print all voice names and IDs in a formatted table
        for name, voice_id in api_voices.items():
            print(f"{name:<40} {voice_id:<40}")
            
        # Find voice IDs in our app that don't exist in the API
        missing_from_api = []
        for name, voice_id in APP_VOICES.items():
            if voice_id not in api_voices.values():
                missing_from_api.append((name, voice_id))
        
        # Find voice IDs in our app with different names in the API
        name_mismatches = []
        for app_name, app_id in APP_VOICES.items():
            for api_name, api_id in api_voices.items():
                if app_id == api_id and app_name != api_name:
                    name_mismatches.append((app_name, api_name, app_id))
        
        # Print voices in our app that don't exist in the API
        if missing_from_api:
            print("\n== VOICES IN APP MISSING FROM API ==")
            print("=" * 80)
            print(f"{'APP VOICE NAME':<40} {'VOICE ID':<40}")
            print("=" * 80)
            for name, voice_id in missing_from_api:
                print(f"{name:<40} {voice_id:<40}")
        
        # Print name mismatches
        if name_mismatches:
            print("\n== NAME MISMATCHES BETWEEN APP AND API ==")
            print("=" * 80)
            print(f"{'APP NAME':<40} {'API NAME':<40} {'VOICE ID':<40}")
            print("=" * 80)
            for app_name, api_name, voice_id in name_mismatches:
                print(f"{app_name:<40} {api_name:<40} {voice_id:<40}")
        
        # Save the voices data to a file for reference
        with open("elevenlabs_voices.json", "w") as f:
            json.dump(data, f, indent=2)
        print("\nVoice data also saved to 'elevenlabs_voices.json'")
        
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        
except Exception as e:
    print(f"Error: {e}")
