from dotenv import load_dotenv
import os
from elevenlabs.client import ElevenLabs
import time

# Load the API key from .env file
load_dotenv()
api_key = os.getenv("ELEVENLABS_API_KEY")

print(f"Testing ElevenLabs API with key: {api_key}")

# Initialize the client
client = ElevenLabs(api_key=api_key)

# Test getting voices
try:
    print("\nFetching voices...")
    response = client.voices.get_all()
    print(f"Response type: {type(response)}")
    
    # Try to access voices in different ways
    if hasattr(response, "voices"):
        print(f"Found {len(response.voices)} voices")
        if len(response.voices) > 0:
            print(f"First voice: {response.voices[0].name} (ID: {response.voices[0].voice_id})")
    else:
        print("No 'voices' attribute found on response")
        print(f"Response object has these attributes: {dir(response)}")
        
    # Try to list all voices
    voice_list = []
    if hasattr(response, "voices"):
        for voice in response.voices:
            print(f"Voice: {voice.name} (ID: {voice.voice_id})")
    
    print("\nAPI test successful!")
    
except Exception as e:
    print(f"Error testing ElevenLabs API: {str(e)}")
    
# Test voice synthesis with a known good voice ID if possible
try:
    # A short test phrase
    test_text = "This is a test of the ElevenLabs API. If you can hear this, the API is working."
    
    # Try with a default voice from ElevenLabs
    test_voice_id = "21m00Tcm4TlvDq8ikWAM"  # Rachel - a common default voice
    
    print(f"\nTesting text-to-speech with voice ID: {test_voice_id}...")
    audio = client.text_to_speech.convert(
        text=test_text,
        voice_id=test_voice_id,
        model_id="eleven_multilingual_v2",
        output_format="wav"
    )
    
    # Handle the response based on its type
    if isinstance(audio, bytes):
        # Direct bytes response
        print(f"Received direct bytes response: {len(audio)} bytes")
        audio_data = audio
    elif hasattr(audio, '__iter__') or hasattr(audio, '__next__'):
        # It's a generator or iterator, collect all chunks
        print("Received generator response, collecting chunks...")
        audio_chunks = bytearray()
        for chunk in audio:
            if isinstance(chunk, bytes):
                audio_chunks.extend(chunk)
            else:
                print(f"Warning: Non-bytes chunk received: {type(chunk)}")
        audio_data = bytes(audio_chunks)
        print(f"Collected {len(audio_data)} bytes of audio data")
    else:
        # Unexpected type
        print(f"Unexpected response type: {type(audio)}")
        audio_data = None
    
    # Save the audio file if we got data
    if audio_data:
        timestamp = int(time.time())
        output_file = f"test_audio_{timestamp}.wav"
        
        with open(output_file, "wb") as f:
            f.write(audio_data)
        print(f"Saved test audio to: {output_file}")
        print("TTS test successful!")
    else:
        print("Failed to generate audio data")
    
except Exception as e:
    print(f"Error testing TTS: {str(e)}")
    import traceback
    traceback.print_exc() 