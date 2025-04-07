"""YouTube transcript extraction utilities."""

import re
import urllib.parse
import importlib.util

# Check if required packages are installed
def check_dependencies():
    """Check if required dependencies are installed."""
    if importlib.util.find_spec("youtube_transcript_api") is None:
        return False
    return True

try:
    from youtube_transcript_api import YouTubeTranscriptApi, NoTranscriptFound, TranscriptsDisabled, VideoUnavailable
    HAS_YOUTUBE_API = True
except ImportError:
    HAS_YOUTUBE_API = False
    print("Warning: youtube_transcript_api not installed. YouTube transcript extraction will be limited.")

def extract_video_id(url):
    """
    Extract the YouTube video ID from a URL.
    
    Args:
        url (str): YouTube URL
        
    Returns:
        str: Video ID or None if not found
    """
    if not url:
        return None
        
    # Try to parse the URL
    patterns = [
        r'(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([\w-]+)',
        r'youtube\.com\/watch.*?[?&]v=([\w-]+)',
        r'youtube\.com\/shorts\/([\w-]+)'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
            
    # Try to parse URL query parameters
    parsed_url = urllib.parse.urlparse(url)
    if 'youtube.com' in parsed_url.netloc:
        query_params = urllib.parse.parse_qs(parsed_url.query)
        if 'v' in query_params:
            return query_params['v'][0]
            
    return None

def extract_youtube_transcript(url, use_alt_methods=False):
    """
    Extract transcript from a YouTube video.
    
    Args:
        url (str): YouTube video URL
        use_alt_methods (bool): Whether to use alternative methods for transcript extraction
        
    Returns:
        tuple: (transcript_text, error) where transcript_text is the extracted transcript 
               and error is an error message if any
    """
    if not check_dependencies():
        return None, "YouTube transcript API not installed. Please install with: pip install youtube-transcript-api"
        
    if not url or not url.strip():
        return None, "No URL provided"
    
    try:
        print(f"Attempting to extract transcript from URL: {url}")
        
        # Extract video ID
        video_id = extract_video_id(url)
        
        if not video_id:
            return None, "Could not extract video ID from the provided URL. Please ensure it's a valid YouTube video URL."
        
        print(f"Extracted video ID: {video_id}")
            
        # Get available transcripts
        transcript = None
        transcript_text = None
        error_message = None
        transcript_list = None
        
        try:
            print(f"Getting transcript list for video ID: {video_id}")
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
            print(f"Successfully retrieved transcript list for {video_id}")
            
            if hasattr(transcript_list, '__iter__') or hasattr(transcript_list, '__next__'):
                # Check if we have any transcripts
                transcripts_available = list(transcript_list)
                if transcripts_available:
                    available_languages = [t.language_code for t in transcripts_available]
                    print(f"Available transcript languages: {', '.join(available_languages)}")
                else:
                    print("No transcripts available in the list.")
            
        except VideoUnavailable as e:
            print(f"VideoUnavailable error: {str(e)}")
            error_message = f"The video (ID: {video_id}) is unavailable. It might be private, deleted, age-restricted, or doesn't exist."
        except TranscriptsDisabled as e:
            print(f"TranscriptsDisabled error: {str(e)}")
            error_message = "Transcripts are disabled for this video. The creator may have turned them off."
        except NoTranscriptFound as e:
            print(f"NoTranscriptFound error: {str(e)}")
            error_message = "No transcripts were found for this video. It might not have any captions available."
        except Exception as e:
            print(f"Unexpected error accessing transcripts: {str(e)}, {type(e)}")
            error_message = f"Error accessing transcripts: {str(e)}"
        
        # If we have a transcript list, try to get a transcript
        if transcript_list:
            # Try to get English transcript first
            try:
                print("Trying to find English transcript...")
                # First try 'en'
                try:
                    transcript = transcript_list.find_transcript(['en'])
                    print("Found 'en' transcript")
                except Exception as e1:
                    print(f"No 'en' transcript found, trying en-US: {str(e1)}")
                    try:
                        # Then try 'en-US'
                        transcript = transcript_list.find_transcript(['en-US'])
                        print("Found 'en-US' transcript")
                    except Exception as e2:
                        print(f"No 'en-US' transcript found: {str(e2)}")
                        # If neither works, get first available transcript
                        try:
                            transcripts = list(transcript_list)
                            if transcripts:
                                # Get the first available transcript
                                transcript = transcripts[0]
                                print(f"Using first available transcript in {transcript.language_code}")
                                
                                # Try to translate to English if it's not already in English
                                if not transcript.language_code.startswith('en'):
                                    try:
                                        print(f"Translating transcript from {transcript.language_code} to English")
                                        transcript = transcript.translate('en')
                                        print("Translation successful")
                                    except Exception as trans_err:
                                        print(f"Translation failed: {str(trans_err)}, using original language")
                            else:
                                print("No transcripts available in the list")
                        except Exception as e3:
                            print(f"Error getting first available transcript: {str(e3)}")
            except Exception as e:
                print(f"Unexpected error finding transcript: {str(e)}")
                error_message = f"Failed to find any usable transcript: {str(e)}"
        
        # If we got a transcript, fetch the data
        if transcript:
            try:
                print(f"Fetching transcript data for language: {transcript.language_code}")
                transcript_data = transcript.fetch()
                print(f"Transcript data type: {type(transcript_data)}")
                
                # Just concatenate all text segments
                try:
                    # Check if transcript_data is a list of dictionaries with 'text' key
                    if isinstance(transcript_data, list) and all(isinstance(item, dict) and 'text' in item for item in transcript_data):
                        print("Processing list of dictionaries with 'text' key")
                        transcript_text = " ".join([item['text'] for item in transcript_data])
                    # Check if transcript_data has a __getitem__ method (subscriptable)
                    elif hasattr(transcript_data, '__getitem__'):
                        print("Processing subscriptable object")
                        # Try both item['text'] and item.text
                        try:
                            transcript_text = " ".join([item['text'] for item in transcript_data])
                        except (KeyError, TypeError):
                            try:
                                transcript_text = " ".join([item.text for item in transcript_data if hasattr(item, 'text')])
                            except (AttributeError, TypeError):
                                # If both fail, try a direct string conversion of each item
                                transcript_text = " ".join([str(item) for item in transcript_data])
                    # Handle other types of transcript objects
                    elif hasattr(transcript_data, 'fetch_transcripts'):
                        print("Processing object with fetch_transcripts method")
                        snippets = transcript_data.fetch_transcripts()
                        if isinstance(snippets, list):
                            transcript_text = " ".join([snippet.get('text', '') for snippet in snippets if isinstance(snippet, dict)])
                        else:
                            transcript_text = str(snippets)
                    # Handle object with a text attribute
                    elif hasattr(transcript_data, 'text'):
                        print("Processing object with 'text' attribute")
                        transcript_text = transcript_data.text
                    else:
                        # For any other case - try to extract text using string methods
                        print("Falling back to string representation")
                        transcript_text = str(transcript_data)
                        # Clean up the string representation if needed
                        if '<' in transcript_text and '>' in transcript_text:
                            # Remove HTML-like tags if present
                            transcript_text = re.sub(r'<[^>]+>', '', transcript_text)
                except Exception as extract_err:
                    print(f"Error extracting text from transcript: {extract_err}")
                    print(f"Transcript data: {transcript_data}")
                    # Last resort: convert to string
                    transcript_text = str(transcript_data)
                
                print(f"Extracted text length: {len(transcript_text) if transcript_text else 0}")
                
                if not transcript_text or len(transcript_text.strip()) < 10:
                    error_message = "Transcript is empty or too short."
                    print(error_message)
                else:
                    # Clear error message if we got a transcript
                    error_message = None
                    print("Successfully extracted transcript text")
            except Exception as e:
                error_message = f"Failed to fetch transcript data: {str(e)}"
                print(f"Error: {error_message}")
        
        # If we have a transcript, return it
        if transcript_text and not error_message:
            return transcript_text, None
        
        # If we're using alternative methods or had an error, try alternative methods
        if use_alt_methods or error_message:
            print(f"Using alternative methods for YouTube transcript: {url}")
            
            # Try alternative approaches here
            # 1. Try using different language codes
            alternative_langs = ['en-GB', 'en-CA', 'en-AU', 'auto']
            for lang in alternative_langs:
                if transcript_list:
                    try:
                        alt_transcript = transcript_list.find_transcript([lang])
                        alt_data = alt_transcript.fetch()
                        
                        # Process the data using the same robust method
                        try:
                            if isinstance(alt_data, list) and all(isinstance(item, dict) and 'text' in item for item in alt_data):
                                alt_text = " ".join([item['text'] for item in alt_data])
                            elif hasattr(alt_data, '__getitem__'):
                                alt_text = " ".join([item['text'] for item in alt_data])
                            elif hasattr(alt_data, 'fetch_transcripts'):
                                snippets = alt_data.fetch_transcripts()
                                alt_text = " ".join([snippet.get('text', '') for snippet in snippets if isinstance(snippet, dict)])
                            else:
                                alt_text = str(alt_data)
                                if '<' in alt_text and '>' in alt_text:
                                    alt_text = re.sub(r'<[^>]+>', '', alt_text)
                        except Exception as extract_err:
                            print(f"Error extracting text from alternative transcript: {extract_err}")
                            # Last resort: convert to string
                            alt_text = str(alt_data)
                            
                        if alt_text and len(alt_text.strip()) >= 10:
                            print(f"Successfully retrieved transcript using alternative language: {lang}")
                            return alt_text, None
                    except Exception as e:
                        print(f"Error with alternative language {lang}: {str(e)}")
                        pass
            
            # 2. Try using manual transcript if available
            try:
                if transcript_list:
                    for trans in list(transcript_list):
                        try:
                            if trans.is_generated is False:  # Try to get a manual transcript
                                manual_data = trans.fetch()
                                
                                # Process the data using the same robust method
                                try:
                                    if isinstance(manual_data, list) and all(isinstance(item, dict) and 'text' in item for item in manual_data):
                                        manual_text = " ".join([item['text'] for item in manual_data])
                                    elif hasattr(manual_data, '__getitem__'):
                                        manual_text = " ".join([item['text'] for item in manual_data])
                                    elif hasattr(manual_data, 'fetch_transcripts'):
                                        snippets = manual_data.fetch_transcripts()
                                        manual_text = " ".join([snippet.get('text', '') for snippet in snippets if isinstance(snippet, dict)])
                                    else:
                                        manual_text = str(manual_data)
                                        if '<' in manual_text and '>' in manual_text:
                                            manual_text = re.sub(r'<[^>]+>', '', manual_text)
                                except Exception as extract_err:
                                    print(f"Error extracting text from manual transcript: {extract_err}")
                                    # Last resort: convert to string
                                    manual_text = str(manual_data)
                                
                                if manual_text and len(manual_text.strip()) >= 10:
                                    print("Successfully retrieved manual transcript")
                                    return manual_text, None
                        except Exception as e:
                            print(f"Error with manual transcript: {str(e)}")
                            pass
            except Exception as e:
                print(f"Error accessing manual transcripts: {str(e)}")
                pass
            
            # Add more alternative methods as needed
            
            # If all alternative methods failed, return the original error
            return None, error_message or "Failed to extract transcript using all available methods"
                
        # Return the original error if there was one
        return None, error_message or "Failed to extract transcript"
                
    except Exception as e:
        return None, f"Error extracting YouTube transcript: {str(e)}" 