import os
import io
import time
from elevenlabs import save
from elevenlabs.client import ElevenLabs
from pydub import AudioSegment
from ..config import ELEVENLABS_API_KEY, VOICE_ID

# Initialize the ElevenLabs client
if ELEVENLABS_API_KEY:
    client = ElevenLabs(api_key=ELEVENLABS_API_KEY)
else:
    client = None
    print("Warning: ELEVENLABS_API_KEY not found. ElevenLabs functionality disabled.")

def list_available_voices():
    """
    Get a list of available voices from ElevenLabs.
    
    Returns:
        list: List of voice objects with name and ID
    """
    if not client:
        print("ElevenLabs client not initialized. Returning default voices.")
        # Return default voices as fallback if client isn't initialized
        return [
            {"name": "Male Voice 1", "id": "pNInz6obpgDQGcFmaJgB"},  # Adam
            {"name": "Male Voice 2", "id": "ErXwobaYiN019PkySvjV"},  # Antoni
            {"name": "Female Voice 1", "id": "EXAVITQu4vr4xnSDxMaL"},  # Bella
            {"name": "Female Voice 2", "id": "21m00Tcm4TlvDq8ikWAM"},  # Rachel
        ]
        
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
        # Return default voices as fallback on error
        return [
            {"name": "Male Voice 1", "id": "pNInz6obpgDQGcFmaJgB"},
            {"name": "Male Voice 2", "id": "ErXwobaYiN019PkySvjV"},
            {"name": "Female Voice 1", "id": "EXAVITQu4vr4xnSDxMaL"},
            {"name": "Female Voice 2", "id": "21m00Tcm4TlvDq8ikWAM"},
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
                       stability=0.5, similarity=0.75, style=0.0, speed=1.0, use_speaker_boost=False,
                       output_format="mp3_44100_128"):
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
        output_format (str): The desired output format from the API
                            - "mp3_44100_128": MP3 format, 44.1kHz, 128kbps (standard)
                            - "mp3_44100_192": MP3 format, 44.1kHz, 192kbps (higher quality)
                            - "pcm_44100": WAV format, 44.1kHz, 16-bit (broadcast quality)
    
    Returns:
        tuple: (audio_bytes, file_path, is_premium_format) if successful, (None, None, False) if failed
              The is_premium_format flag indicates if the requested format requires a premium subscription
    """
    if not client:
        print("ElevenLabs client not initialized. Skipping voiceover generation.")
        return None, None, False
        
    try:
        # Calculate character count for tracking
        character_count = len(script)
        print(f"Submitting {character_count} characters to ElevenLabs TTS.")
        
        # Validate speed parameter to ensure it's within allowed range
        speed = max(0.7, min(1.2, speed))
        
        print(f"Generating voiceover with voice ID: {voice_id}, model: {model}")
        print(f"Voice settings - Stability: {stability}, Similarity: {similarity}, Style: {style}, Speed: {speed}, Speaker Boost: {use_speaker_boost}")
        print(f"Requested output format: {output_format}")
        
        # Configure voice settings
        voice_settings = {
            "stability": stability,
            "similarity_boost": similarity,
            "style": style,
            "use_speaker_boost": use_speaker_boost,
            "speed": speed
        }
        
        # Variable to track premium format usage
        is_premium_format = False
        original_format = output_format
        
        # Check if the requested format is a premium format (WAV/PCM or high bitrate MP3)
        if output_format in ["pcm_44100", "mp3_44100_192"]:
            is_premium_format = True
            try:
                # Generate audio from script with premium format
                audio_response = client.text_to_speech.convert(
                    text=script,
                    voice_id=voice_id,
                    model_id=model,
                    output_format=output_format,
                    voice_settings=voice_settings
                )
            except Exception as premium_error:
                print(f"Error using premium format {output_format}: {str(premium_error)}")
                print("Falling back to standard MP3 format")
                output_format = "mp3_44100_128"
                audio_response = client.text_to_speech.convert(
                    text=script,
                    voice_id=voice_id,
                    model_id=model,
                    output_format=output_format,
                    voice_settings=voice_settings
                )
        else:
            # Generate audio from script with standard format
            audio_response = client.text_to_speech.convert(
                text=script,
                voice_id=voice_id,
                model_id=model,
                output_format=output_format,
                voice_settings=voice_settings
            )
        
        # Handle the response based on its type
        if isinstance(audio_response, bytes):
            audio = audio_response
        elif hasattr(audio_response, '__iter__') or hasattr(audio_response, '__next__'):
            print("Received generator response, collecting chunks...")
            audio_chunks = bytearray()
            for chunk in audio_response:
                if isinstance(chunk, bytes):
                    audio_chunks.extend(chunk)
                else:
                    print(f"Warning: Non-bytes chunk received: {type(chunk)}")
            audio = bytes(audio_chunks)
        else:
            print(f"Unexpected response type: {type(audio_response)}")
            return None, None, False
        
        print(f"Successfully generated audio: {len(audio)} bytes")
        # --- Character Count Logging --- 
        print(f"Character Usage (ElevenLabs): Submitted={character_count}")
        # TODO: Store character_count here later
        # --- End Character Count Logging ---
            
        # If output path is provided, save the audio file
        if output_path:
            timestamp = int(time.time())
            if not os.path.exists(os.path.dirname(output_path)):
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            filename, ext = os.path.splitext(output_path)
            
            # Determine the correct extension based on actual format received
            if output_format.startswith("pcm_"):
                ext = ".wav"
            elif output_format.startswith("mp3_"):
                ext = ".mp3"
            else:
                ext = ext or ".mp3"  # Default to mp3 if extension is empty
                
            file_path = f"{filename}_{timestamp}{ext}"
            
            with open(file_path, "wb") as f:
                f.write(audio)
            
            print(f"Saved audio to: {file_path}")
            
            # Check if we need to convert back to the originally requested format
            if original_format != output_format and original_format.startswith("pcm_"):
                # User wanted WAV but we could only get MP3 - convert as best we can
                try:
                    wav_path = file_path.replace(".mp3", ".wav")
                    convert_to_wav(file_path, wav_path)
                    file_path = wav_path
                    print(f"Converted MP3 to WAV as fallback: {file_path}")
                except Exception as conv_err:
                    print(f"Error during fallback conversion: {str(conv_err)}")
            
            return audio, file_path, is_premium_format
        
        return audio, None, is_premium_format
    
    except Exception as e:
        print(f"Error generating voiceover: {str(e)}")
        import traceback
        traceback.print_exc()
        return None, None, False

def convert_mp3_to_ogg(mp3_data_or_path, output_path=None, quality="high"):
    """
    Convert MP3 audio to OGG format for better compatibility.
    
    Args:
        mp3_data_or_path: Either bytes data or file path of the MP3 audio
        output_path (str, optional): Where to save the OGG file
        quality (str): Quality level - "low", "medium", or "high"
    
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
        
        # Set bitrate based on quality
        if quality == "low":
            bitrate = "128k"
        elif quality == "medium":
            bitrate = "192k"
        else:  # high
            bitrate = "256k"
            
        # If output path is provided, export the OGG file
        if output_path:
            # Make sure the directory exists
            if not os.path.exists(os.path.dirname(output_path)):
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Export as OGG with quality based on parameter
            audio.export(output_path, format="ogg", codec="libvorbis", bitrate=bitrate)
            return audio, output_path
        
        return audio, None
    
    except Exception as e:
        print(f"Error converting MP3 to OGG: {str(e)}")
        return None, None

def convert_to_wav(input_path, output_path, sample_rate=44100, bit_depth=16):
    """
    Convert any audio file to WAV format with specified quality settings.
    
    Args:
        input_path (str): Path to the input audio file
        output_path (str): Path to save the WAV file
        sample_rate (int): The sample rate for the WAV file (default: 44100 Hz)
        bit_depth (int): Bit depth for the WAV file (default: 16 bit)
    
    Returns:
        str: Path to the output WAV file if successful, None if failed
    """
    try:
        # Load the audio
        audio = AudioSegment.from_file(input_path)
        
        # Set the desired sample rate if needed
        if audio.frame_rate != sample_rate:
            audio = audio.set_frame_rate(sample_rate)
        
        # Set the desired bit depth if needed
        if audio.sample_width != bit_depth // 8:
            audio = audio.set_sample_width(bit_depth // 8)
        
        # Export as WAV (PCM format)
        audio.export(output_path, format="wav")
        
        print(f"Converted audio to WAV: {output_path}")
        return output_path
    
    except Exception as e:
        print(f"Error converting to WAV: {str(e)}")
        return None

def convert_wav_to_format(wav_path, output_path, format_type="mp3", quality="high"):
    """
    Convert WAV to another format with high quality.
    
    Args:
        wav_path (str): Path to the WAV file
        output_path (str): Path to save the output file
        format_type (str): Output format - "mp3", "ogg"
        quality (str): Quality level - "low", "medium", or "high"
    
    Returns:
        str: Path to the output file if successful, None if failed
    """
    try:
        # Load the WAV file
        audio = AudioSegment.from_file(wav_path, format="wav")
        
        # Define quality parameters for each format
        quality_settings = {
            "mp3": {
                "low": {"bitrate": "128k"},
                "medium": {"bitrate": "192k"},
                "high": {"bitrate": "320k"}
            },
            "ogg": {
                "low": {"bitrate": "128k"},
                "medium": {"bitrate": "192k"},
                "high": {"bitrate": "256k"}
            }
        }
        
        # Get quality settings for the requested format
        format_settings = quality_settings.get(format_type, {})
        settings = format_settings.get(quality, format_settings.get("high", {}))
        
        # Export to the desired format
        audio.export(output_path, format=format_type, **settings)
        
        print(f"Converted WAV to {format_type}: {output_path}")
        return output_path
    
    except Exception as e:
        print(f"Error converting WAV to {format_type}: {str(e)}")
        return None

# Keep the old function for backward compatibility
def convert_wav_to_ogg(wav_data_or_path, output_path=None):
    """Legacy function - redirects to convert_mp3_to_ogg"""
    print("Warning: convert_wav_to_ogg is deprecated, use convert_mp3_to_ogg instead")
    return convert_mp3_to_ogg(wav_data_or_path, output_path) 