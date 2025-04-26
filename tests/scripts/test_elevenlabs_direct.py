import os
import time
import json
import requests
from dotenv import load_dotenv

# Load API key from .env file
load_dotenv()
api_key = os.getenv("ELEVENLABS_API_KEY")

print(f"Testing ElevenLabs API with key: {api_key}")
print(f"Key length: {len(api_key) if api_key else 0}")

# Direct API calls without using the library for diagnostic purposes
ELEVENLABS_API_URL = "https://api.elevenlabs.io/v1"

# Test 1: Check user subscription info
def test_user_info():
    print("\n===== TEST 1: Checking User Info =====")
    headers = {
        "Accept": "application/json",
        "xi-api-key": api_key
    }
    
    try:
        response = requests.get(f"{ELEVENLABS_API_URL}/user", headers=headers)
        response.raise_for_status()
        user_info = response.json()
        print(f"SUCCESS: Got user info. Status code: {response.status_code}")
        print(f"Subscription: {user_info.get('subscription', {}).get('tier', 'Unknown')}")
        print(f"Character limit: {user_info.get('subscription', {}).get('character_limit', 'Unknown')}")
        print(f"Character count: {user_info.get('subscription', {}).get('character_count', 'Unknown')}")
        return True
    except requests.exceptions.HTTPError as e:
        print(f"ERROR: HTTP Error: {e}")
        print(f"Status code: {e.response.status_code}")
        print(f"Response: {e.response.text}")
        return False
    except Exception as e:
        print(f"ERROR: Other error: {str(e)}")
        return False

# Test 2: List available voices
def test_list_voices():
    print("\n===== TEST 2: Listing Available Voices =====")
    headers = {
        "Accept": "application/json",
        "xi-api-key": api_key
    }
    
    try:
        response = requests.get(f"{ELEVENLABS_API_URL}/voices", headers=headers)
        response.raise_for_status()
        voices = response.json()
        print(f"SUCCESS: Listed voices. Status code: {response.status_code}")
        print(f"Found {len(voices.get('voices', []))} voices")
        
        # Print first few voices for verification
        for i, voice in enumerate(voices.get('voices', [])[:3]):
            print(f"Voice {i+1}: {voice.get('name')} (ID: {voice.get('voice_id')})")
        
        return True, voices.get('voices', [])
    except requests.exceptions.HTTPError as e:
        print(f"ERROR: HTTP Error: {e}")
        print(f"Status code: {e.response.status_code}")
        print(f"Response: {e.response.text}")
        return False, []
    except Exception as e:
        print(f"ERROR: Other error: {str(e)}")
        return False, []

# Test 3: Get a specific voice
def test_get_voice(voice_id="21m00Tcm4TlvDq8ikWAM"):  # Default to Rachel voice
    print(f"\n===== TEST 3: Getting Voice Details (ID: {voice_id}) =====")
    headers = {
        "Accept": "application/json",
        "xi-api-key": api_key
    }
    
    try:
        response = requests.get(f"{ELEVENLABS_API_URL}/voices/{voice_id}", headers=headers)
        response.raise_for_status()
        voice = response.json()
        print(f"SUCCESS: Got voice details. Status code: {response.status_code}")
        print(f"Voice name: {voice.get('name')}")
        print(f"Voice ID: {voice.get('voice_id')}")
        return True
    except requests.exceptions.HTTPError as e:
        print(f"ERROR: HTTP Error: {e}")
        print(f"Status code: {e.response.status_code}")
        print(f"Response: {e.response.text}")
        return False
    except Exception as e:
        print(f"ERROR: Other error: {str(e)}")
        return False

# Test 4: Generate a TTS audio
def test_tts(voice_id="21m00Tcm4TlvDq8ikWAM", model_id="eleven_multilingual_v2"):
    print(f"\n===== TEST 4: Generating TTS (Voice ID: {voice_id}) =====")
    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": api_key
    }
    
    data = {
        "text": "This is a test of the ElevenLabs Text-to-Speech API.",
        "model_id": model_id,
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.5
        }
    }
    
    try:
        response = requests.post(
            f"{ELEVENLABS_API_URL}/text-to-speech/{voice_id}",
            json=data,
            headers=headers
        )
        response.raise_for_status()
        
        # Save the audio file
        timestamp = int(time.time())
        filename = f"test_tts_{timestamp}.mp3"
        with open(filename, "wb") as f:
            f.write(response.content)
            
        print(f"SUCCESS: Generated TTS. Status code: {response.status_code}")
        print(f"Audio saved to: {filename}")
        print(f"Audio size: {len(response.content)} bytes")
        return True
    except requests.exceptions.HTTPError as e:
        print(f"ERROR: HTTP Error: {e}")
        print(f"Status code: {e.response.status_code}")
        print(f"Response: {e.response.text}")
        return False
    except Exception as e:
        print(f"ERROR: Other error: {str(e)}")
        return False

# Test 5: Get available models
def test_get_models():
    print("\n===== TEST 5: Checking Available Models =====")
    headers = {
        "Accept": "application/json",
        "xi-api-key": api_key
    }
    
    try:
        response = requests.get(f"{ELEVENLABS_API_URL}/models", headers=headers)
        response.raise_for_status()
        models = response.json()
        print(f"SUCCESS: Listed models. Status code: {response.status_code}")
        
        # Print available models
        for model in models:
            print(f"Model: {model.get('name')} (ID: {model.get('model_id')})")
            
        return True, models
    except requests.exceptions.HTTPError as e:
        print(f"ERROR: HTTP Error: {e}")
        print(f"Status code: {e.response.status_code}")
        print(f"Response: {e.response.text}")
        return False, []
    except Exception as e:
        print(f"ERROR: Other error: {str(e)}")
        return False, []

# Run all tests
print("\nRunning comprehensive ElevenLabs API tests...")

# First, check if the key seems valid (not empty, right format)
if not api_key or len(api_key) < 10:
    print("ERROR: API key appears to be missing or invalid (too short)")
else:
    # Check format
    if not api_key.startswith(""):
        print("INFO: API key doesn't start with a common prefix (could be fine)")

    # Run the tests
    user_success = test_user_info()
    
    if user_success:
        voices_success, voices = test_list_voices()
        
        if voices_success and voices:
            # Get the first voice ID for testing
            first_voice_id = voices[0]["voice_id"] if voices else "21m00Tcm4TlvDq8ikWAM"
            test_get_voice(first_voice_id)
            test_tts(first_voice_id)
        
        models_success, _ = test_get_models()
    
    print("\n===== SUMMARY =====")
    print("If all tests show SUCCESS, your API key works correctly.")
    print("If any tests fail, there may be an issue with your key or account.")
    print("Check the error messages for more details.") 