"""
Text-to-Speech Client Module

This module integrates various TTS functionalities, serving as a central point for voice generation features.
"""

from .elevenlabs_client import (
    generate_voiceover,
    get_voices,
    load_all_voices,
    convert_mp3_to_ogg,
    convert_to_wav,
    convert_wav_to_format,
    convert_to_high_quality_wav
)

from .humanize_script import humanize_script

# Re-export the consolidated load_all_voices function
load_voices = load_all_voices  # Alias for backward compatibility

# Re-export generate_audio function with a more consistent interface
def generate_audio(script, voice_id, output_path=None, stability=0.5, similarity=0.75, style=0.0, speed=1.0, use_speaker_boost=False, output_format="mp3_44100_128"):
    """
    Generate audio from a script using the Eleven Labs API
    
    Args:
        script (str): The script to convert to speech
        voice_id (str): The ID of the voice to use
        output_path (str, optional): Where to save the audio file
        stability (float): Voice stability (0.0 to 1.0)
        similarity (float): Voice similarity (0.0 to 1.0)
        style (float): Style exaggeration (0.0 to 1.0)
        speed (float): Speaking speed (0.7 to 1.2)
        use_speaker_boost (bool): Whether to apply speaker boost
        output_format (str): The desired output format
        
    Returns:
        tuple: (audio_bytes, file_path, is_premium_format)
    """
    return generate_voiceover(
        script=script,
        voice_id=voice_id,
        output_path=output_path,
        stability=stability,
        similarity=similarity,
        style=style,
        speed=speed,
        use_speaker_boost=use_speaker_boost,
        output_format=output_format
    )

# Re-export humanize_audio function that applies humanize_script to text before TTS
def humanize_audio(script, voice_id, output_path=None, stability=0.5, similarity=0.75, style=0.0, speed=1.0, use_speaker_boost=False, output_format="mp3_44100_128"):
    """
    Humanize a script and then generate audio using the Eleven Labs API
    
    Args:
        script (str): The script to humanize and convert to speech
        voice_id (str): The ID of the voice to use
        output_path (str, optional): Where to save the audio file
        stability (float): Voice stability (0.0 to 1.0)
        similarity (float): Voice similarity (0.0 to 1.0)
        style (float): Style exaggeration (0.0 to 1.0)
        speed (float): Speaking speed (0.7 to 1.2)
        use_speaker_boost (bool): Whether to apply speaker boost
        output_format (str): The desired output format
        
    Returns:
        tuple: (audio_bytes, file_path, is_premium_format, humanized_script)
    """
    # First, humanize the script
    humanized_result = humanize_script(script)
    humanized_script = humanized_result.get("content", script)
    
    # If humanization failed, use the original script
    if "error" in humanized_result:
        print(f"Warning: Humanization error: {humanized_result.get('error')}")
        print("Using original script instead")
        humanized_script = script
    
    # Generate audio with the humanized script
    audio_bytes, file_path, is_premium_format = generate_audio(
        script=humanized_script,
        voice_id=voice_id,
        output_path=output_path,
        stability=stability,
        similarity=similarity,
        style=style,
        speed=speed,
        use_speaker_boost=use_speaker_boost,
        output_format=output_format
    )
    
    # Return the audio data along with the humanized script
    return audio_bytes, file_path, is_premium_format, humanized_script 