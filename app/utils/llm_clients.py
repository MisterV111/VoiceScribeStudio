from openai import OpenAI
from anthropic import Anthropic
import uuid
from ..config import (
    DEEPSEEK_API_KEY, DEEPSEEK_MODEL,
    DEEPSEEK_BASE_URL,
    ANTHROPIC_API_KEY, CLAUDE_MODEL
)
from .token_counter import token_tracker
import re

# --- Client Initialization --- 

# DeepSeek Client (using OpenAI SDK)
if DEEPSEEK_API_KEY and DEEPSEEK_BASE_URL:
    # This client instance is specifically for DeepSeek
    deepseek_client_via_openai_sdk = OpenAI(
        api_key=DEEPSEEK_API_KEY,
        base_url=DEEPSEEK_BASE_URL
    )
else:
    deepseek_client_via_openai_sdk = None
    if not DEEPSEEK_API_KEY:
        print("Warning: DEEPSEEK_API_KEY not found. DeepSeek functionality disabled.")
    if not DEEPSEEK_BASE_URL:
        print("Warning: DEEPSEEK_BASE_URL not found or invalid. DeepSeek functionality disabled.")

# Anthropic Client
if ANTHROPIC_API_KEY:
    try:
        import time
        import random
        # Import base anthropic package first
        import anthropic
        
        # Determine which error types to import based on what's available in the package
        if hasattr(anthropic, 'types') and hasattr(anthropic.types, 'APIStatusError'):
            # Newer version structure
            from anthropic.types import RateLimitError, APIStatusError, APITimeoutError, APIConnectionError
        elif hasattr(anthropic, 'RateLimitError'):
            # Older version structure
            from anthropic import RateLimitError, APIError as APIStatusError
            # Create aliases for missing error types
            APITimeoutError = APIStatusError
            APIConnectionError = APIStatusError
            print("Using older anthropic library error types")
        else:
            # Create fallback error types if none are available
            print("Unable to import specific Anthropic error types - using generic exceptions")
            RateLimitError = Exception
            APIStatusError = Exception
            APITimeoutError = Exception
            APIConnectionError = Exception
        
        # Create a session with retry logic
        anthropic_client = Anthropic(
            api_key=ANTHROPIC_API_KEY,
            # Default timeout settings
            timeout=60.0  # 60 second timeout
        )
        
        # Wrapper function for anthropic calls with retries
        def call_anthropic_with_retry(func, *args, max_retries=3, initial_retry_delay=2, **kwargs):
            """
            Execute an Anthropic API call with exponential backoff retry logic.
            
            Args:
                func: The anthropic client function to call
                *args: Arguments to pass to the function
                max_retries: Maximum number of retries
                initial_retry_delay: Initial delay in seconds before retry (will increase exponentially)
                **kwargs: Keyword arguments to pass to the function
                
            Returns:
                The function result or raises the last exception after retries
            """
            retry_count = 0
            retry_delay = initial_retry_delay
            
            while True:
                try:
                    return func(*args, **kwargs)
                except (RateLimitError, APIStatusError, APITimeoutError, APIConnectionError) as e:
                    retry_count += 1
                    status_code = getattr(e, 'status_code', None)
                    
                    # Log the error
                    print(f"Anthropic API error (attempt {retry_count}/{max_retries}): {type(e).__name__}")
                    if status_code:
                        print(f"Status code: {status_code}")
                    
                    # If we hit max retries or it's not a retriable error, raise
                    if retry_count >= max_retries or not (
                        isinstance(e, RateLimitError) or  # Rate limits (429)
                        (isinstance(e, APIStatusError) and status_code in (429, 500, 502, 503, 504, 529)) or  # Server errors
                        isinstance(e, APITimeoutError) or  # Timeouts
                        isinstance(e, APIConnectionError)  # Connection issues
                    ):
                        raise
                    
                    # Calculate jittered exponential backoff
                    jitter = random.uniform(0.8, 1.2)
                    sleep_time = retry_delay * jitter
                    print(f"Retrying in {sleep_time:.2f} seconds...")
                    time.sleep(sleep_time)
                    
                    # Increase the delay for next time
                    retry_delay = min(retry_delay * 2, 30)  # Cap at 30 seconds
                except Exception as e:
                    # For any other exceptions, don't retry
                    print(f"Unretriable error in Anthropic API call: {type(e).__name__}: {str(e)}")
                    raise
        
        # Test the client with a simple request
        print("Testing Anthropic client connection...")
        try:
            call_anthropic_with_retry(
                anthropic_client.messages.create,
                model="claude-3-haiku-20240307",
                messages=[{"role": "user", "content": "Hello, this is a connection test."}],
                system="You are a helpful AI.",
                max_tokens=10
            )
            print("Anthropic client connection successful.")
        except Exception as e:
            print(f"Warning: Anthropic client test failed: {str(e)}")
            print("Claude functionality may be limited.")
    except Exception as init_error:
        anthropic_client = None
        print(f"Warning: Failed to initialize Anthropic client: {str(init_error)}")
        print("Claude functionality disabled due to initialization error.")
else:
    anthropic_client = None
    print("Warning: ANTHROPIC_API_KEY not found. Claude functionality disabled.")

# --- Generation Helper Functions --- 

def _generate_with_openai_sdk(client_instance, system_message, user_message, model, template=None, params=None, session_id=None, is_test=False):
    """Helper to generate script using an OpenAI-compatible SDK client instance (like DeepSeek)."""
    if not client_instance:
        print(f"Client instance for model {model} not available. Skipping.")
        return None
        
    try:
        print(f"Attempting script generation with model: {model} via client: {getattr(client_instance, 'base_url', 'Unknown Base URL')}")
        
        # Create messages array for the API call
        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_message}
        ]
        
        # Perform the API call
        completion = client_instance.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0.7,
            max_tokens=3000 
        )
        
        # --- Token Tracking --- 
        prompt_tokens = 0
        completion_tokens = 0
        if completion.usage:
            prompt_tokens = completion.usage.prompt_tokens
            completion_tokens = completion.usage.completion_tokens
            print(f"Token Usage ({model}): Prompt={prompt_tokens}, Completion={completion_tokens}, Total={completion.usage.total_tokens}")
        else:
            print(f"Token usage data not available for {model}.")
            
        # Content retrieval
        if completion.choices and completion.choices[0].message:
            generated_content = completion.choices[0].message.content
            print(f"Model {model} generated {len(generated_content.split())} words.")
            
            # Enhanced token tracking with our system
            # Use reported tokens if available, otherwise let the tracker count them
            input_text = system_message + "\n" + user_message
            token_metrics = token_tracker.track_generation(
                model="deepseek",
                input_text=input_text,
                output_text=generated_content,
                template=template,
                is_fallback=False,
                parameters=params,
                session_id=session_id,
                is_test=is_test,
                success=True
            )
            
            # Return both content and metrics
            return {
                "content": generated_content,
                "token_metrics": token_metrics,
                "model_used": "deepseek"
            }
        else:
            print(f"Model {model} response did not contain expected content.")
            return None
            
    except Exception as e:
        print(f"Error generating script with OpenAI-SDK compatible model {model}: {str(e)}")
        import traceback
        traceback.print_exc()
        
        # Track failed attempt
        if system_message and user_message:
            token_tracker.track_generation(
                model="deepseek",
                input_text=system_message + "\n" + user_message,
                output_text="",
                template=template,
                is_fallback=False,
                parameters=params,
                session_id=session_id,
                is_test=is_test,
                success=False
            )
            
        return None

def _generate_with_claude(system_message, user_message, model=CLAUDE_MODEL, template=None, params=None, 
                         is_fallback=False, session_id=None, is_test=False):
    """Helper to generate script using the Anthropic Claude API."""
    if not anthropic_client:
        print(f"Anthropic client not available. Skipping Claude generation.")
        return None
        
    try:
        print(f"Attempting script generation with Claude model: {model}")
        
        # Use our retry wrapper function instead of direct API call
        try:
            message = call_anthropic_with_retry(
                anthropic_client.messages.create,
                model=model,
                system=system_message, 
                messages=[{"role": "user", "content": user_message}],
                temperature=0.7,
                max_tokens=3000,
                max_retries=3  # Retry up to 3 times
            )
        except Exception as api_error:
            print(f"Claude API call failed after retries: {type(api_error).__name__}: {str(api_error)}")
            # Check for specific error types that should be handled gracefully
            status_code = getattr(api_error, 'status_code', None)
            if status_code:
                print(f"Status code from Claude API: {status_code}")
                if status_code == 529:
                    return {
                        "content": "Sorry, the Claude API is currently overloaded. Please try again in a few minutes.",
                        "token_metrics": {},
                        "model_used": "claude",
                        "is_fallback": is_fallback,
                        "error": "Claude API overloaded (HTTP 529). Please try again later."
                    }
            # Re-raise if we didn't handle it specifically
            raise
        
        # --- Token Tracking --- 
        input_tokens = 0
        output_tokens = 0
        if message.usage:
            input_tokens = message.usage.input_tokens
            output_tokens = message.usage.output_tokens
            total_tokens = input_tokens + output_tokens # Claude API might not provide total directly
            print(f"Token Usage ({model}): Input={input_tokens}, Output={output_tokens}, Total={total_tokens}")
        else:
            print(f"Token usage data not available for {model}.")
            
        # Content retrieval
        if message.content and isinstance(message.content, list) and message.content[0].text:
            generated_content = message.content[0].text
            
            # Check for error messages in the content itself
            error_patterns = [
                r'error (\d+)',
                r'(\d{3})[\s-]+(overloaded|unavailable|error)',
                r'<\s*h\d\s*>\s*(\d{3})\s*',
                r'```\s*(\d{3})'
            ]
            
            for pattern in error_patterns:
                error_match = re.search(pattern, generated_content, re.IGNORECASE)
                if error_match:
                    error_code = error_match.group(1)
                    print(f"Detected possible error code in content: {error_code}")
                    return {
                        "content": "Sorry, the Claude API returned an error response. Please try again in a few minutes.",
                        "token_metrics": {},
                        "model_used": "claude",
                        "is_fallback": is_fallback,
                        "error": f"Claude API returned an error in content (code: {error_code}). Please try again later."
                    }
            
            print(f"Claude model {model} generated {len(generated_content.split())} words.")
            
            # Enhanced token tracking with our system
            # Use reported tokens if available, otherwise let the tracker count them
            token_metrics = token_tracker.track_generation(
                model="claude",
                input_text=system_message + "\n" + user_message,
                output_text=generated_content,
                template=template,
                is_fallback=is_fallback,
                parameters=params,
                session_id=session_id,
                is_test=is_test,
                success=True
            )
            
            # Return both content and metrics
            return {
                "content": generated_content,
                "token_metrics": token_metrics,
                "model_used": "claude",
                "is_fallback": is_fallback
            }
        else:
            print(f"Claude model {model} response did not contain expected content structure.")
            return {
                "content": "Sorry, the response from Claude API was not in the expected format. Please try again.",
                "token_metrics": {},
                "model_used": "claude",
                "is_fallback": is_fallback,
                "error": "Invalid response format from Claude API."
            }
            
    except Exception as e:
        print(f"Error generating script with Claude model {model}: {str(e)}")
        import traceback
        traceback.print_exc()
        
        # Track failed attempt
        if system_message and user_message:
            token_tracker.track_generation(
                model="claude",
                input_text=system_message + "\n" + user_message,
                output_text="",
                template=template,
                is_fallback=is_fallback,
                parameters=params,
                session_id=session_id,
                is_test=is_test,
                success=False
            )
            
        return {
            "content": f"Error generating script: {str(e)}",
            "token_metrics": {},
            "model_used": "claude",
            "is_fallback": is_fallback,
            "error": str(e)
        }

# --- New Claude Helper for Analysis --- 
def call_claude_sonnet_for_analysis(system_prompt: str, user_prompt: str, model: str = CLAUDE_MODEL) -> str | None:
    """
    Calls the Claude Sonnet API specifically for analysis tasks that expect a structured response (like JSON).
    
    This is a specialized helper for analysis tasks, more focused than the general generation function.
    
    Args:
        system_prompt: The system prompt guiding the analysis task.
        user_prompt: The user prompt containing the content to analyze and structure instructions.
        model: The Claude model to use (defaults to the one in config.py).
        
    Returns:
        str: The raw model output if successful, or None if there's an error.
    """
    if not anthropic_client:
        print(f"Anthropic client not available. Skipping Claude analysis call.")
        return None
        
    try:
        print(f"Attempting analysis with Claude model: {model}")
        
        # Call the Claude API with retry logic
        message = call_anthropic_with_retry(
            anthropic_client.messages.create,
            model=model,
            system=system_prompt,
            messages=[
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.0,  # Use 0 temperature for analytical tasks for consistency
            max_tokens=2000  # Adjust max_tokens based on expected analysis size
        )
        
        # Handle token usage reporting
        if hasattr(message, 'usage'):
            print(f"Token Usage (Analysis - {model}): Input={message.usage.input_tokens}, Output={message.usage.output_tokens}")
        else:
            print(f"Token usage data not available for analysis call ({model}).")
            
        # Extract content from the response
        if message.content and isinstance(message.content, list) and len(message.content) > 0 and hasattr(message.content[0], 'text'):
            content = message.content[0].text
            print(f"Claude model {model} returned analysis content.")
            return content
        else:
            print(f"Claude model {model} analysis response did not contain expected text content.")
            return None
    except Exception as e:
        print(f"Error during Claude analysis API call with model {model}: {str(e)}")
        return None

# ---------------
# Content Analysis
# ---------------

def analyze_content(content_type, content, **kwargs):
    """
    Analyzes content from different sources and returns structured data.
    
    This function acts as a central dispatcher for content analysis
    features, selecting the appropriate analyzer based on content_type.
    
    Args:
        content_type (str): The type of content to analyze:
            - "document": Direct text content from a document
            - "youtube": A YouTube URL for transcript analysis
            - "web": A general web URL for content analysis
        content (str): The actual content to analyze (text or URL)
        **kwargs: Additional parameters specific to different content types
    
    Returns:
        dict: Structured analysis results or error information
    """
    try:
        from ..components.content_analyzer import (
            analyze_document_content,
            analyze_youtube_url,
            analyze_web_url
        )
        
        # Log the analysis request
        print(f"Analyzing content of type: {content_type}")
        
        # Validate basic inputs
        if not content or not isinstance(content, str):
            return {"error": "No content provided for analysis"}
            
        if content_type == "document":
            # Direct document text analysis
            return analyze_document_content(content)
            
        elif content_type == "youtube":
            # YouTube URL analysis
            return analyze_youtube_url(content)
            
        elif content_type == "web":
            # General web URL analysis
            return analyze_web_url(content)
            
        else:
            return {"error": f"Unsupported content type: {content_type}"}
            
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"error": f"Error in content analysis: {str(e)}"}

# --- Main Generation Function --- 

def generate_script(prompt: str, 
                   subject: str ="", 
                   length: str ="medium", 
                   audience: str ="general", 
                   tone: str ="informative",
                   template: str ="General",
                   context: str ="",
                   analysis_results: dict | None = None,
                   force_fallback: bool =False,
                   is_test: bool =False):
    """
    Generate an educational script using the best available LLM 
    (DeepSeek primary via OpenAI SDK, Claude fallback).
    Optionally uses pre-computed analysis results to enhance generation.
    
    Args:
        prompt (str): The main script generation prompt
        subject (str): Subject matter of the script
        length (str): Desired length - short, medium, long
        audience (str): Target audience - general, beginner, advanced, etc.
        tone (str): Tone of the script - informative, conversational, etc.
        template (str): Industry-specific template to use
        context (str): Additional context information (e.g., background knowledge)
        analysis_results (dict | None): Structured analysis from content_analyzer (optional)
        force_fallback (bool): If True, skip primary model and use Claude directly.
        is_test (bool): Whether this is a test generation
        
    Returns:
        dict or None: Dictionary containing generated content and metadata, or None if failed.
    """
    # Generate session ID for tracking this generation across models
    session_id = str(uuid.uuid4())
    
    # Get template-specific guidance
    template_guidance = get_template_guidance(template)
    
    # Prepare base system message
    system_message_base = f"""
    You are an expert educational script writer. Create a well-structured {length} script 
    about {subject} for a {audience} audience with a {tone} tone.
    
    {template_guidance}
    
    Use clear, engaging language and organize the content logically.
    Include appropriate transitions, examples, and explanations.
    
    Length guideline:
    - Short: 150-250 words
    - Medium: 300-500 words
    - Long: 600-900 words
    """
    
    # --- Incorporate Analysis Results into System Message (if available) --- 
    system_message = system_message_base
    if analysis_results and isinstance(analysis_results, dict):
        print("Incorporating analysis results into generation prompt...")
        analysis_context = "\n\nCONTEXTUAL ANALYSIS (Use this information to enhance the script's accuracy and relevance):\n"
        if "summary" in analysis_results:
            analysis_context += f"- Summary: {analysis_results['summary']}\n"
        if "key_topics" in analysis_results and analysis_results['key_topics']:
            analysis_context += f"- Key Topics: {', '.join(analysis_results['key_topics'])}\n"
        if "structure_outline" in analysis_results and analysis_results['structure_outline']:
            analysis_context += f"- Suggested Structure: {', '.join(analysis_results['structure_outline'])}\n"
        if "extracted_keywords" in analysis_results and analysis_results['extracted_keywords']:
            analysis_context += f"- Keywords: {', '.join(analysis_results['extracted_keywords'])}\n"
        
        system_message += analysis_context
        system_message += "\nGenerate the script based on the user's main prompt, ensuring it aligns with and incorporates insights from this contextual analysis. Focus on accuracy based on the context provided."
    # --- End Analysis Incorporation ---

    # Prepare user message (handle existing context field)
    user_message = prompt
    if context:
        # Special handling for Music Lesson context, append analysis after it
        if template == "Music Lesson":
            user_message = f"""
{prompt}

BACKGROUND KNOWLEDGE (Do not reference this directly in your script):
{context}

Remember to build naturally on this background without phrases like "as you've learned before" or "now that you know X". Simply assume this knowledge is present and create a natural progression.
"""
        else:
            user_message = f"{prompt}\n\nAdditional context to incorporate:\n{context}"
    
    # Create parameters dict for token tracking
    params = {
        "subject": subject,
        "length": length,
        "audience": audience,
        "tone": tone,
        "analysis_provided": bool(analysis_results) # Track if analysis was used
    }
    
    # --- Generation Logic --- 
    print("--- Starting Script Generation --- ")
    result = None
    
    # Check if fallback is forced
    if force_fallback:
        print("--- Fallback to Claude forced --- ")
    else:
        # 1. Try DeepSeek (via OpenAI SDK)
        if deepseek_client_via_openai_sdk:
            result = _generate_with_openai_sdk(
                deepseek_client_via_openai_sdk, 
                system_message, # Use potentially modified system_message
                user_message, 
                model=DEEPSEEK_MODEL,
                template=template,
                params=params,
                session_id=session_id,
                is_test=is_test
            )
            
            if result:
                print("--- Script generated successfully with DeepSeek (via OpenAI SDK) --- ")
                return result # Always return the dict now
            else:
                 print("--- DeepSeek (via OpenAI SDK) failed, attempting Claude fallback --- ")
        else:
            print("--- DeepSeek client not configured, attempting Claude fallback --- ")

    # 2. Try Claude Model (either as fallback or forced)
    if anthropic_client:
        # Note: Claude fallback currently uses the *original* system message without analysis context
        # We might want to reconsider if Claude should also use the analysis context in fallback scenarios
        result = _generate_with_claude(
            system_message_base, # Use original system message for fallback for now
            user_message, 
            model=CLAUDE_MODEL,
            template=template,
            params=params,
            is_fallback=not force_fallback,  # It's a fallback unless explicitly forced
            session_id=session_id,
            is_test=is_test
        )
        
        if result:
             print(f"--- Script generated successfully with Claude ({CLAUDE_MODEL}){' (forced fallback)' if force_fallback else ' (fallback)'} --- ")
             return result # Always return the dict
        else:
            print(f"--- Claude ({CLAUDE_MODEL}) also failed. --- ")
    else:
        print("--- Anthropic client not configured. Cannot fallback to Claude. --- ")
            
    # 3. If all configured models fail
    print("--- All configured models failed to generate the script. --- ")
    # Track complete failure (maybe needed in token_tracker?)
    token_tracker.track_generation(
        model="none",
        input_text=system_message + "\n" + user_message,
        output_text="GENERATION FAILED",
        template=template,
        is_fallback=False,
        parameters=params,
        session_id=session_id,
        is_test=is_test,
        success=False
    )
    return None # Return None on complete failure

# --- Editing Function (Now using Claude) --- 
def edit_script_with_claude(original_script, edit_instructions, context="", is_test=False):
    """
    Edit a script using the Anthropic Claude API.
    
    Args:
        original_script (str): The script to be edited.
        edit_instructions (str): Instructions on how to edit the script.
        context (str): Additional context to consider during editing.
        is_test (bool): Whether this is a test edit
        
    Returns:
        str or dict: The edited script (str) or dict with script and metadata
    """
    if not anthropic_client:
        print("Anthropic client not initialized. Skipping Claude editing.")
        return None

    # Generate session ID for tracking
    session_id = str(uuid.uuid4())

    # Use a system prompt appropriate for Claude editing
    system_message = "You are an expert script editor. Your task is to modify the provided script based *only* on the user's specific instructions. Maintain the original tone, style, and length unless explicitly asked to change them. Apply the edits precisely and return only the complete, edited script without any commentary or explanation before or after it." 
       
    user_message = f"Original Script:\n<original_script>{original_script}</original_script>\n\nEdit Instructions:\n<edit_instructions>{edit_instructions}</edit_instructions>"
    if context:
        user_message += f"\n\nAdditional Context for Editing:\n<context>{context}</context>"
        
    try:
        # Use the primary Claude model for editing
        print(f"Attempting script editing with Claude model: {CLAUDE_MODEL}")
        message = anthropic_client.messages.create(
            model=CLAUDE_MODEL, 
            system=system_message, # System prompt for Claude
            messages=[
                {"role": "user", "content": user_message}
            ],
            temperature=0.3, # Lower temperature for precise editing
            max_tokens=3500 # Allow ample tokens for editing
        )
        
        # --- Token Tracking --- 
        input_tokens = 0
        output_tokens = 0
        if message.usage:
            input_tokens = message.usage.input_tokens
            output_tokens = message.usage.output_tokens
            total_tokens = input_tokens + output_tokens
            print(f"Token Usage (Editing - {CLAUDE_MODEL}): Input={input_tokens}, Output={output_tokens}, Total={total_tokens}")
        else:
             print(f"Token usage data not available for editing with {CLAUDE_MODEL}.")
             
        # Content retrieval
        if message.content and isinstance(message.content, list) and message.content[0].text:
            edited_content = message.content[0].text
            print("Script edited successfully with Claude.")
            
            # Enhanced token tracking for edits
            params = {"operation": "edit"}
            token_metrics = token_tracker.track_generation(
                model="claude",
                input_text=system_message + "\n" + user_message,
                output_text=edited_content,
                template="editing",  # Mark as an editing operation
                is_fallback=False,
                parameters=params,
                session_id=session_id,
                is_test=is_test,
                success=True
            )
            
            # Return both content and metrics if requested
            return {
                "content": edited_content,
                "token_metrics": token_metrics,
                "model_used": "claude"
            }
        else:
            print(f"Claude ({CLAUDE_MODEL}) editing response did not contain expected content structure.")
            return None
            
    except Exception as e:
        print(f"Error editing script with Claude model {CLAUDE_MODEL}: {str(e)}")
        import traceback
        traceback.print_exc()
        
        # Track failed edit attempt
        if system_message and user_message:
            token_tracker.track_generation(
                model="claude",
                input_text=system_message + "\n" + user_message,
                output_text="",
                template="editing",
                is_fallback=False,
                parameters={"operation": "edit"},
                session_id=session_id,
                is_test=is_test,
                success=False
            )
            
        return None

# --- get_template_guidance function --- 
def get_template_guidance(template):
    """
    Get template-specific guidance for script generation
    
    Args:
        template (str): The template to use
        
    Returns:
        str: Template-specific guidance
    """
    if template == "Music Lesson":
        return """
        Create a professional music education script WITHOUT any section markers, headers, labels, or structural notes in the final output. Follow this structure for organizing your content, but do not include any of these headings or organization notes in your response:

        Introduction:
        - Begin with a concise, engaging hook about the subject
        - Use <Talking Head> marker at the beginning of this section
        - Focus on immediate practical application rather than theory
        - Use conversational "friend showing you" tone rather than formal educational language
        
        Concept & Demonstration:
        - Begin with <Action Motion + Instrument View + VO> marker
        - Provide clear, simple instructions in layperson's terms
        - Include specific camera angle directions for key techniques: [TOP VIEW] or [SIDE VIEW]
        - Structure demonstrations as simple, sequential steps with clear visual transitions
        - Use directive language ("Place your index finger on...") rather than abstract explanations
        - Connect new techniques to songs students are already familiar with
        - Reference previous skills (what they've already learned) when introducing new concepts
        - Include detailed demonstration markers formatted as: [DEMONSTRATION: Detailed description of what is being shown, including tempo, technique focus, and visual elements]
        
        Call-to-Action:
        - Return to <Talking Head> marker
        - Include a transition phrase to the interactive element: "Let's try it out with the trainer!" or "Now it's your turn to try!"
        
        Throughout the script:
        - Include exactly one detailed demonstration break
        - Adjust your language accordingly to the target level selected by the user. For 'Beginner' and 'Children' use extremely simple language and avoid advanced music terminology
        - Reference specific strings/keys by both number and location (e.g., "the 6th string, the thickest one")
        - Ensure compatibility with interactive follow-up activities
        - Do not use asterisks (**) or other Markdown formatting in the final text
        
        ** CRITICAL INSTRUCTION: Do not include ANY of the following in your response **
        1. Section headers like [INTRODUCTION], [MAIN CONTENT], [CONCLUSION], etc.
        2. Percentages or notes about script structure (e.g., "CONCEPT & DEMONSTRATION - 80% of script")
        3. Organizational notes or reminders about the template format
        4. Any meta-information about how the script should be structured
        5. DO NOT include labels like "[CONCEPT & DEMONSTRATION]" or similar structural markers
        
        The script should be clean and ready to use without any template formatting or scaffolding visible. The final script should appear as a cohesive narrative with no visible template structure.
        
        ** CONTEXT HANDLING INSTRUCTION **
        When additional context about student knowledge is provided:
        - Use this to inform the difficulty level and examples
        - DO NOT explicitly mention the student's prior knowledge with phrases like "as you learned previously" or "now that you know X"
        - DO NOT directly refer to context information in your script
        - Instead, naturally build upon this assumed knowledge baseline
        - Tailor your examples and applications to be relevant based on this context
        
        Example of good context usage:
        Context: "Student knows basic open chords (G, C, D, Em) and can switch between them"
        BAD: "Since you already know your basic open chords like G, C, D, and Em, let's move to barre chords."
        GOOD: "Today we're moving up the neck to explore barre chords, which will expand your playing beyond the first position."
        """
    elif template == "Corporate Training":
        return """
        Create a corporate training script that follows this professional structure:
        
        [OPENING - 10% of script]
        - Begin with an attention-grabbing statistic or business scenario related to the subject
        - Clearly state the business value and measurable outcomes of this training
        - Include a quick participant engagement question marked as [ENGAGEMENT POINT]
        
        [KEY CONCEPTS - 25% of script]
        - Present 3-5 main concepts using clear business terminology
        - For each concept, include a specific workplace application example
        - Format each key concept as a concise, memorable statement in bold
        
        [CASE STUDIES/SCENARIOS - 30% of script]
        - Develop 2-3 detailed workplace scenarios that illustrate the concepts
        - Format each scenario with:
          * The situation description
          * Critical decision points or challenges
          * [GROUP DISCUSSION PROMPT] with specific questions
          * Best practice resolution with business rationale
        
        [SKILL PRACTICE - 25% of script]
        - Create structured role-play or application exercises with:
          * Clear time allocations (e.g., "Allow 10 minutes for this activity")
          * Step-by-step instructions formatted as a numbered list
          * [FACILITATOR NOTE] with implementation guidance
          * Assessment criteria for successful completion
        
        [CONCLUSION & ACTION PLANNING - 10% of script]
        - Summarize key takeaways as bullet points
        - Include a personal action plan template with 3 specific questions
        - Add a concrete follow-up commitment mechanism
        
        [KNOWLEDGE CHECK - Integrated throughout]
        - Include 2-3 multiple-choice or short-answer questions marked as [KNOWLEDGE CHECK]
        """
    elif template == "Marketing":
        return """
        Create a marketing script optimized for engagement and conversion:
        
        [HOOK - 5% of script]
        - Start with a compelling question, surprising fact, or relatable problem
        - Use <Visual: Dynamic opening shot> marker
        - Keep it under 10 seconds
        
        [PROBLEM/NEED AGITATION - 20% of script]
        - Clearly define the target audience's pain point or desire
        - Use emotional language and storytelling
        - Include a [CUSTOMER QUOTE/TESTIMONIAL snippet] placeholder
        - Use <Visual: Relatable scenario footage> marker
        
        [SOLUTION INTRODUCTION - 15% of script]
        - Introduce the product/service as the clear solution
        - State the Unique Selling Proposition (USP) concisely
        - Use <Visual: Product reveal or animation> marker
        
        [BENEFITS & FEATURES - 35% of script]
        - Highlight 3-5 key benefits, focusing on outcomes (not just features)
        - Use action-oriented language and demonstrate value
        - Include [FEATURE DEMONSTRATION: Description of visual] markers for key features
        - Use <Visual: Product in use, benefit realization shots> marker
        
        [SOCIAL PROOF/CREDIBILITY - 10% of script]
        - Mention awards, key statistics, or well-known clients
        - Include a placeholder for [TRUST BADGE/LOGO: Description]
        - Use <Visual: Graphics showing stats or logos> marker
        
        [CALL TO ACTION (CTA) - 10% of script]
        - Make a clear, direct request (e.g., "Visit our website", "Download the guide")
        - Create urgency or offer a limited-time incentive
        - Repeat the CTA clearly
        - Use <Visual: CTA button overlay, website URL display> marker
        
        [CLOSING - 5% of script]
        - End with a memorable brand statement or tagline
        - Use <Visual: Brand logo animation> marker
        """
    elif template == "General Education":
        return """
        Create an educational script with a clear, logical structure for learning:
        
        [INTRODUCTION - 15% of script]
        - Hook the learner with a relevant question or real-world connection
        - State the learning objective(s) clearly (e.g., "By the end of this lesson, you will be able to...")
        - Briefly outline the topics to be covered
        
        [EXPLANATION OF CONCEPTS - 40% of script]
        - Break down the main topic into 2-4 key concepts
        - Explain each concept using simple language and analogies
        - Use [VISUAL AID: Description of chart, diagram, or image] markers where helpful
        - Include definitions for key terminology in bold
        
        [EXAMPLES & ILLUSTRATIONS - 30% of script]
        - Provide concrete examples for each key concept
        - Use storytelling or real-world scenarios to make concepts relatable
        - Include [INTERACTIVE ELEMENT: Suggestion for simple interaction, e.g., pause and think]
        
        [SUMMARY - 10% of script]
        - Recap the main concepts and learning objectives
        - Reiterate the key takeaways in a concise bulleted list
        
        [NEXT STEPS/APPLICATION - 5% of script]
        - Suggest how learners can apply the knowledge
        - Briefly mention the topic of the next lesson or further resources
        """
    elif template == "Technical Tutorial":
        return """
        Create a technical tutorial script focused on clear, step-by-step guidance:
        
        [INTRODUCTION - 10% of script]
        - Clearly state the goal of the tutorial (e.g., "In this tutorial, you will learn how to...")
        - List any prerequisites (software, knowledge) required
        - Briefly mention the final outcome or project
        
        [SETUP & CONFIGURATION - 15% of script]
        - Detail any necessary setup steps (installation, configuration files)
        - Use [CODE SNIPPET: Description of code and language] markers for setup commands
        - Include [FILE PATH: Path to relevant file] markers
        
        [STEP-BY-STEP INSTRUCTIONS - 60% of script]
        - Break the process down into numbered steps
        - For each step, provide clear, concise instructions
        - Use action verbs (e.g., "Click", "Type", "Create")
        - Include [SCREENCAST FOCUS: Description of UI element to highlight] markers
        - Use [CODE SNIPPET: Description of code and language] for any code to be written
        - Explain the purpose of each significant step or code block
        - Mention common pitfalls or important considerations using [NOTE: Important tip or warning]
        
        [VERIFICATION & TESTING - 10% of script]
        - Describe how to verify that the steps were successful
        - Include expected output or behavior
        - Suggest simple tests to run
        
        [CONCLUSION & NEXT STEPS - 5% of script]
        - Briefly summarize what was accomplished
        - Suggest next steps or related tutorials
        """
    else: # General Template (fallback)
        return """
        Create a well-structured script focusing on clarity and engagement.
        Organize content logically with a clear introduction, body, and conclusion.
        Use appropriate language for the specified audience and tone.
        """ 