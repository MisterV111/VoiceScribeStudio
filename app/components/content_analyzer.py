"""
Handles the analysis of external content sources (documents, web pages, YouTube links)
using LLMs like Claude 3.7 Sonnet to extract key information for script generation.
"""

import os
import json

# Import the specific client function (adjust path if needed)
from ..utils.llm_clients import call_claude_sonnet_for_analysis 

def analyze_document_content(document_text: str) -> dict:
    """
    Analyzes the provided text content (from a document) using Claude 3.7 Sonnet.

    Args:
        document_text: The raw text content of the document.

    Returns:
        A dictionary containing structured analysis results (e.g., summary, key topics).
        Returns an error dictionary if analysis fails.
    """
    print(f"Analyzing document content (length: {len(document_text)} chars) using Claude Sonnet...")
    
    if not document_text:
        return {"error": "No document text provided for analysis."}
    
    # --- Define the Structured Output Format --- 
    # We want Claude to return JSON matching this structure
    json_structure = """
    {
        "summary": "<A concise, neutral summary of the document's main points (2-4 sentences)>",
        "key_topics": ["<List of 3-5 main topics or themes discussed>"],
        "structure_outline": ["<List of potential section headings or logical flow identified>"],
        "extracted_keywords": ["<List of 5-10 important keywords or technical terms>"]
    }
    """
    
    # --- Construct the Prompt for Claude --- 
    # Instruct Claude to analyze the text and return JSON in the specified format
    system_prompt = "You are an expert content analyst. Your task is to carefully read the provided document text and extract key information. Respond ONLY with a valid JSON object matching the specified structure, containing your analysis. Do not include any introductory text, explanations, or markdown formatting around the JSON."
    
    user_prompt = f"""
Please analyze the following document text and provide the analysis as a JSON object matching the structure below.

JSON Structure:
```json
{json_structure}
```

Document Text:
<document>
{document_text}
</document>

Respond only with the populated JSON object.
"""
    
    # --- Call the Claude 3.7 Sonnet API --- 
    try:
        # We assume a function call_claude_sonnet_for_analysis exists in llm_clients
        # This function should handle the API call, token tracking, and error handling
        # It should ideally return the parsed JSON content or None/error
        analysis_result_raw = call_claude_sonnet_for_analysis(system_prompt, user_prompt)
        
        if analysis_result_raw:
            # Attempt to parse the JSON response from Claude
            try:
                analysis_result = json.loads(analysis_result_raw)
                print("Document analysis complete and JSON parsed successfully.")
                # Optional: Add validation here to ensure the structure matches expected keys
                return analysis_result
            except json.JSONDecodeError as json_err:
                print(f"Error parsing JSON response from Claude: {json_err}")
                print(f"Raw response: {analysis_result_raw}") # Log the raw response for debugging
                return {"error": "Failed to parse analysis result from Claude.", "raw_response": analysis_result_raw}
        else:
            print("Claude analysis returned no result.")
            return {"error": "Analysis failed, Claude returned no result."}
            
    except Exception as e:
        print(f"Error during Claude analysis API call: {str(e)}")
        # Log the full traceback for detailed debugging if needed
        # import traceback
        # traceback.print_exc()
        return {"error": f"An unexpected error occurred during analysis: {str(e)}"}

# --- Future Functions (Placeholders) --- 

def analyze_youtube_url(youtube_url: str) -> dict:
    """
    Analyzes a YouTube URL to extract transcript/metadata for style reference.
    
    Args:
        youtube_url: The YouTube URL to analyze
        
    Returns:
        dict: Analysis results or error information
    """
    print(f"Analyzing YouTube URL: {youtube_url}")
    
    if not youtube_url or not youtube_url.strip():
        return {"error": "No YouTube URL provided."}
    
    try:
        # Import the YouTube utilities
        from ..utils.reference_handlers.youtube_utils import extract_youtube_transcript, extract_video_id
        
        # Extract video ID first for validation
        video_id = extract_video_id(youtube_url)
        if not video_id:
            return {"error": "Invalid YouTube URL format. Could not extract video ID."}
            
        print(f"Extracted video ID: {video_id}")
        
        # Try to extract the transcript, with alternative methods if needed
        transcript_text, error = extract_youtube_transcript(youtube_url, use_alt_methods=True)
        
        if error:
            print(f"Error extracting transcript: {error}")
            return {"error": f"Failed to extract YouTube transcript: {error}"}
            
        if not transcript_text or len(transcript_text) < 100:
            print("Transcript too short or empty")
            return {"error": "The extracted transcript is too short or empty."}
        
        print(f"Successfully extracted transcript with {len(transcript_text)} characters")
        
        # Return the transcript for now
        # In a future enhancement, we could analyze the transcript with Claude
        return {
            "transcript": transcript_text,
            "video_id": video_id,
            "url": youtube_url
        }
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"error": f"Error analyzing YouTube URL: {str(e)}"}

def analyze_web_url(web_url: str) -> dict:
    """
    Fetches and analyzes content from a general web URL.
    (Placeholder - requires basic web fetching)
    """
    print(f"Analyzing Web URL: {web_url} (placeholder)...")
    return {"error": "Web URL analysis not yet implemented."} 