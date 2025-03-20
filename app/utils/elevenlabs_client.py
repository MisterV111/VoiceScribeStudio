import os
import io
import time
from elevenlabs import save
from elevenlabs.client import ElevenLabs
from pydub import AudioSegment
from ..config import ELEVENLABS_API_KEY, VOICE_ID

# Initialize the ElevenLabs client
client = ElevenLabs(api_key=ELEVENLABS_API_KEY)

def list_available_voices():
    """
    Get a list of available voices from ElevenLabs.
    
    Returns:
        list: List of voice objects with name and ID
    """
    try:
        all_voices = client.voices.get_all()
        
        # Debug information
        print(f"Voice response type: {type(all_voices)}")
        
        # Handle response based on its structure
        voice_list = []
        
        if hasattr(all_voices, "voices"):
            # New API format
            for voice in all_voices.voices:
                voice_list.append({"name": voice.name, "id": voice.voice_id})
        elif isinstance(all_voices, list):
            # Older API format - list of voice objects
            for voice in all_voices:
                if hasattr(voice, "name") and hasattr(voice, "voice_id"):
                    voice_list.append({"name": voice.name, "id": voice.voice_id})
                elif isinstance(voice, dict) and "name" in voice and "voice_id" in voice:
                    voice_list.append({"name": voice["name"], "id": voice["voice_id"]})
        
        print(f"Successfully retrieved {len(voice_list)} voices")
        return voice_list
    except Exception as e:
        print(f"Error fetching voices: {str(e)}")
        # Return default voices as fallback
        return [
            {"name": "Male Voice 1", "id": "pNInz6obpgDQGcFmaJgB"},  # Adam
            {"name": "Male Voice 2", "id": "ErXwobaYiN019PkySvjV"},  # Antoni
            {"name": "Female Voice 1", "id": "EXAVITQu4vr4xnSDxMaL"},  # Bella
            {"name": "Female Voice 2", "id": "21m00Tcm4TlvDq8ikWAM"},  # Rachel
        ]

def get_voices():
    """
    Get voices from ElevenLabs API in a simplified format for the main application.
    
    Returns:
        list: List of voice dictionaries with name and voice_id
    """
    try:
        voice_list = list_available_voices()
        # Convert to the format expected by the application
        return [
            {"name": voice["name"], "voice_id": voice["id"]} 
            for voice in voice_list
        ]
    except Exception as e:
        print(f"Error in get_voices: {str(e)}")
        return []

def generate_voiceover(script, voice_id=VOICE_ID, output_path=None, model="eleven_multilingual_v2", 
                       stability=0.5, similarity=0.75, style=0.0, speed=1.0, use_speaker_boost=False):
    """
    Generate a voiceover using ElevenLabs API.
    
    Args:
        script (str): The script to convert to speech
        voice_id (str): The ID of the voice to use
        output_path (str, optional): Where to save the audio file
        model (str): The TTS model to use
        stability (float): Voice stability (0.0 to 1.0)
        similarity (float): Voice similarity (0.0 to 1.0)
        style (float): Style exaggeration (0.0 to 1.0)
        speed (float): Speaking speed (0.7 to 1.2)
        use_speaker_boost (bool): Whether to apply speaker boost
    
    Returns:
        tuple: (audio_bytes, file_path) if successful, (None, None) if failed
    """
    try:
        # Validate speed parameter to ensure it's within allowed range
        speed = max(0.7, min(1.2, speed))
        
        print(f"Generating voiceover with voice ID: {voice_id}, model: {model}")
        print(f"Voice settings - Stability: {stability}, Similarity: {similarity}, Style: {style}, Speed: {speed}, Speaker Boost: {use_speaker_boost}")
        
        # Configure voice settings
        voice_settings = {
            "stability": stability,
            "similarity_boost": similarity,
            "style": style,
            "use_speaker_boost": use_speaker_boost,
            "speed": speed
        }
        
        # Generate audio from script
        audio_response = client.text_to_speech.convert(
            text=script,
            voice_id=voice_id,
            model_id=model,
            output_format="mp3_44100_128",
            voice_settings=voice_settings
        )
        
        # Handle the response based on its type
        if isinstance(audio_response, bytes):
            # Direct bytes response
            audio = audio_response
        elif hasattr(audio_response, '__iter__') or hasattr(audio_response, '__next__'):
            # It's a generator or iterator, collect all chunks
            print("Received generator response, collecting chunks...")
            audio_chunks = bytearray()
            for chunk in audio_response:
                if isinstance(chunk, bytes):
                    audio_chunks.extend(chunk)
                else:
                    print(f"Warning: Non-bytes chunk received: {type(chunk)}")
            audio = bytes(audio_chunks)
        else:
            # Unexpected type
            print(f"Unexpected response type: {type(audio_response)}")
            return None, None
        
        print(f"Successfully generated audio: {len(audio)} bytes")
        
        # If output path is provided, save the audio file
        if output_path:
            timestamp = int(time.time())
            if not os.path.exists(os.path.dirname(output_path)):
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Add timestamp to filename to prevent overwriting
            filename, ext = os.path.splitext(output_path)
            if not ext:  # If no extension provided
                ext = ".mp3"
            file_path = f"{filename}_{timestamp}{ext}"
            
            # Save the audio
            with open(file_path, "wb") as f:
                f.write(audio)
            
            print(f"Saved audio to: {file_path}")
            return audio, file_path
        
        return audio, None
    
    except Exception as e:
        print(f"Error generating voiceover: {str(e)}")
        import traceback
        traceback.print_exc()
        return None, None

def convert_mp3_to_ogg(mp3_data_or_path, output_path=None):
    """
    Convert MP3 audio to OGG format for better compatibility.
    
    Args:
        mp3_data_or_path: Either bytes data or file path of the MP3 audio
        output_path (str, optional): Where to save the OGG file
    
    Returns:
        tuple: (audio_segment, file_path) if successful, (None, None) if failed
    """
    try:
        # Load the audio data
        if isinstance(mp3_data_or_path, bytes):
            # Load from bytes
            audio = AudioSegment.from_file(io.BytesIO(mp3_data_or_path), format="mp3")
        elif isinstance(mp3_data_or_path, str) and os.path.exists(mp3_data_or_path):
            # Load from file
            audio = AudioSegment.from_file(mp3_data_or_path, format="mp3")
        else:
            raise ValueError("Invalid input: must be bytes data or existing file path")
        
        # If output path is provided, export the OGG file
        if output_path:
            # Make sure the directory exists
            if not os.path.exists(os.path.dirname(output_path)):
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Export as OGG with decent quality (quality scale: 0-10)
            audio.export(output_path, format="ogg", codec="libvorbis", bitrate="192k")
            return audio, output_path
        
        return audio, None
    
    except Exception as e:
        print(f"Error converting MP3 to OGG: {str(e)}")
        return None, None

# Keep the old function for backward compatibility
def convert_wav_to_ogg(wav_data_or_path, output_path=None):
    """Legacy function - redirects to convert_mp3_to_ogg"""
    print("Warning: convert_wav_to_ogg is deprecated, use convert_mp3_to_ogg instead")
    return convert_mp3_to_ogg(wav_data_or_path, output_path) 