import re
import logging
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def extract_video_id(youtube_url):
    """
    Extract YouTube video ID from various URL formats.
    
    Args:
        youtube_url (str): YouTube video URL
        
    Returns:
        str: YouTube video ID or None if not found
    """
    if not youtube_url:
        return None
        
    # YouTube URL patterns
    patterns = [
        r'(?:https?:\/\/)?(?:www\.)?youtube\.com\/watch\?v=([^&\s]+)',  # Standard watch URL
        r'(?:https?:\/\/)?(?:www\.)?youtube\.com\/embed\/([^\?\s]+)',   # Embed URL
        r'(?:https?:\/\/)?(?:www\.)?youtu\.be\/([^\?\s]+)',            # Shortened URL
        r'(?:https?:\/\/)?(?:www\.)?youtube\.com\/shorts\/([^\?\s]+)'  # YouTube Shorts
    ]
    
    for pattern in patterns:
        match = re.search(pattern, youtube_url)
        if match:
            return match.group(1)
    
    logger.warning(f"Could not extract video ID from URL: {youtube_url}")
    return None

def get_video_info(video_id):
    """
    Get basic video information using the transcript API.
    This is a limited implementation - in a production app, you might use the YouTube Data API.
    
    Args:
        video_id (str): YouTube video ID
        
    Returns:
        dict: Video information (currently just ID and URL)
    """
    return {
        'id': video_id,
        'url': f"https://www.youtube.com/watch?v={video_id}"
    }

def get_transcript(video_id, language_codes=['en']):
    """
    Get transcript for a YouTube video.
    
    Args:
        video_id (str): YouTube video ID
        language_codes (list): List of language codes to try, in order of preference
        
    Returns:
        dict: A dictionary containing:
            - success (bool): Whether transcript retrieval was successful
            - transcript (str): The transcript text if successful
            - error (str): Error message if not successful
    """
    result = {
        'success': False,
        'transcript': '',
        'error': None
    }
    
    if not video_id:
        result['error'] = "No YouTube video ID provided"
        return result
    
    try:
        # Try to get transcript in preferred languages
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        
        # First try manual transcripts in preferred languages
        transcript = None
        for lang_code in language_codes:
            try:
                # Try to find a manually created transcript
                for t in transcript_list:
                    if t.language_code == lang_code and not t.is_generated:
                        transcript = t
                        break
                
                # If found, break the loop
                if transcript:
                    break
            except Exception:
                continue
        
        # If no manual transcript, try auto-generated ones
        if not transcript:
            for lang_code in language_codes:
                try:
                    for t in transcript_list:
                        if t.language_code == lang_code:
                            transcript = t
                            break
                    
                    if transcript:
                        break
                except Exception:
                    continue
        
        # If still no transcript, try getting any available transcript
        if not transcript and len(transcript_list._transcripts) > 0:
            # Get the first available transcript
            transcript_lang = list(transcript_list._transcripts.keys())[0]
            transcript = transcript_list._transcripts[transcript_lang]
        
        # If we found a transcript, fetch it
        if transcript:
            transcript_data = transcript.fetch()
            
            # Format transcript into a readable text
            formatted_transcript = ""
            for entry in transcript_data:
                text = entry.get('text', '')
                # Clean up newlines and HTML artifacts
                text = re.sub(r'<[^>]+>', '', text)  # Remove HTML tags
                text = text.replace('\n', ' ').strip()
                formatted_transcript += text + " "
            
            result['transcript'] = formatted_transcript.strip()
            result['success'] = True
        else:
            result['error'] = "No transcripts found for this video"
        
    except TranscriptsDisabled:
        result['error'] = "Transcripts are disabled for this video"
    except NoTranscriptFound:
        result['error'] = "No transcript found for this video"
    except Exception as e:
        logger.error(f"Error getting transcript: {str(e)}")
        result['error'] = f"Error extracting transcript: {str(e)}"
    
    return result

def format_youtube_transcript_for_llm(video_id, transcript_data):
    """
    Format the extracted YouTube transcript for use with LLM.
    
    Args:
        video_id (str): The YouTube video ID
        transcript_data (dict): The dictionary returned by get_transcript
        
    Returns:
        str: Formatted transcript ready to use as context for an LLM
    """
    if not transcript_data['success']:
        return f"Error retrieving transcript for YouTube video: {transcript_data['error']}"
    
    video_url = f"https://www.youtube.com/watch?v={video_id}"
    
    formatted_content = f"YouTube Video: {video_url}\n\n"
    formatted_content += "Transcript:\n" + transcript_data['transcript']
    
    return formatted_content 