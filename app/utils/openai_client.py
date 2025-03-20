from openai import OpenAI
from ..config import OPENAI_API_KEY, OPENAI_MODEL

# Initialize OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)

# Fallback models in case preferred model is not available
FALLBACK_MODELS = ["gpt-4", "gpt-4-turbo", "gpt-3.5-turbo"]

def generate_script(prompt, 
                   subject="", 
                   length="medium", 
                   audience="general", 
                   tone="informative",
                   template="General",
                   context=""):
    """
    Generate an educational script using OpenAI.
    
    Args:
        prompt (str): The main script generation prompt
        subject (str): Subject matter of the script
        length (str): Desired length - short, medium, long
        audience (str): Target audience - general, beginner, advanced, etc.
        tone (str): Tone of the script - informative, conversational, etc.
        template (str): Industry-specific template to use
        context (str): Additional context information
        
    Returns:
        str: The generated script
    """
    # Get template-specific guidance
    template_guidance = get_template_guidance(template)
    
    # Prepare a system message with script generation guidelines
    system_message = f"""
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
    
    # Add context if provided
    user_message = prompt
    if context:
        user_message = f"{prompt}\n\nAdditional context to incorporate:\n{context}"
    
    try:
        # Try the primary model first
        completion = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_message}
            ],
            temperature=0.7,
            max_tokens=1500
        )
        return completion.choices[0].message.content
    except Exception as primary_err:
        print(f"Error with primary model {OPENAI_MODEL}: {str(primary_err)}")
        
        # Try fallback models
        for fallback_model in FALLBACK_MODELS:
            try:
                print(f"Trying fallback model: {fallback_model}")
                completion = client.chat.completions.create(
                    model=fallback_model,
                    messages=[
                        {"role": "system", "content": system_message},
                        {"role": "user", "content": user_message}
                    ],
                    temperature=0.7,
                    max_tokens=1500
                )
                return completion.choices[0].message.content
            except Exception as fallback_err:
                print(f"Error with fallback model {fallback_model}: {str(fallback_err)}")
                continue
        
        # If all models fail, raise an exception
        error_msg = f"Failed to generate script with all available models"
        print(error_msg)
        raise Exception(error_msg)

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
        Create a music education script that:
        - Uses clear terminology for musical concepts
        - Includes appropriate places for demonstrations or examples
        - Builds knowledge progressively
        - Incorporates practical applications of the theory
        - Suggests places where visual aids would be helpful
        - Maintains an engaging and encouraging tone
        - References how the concept relates to actual music performance
        - Includes practice suggestions or exercises
        """
    elif template == "Corporate Training":
        return """
        Create a corporate training script that:
        - Focuses on practical workplace applications
        - Uses professional language appropriate for a business setting
        - Includes relevant workplace scenarios or case studies
        - Emphasizes measurable skills or outcomes
        - Maintains a clear structure with key takeaways
        - Balances theory with actionable advice
        - Incorporates opportunities for participant reflection or discussion
        """
    elif template == "Marketing":
        return """
        Create a marketing script that:
        - Emphasizes benefits over features
        - Uses persuasive and engaging language
        - Incorporates a clear call-to-action
        - Addresses potential customer pain points
        - Maintains a consistent brand voice
        - Creates emotional connection with the audience
        - Uses concise messaging without unnecessary jargon
        - Follows a problem-solution structure when appropriate
        """
    elif template == "General Education":
        return """
        Create an educational script that:
        - Explains concepts clearly without assuming prior knowledge
        - Uses analogies or examples to illustrate complex ideas
        - Builds knowledge progressively from simple to complex
        - Incorporates opportunities for reflection or questions
        - Emphasizes key points for retention
        - Uses appropriate terminology with explanations
        - Connects the topic to real-world applications
        """
    elif template == "Technical Tutorial":
        return """
        Create a technical tutorial script that:
        - Provides step-by-step instructions in a logical sequence
        - Uses precise technical terminology correctly
        - Explains the purpose behind each step
        - Anticipates common issues or questions
        - Includes prerequisites or assumptions
        - Balances conceptual understanding with practical instructions
        - Uses consistent formatting for commands, code, or technical elements
        - References best practices in the field
        """
    else:  # General template
        return """
        Create a well-structured script that:
        - Provides clear information about the topic
        - Has a logical beginning, middle, and end
        - Uses appropriate language for the intended audience
        - Balances information with engagement
        - Maintains a consistent voice throughout
        """

def edit_script(script, instructions, context=""):
    """
    Edit a script based on instructions using OpenAI.
    
    Args:
        script (str): The original script to edit
        instructions (str): Instructions for editing the script
        context (str): Additional context for editing
        
    Returns:
        str: The edited script
    """
    # Prepare the system message
    system_message = """
    You are an expert script editor. Edit the provided script according to the instructions while maintaining its overall quality and purpose.
    Make the edits focused, clear, and natural to the flow of the original script.
    Preserve the original voice and tone unless explicitly instructed otherwise.
    """
    
    # Prepare the user message with context if provided
    user_message = f"""
    # ORIGINAL SCRIPT:
    {script}
    
    # EDIT INSTRUCTIONS:
    {instructions}
    """
    
    if context:
        user_message += f"""
        
        # ADDITIONAL CONTEXT:
        {context}
        """
    
    try:
        # Try with the preferred model first
        completion = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_message}
            ],
            temperature=0.7,
            max_tokens=1500
        )
        return completion.choices[0].message.content
    except Exception as primary_err:
        print(f"Error with primary model {OPENAI_MODEL}: {str(primary_err)}")
        
        # Try fallback models
        for fallback_model in FALLBACK_MODELS:
            try:
                print(f"Trying fallback model: {fallback_model}")
                completion = client.chat.completions.create(
                    model=fallback_model,
                    messages=[
                        {"role": "system", "content": system_message},
                        {"role": "user", "content": user_message}
                    ],
                    temperature=0.7,
                    max_tokens=1500
                )
                return completion.choices[0].message.content
            except Exception as fallback_err:
                print(f"Error with fallback model {fallback_model}: {str(fallback_err)}")
                continue
        
        # If all models fail, raise an exception
        error_msg = f"Failed to edit script with all available models"
        print(error_msg)
        raise Exception(error_msg)

# Alias functions for backwards compatibility
def generate_script_with_openai(prompt, subject="", length="medium", audience="general", tone="informative", template="General", context=""):
    """Alias for generate_script for backwards compatibility"""
    return generate_script(prompt, subject, length, audience, tone, template, context)

def edit_script_with_openai(script, instructions, context=""):
    """Alias for edit_script for backwards compatibility"""
    return edit_script(script, instructions, context) 