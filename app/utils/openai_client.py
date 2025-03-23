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
        Create a professional music education script that follows this exact structure:
        
        [INTRODUCTION - 10% of script]
        - Begin with an engaging hook about the subject
        - State clear learning objectives
        - Connect to previous knowledge
        
        [CONCEPT EXPLANATION - 30% of script]
        - Define key musical terminology with precise explanations
        - Use accessible analogies for complex musical concepts
        - Include [DEMONSTRATION POINT] markers where instructor should demonstrate
        
        [GUIDED PRACTICE - 30% of script]
        - Provide step-by-step sequence for skill development
        - Include [STUDENT PRACTICE] markers with exact timing (e.g., "Take 30 seconds to try...")
        - Anticipate common mistakes and include correction guidance
        
        [APPLICATION - 20% of script]
        - Connect the skill to real musical pieces or performances
        - Include at least one practical exercise formatted as numbered steps
        - Reference how this concept applies to different musical contexts
        
        [CONCLUSION - 10% of script]
        - Summarize key points using bullet points
        - Provide specific next-step practice suggestions with timing (e.g., "Practice daily for 10 minutes")
        - End with an inspirational connection to musical performance
        
        Throughout the script:
        - Mark visual aid opportunities with [VISUAL CUE: description]
        - Format all musical terms in bold
        - Use encouraging, supportive language appropriate for the specified audience level
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
        
        Throughout the script:
        - Include [SLIDE CONTENT] markers for presentation slide suggestions
        - Mark handout opportunities as [HANDOUT: description]
        - Maintain professional language with concrete metrics and business terminology
        - Include at least 3 [KNOWLEDGE CHECK] questions at strategic points
        """
    elif template == "Marketing":
        return """
        Create a high-conversion marketing script using this proven structure:
        
        [HOOK - 10% of script]
        - Open with a compelling question or statement targeting the audience's primary pain point
        - Include timing marker [0:00-0:XX] for audio/video production
        - Use second-person perspective ("you") to create immediate connection
        
        [PROBLEM AMPLIFICATION - 20% of script]
        - Vividly describe the problem/need using emotionally resonant language
        - Include specific examples of how this problem affects the target audience daily
        - Reference key audience demographics and psychographics in scenarios
        - Add [VISUAL: description] markers for key emotional moments
        
        [SOLUTION INTRODUCTION - 15% of script]
        - Introduce the solution with emphasis on transformation, not features
        - Format the main value proposition in bold as a standalone statement
        - Include [TONE SHIFT] marker with specific direction (e.g., "Music becomes uplifting")
        
        [BENEFIT ELABORATION - 25% of script]
        - Present 3-5 key benefits (not features), each formatted as:
          * Benefit statement focused on audience outcome
          * Emotional reinforcement of the benefit
          * Concrete example or mini-story illustrating the benefit
          * [PROOF POINT] with specific evidence (testimonial, statistic, demonstration)
        
        [OBJECTION HANDLING - 15% of script]
        - Subtly address 2-3 common objections before they arise
        - Format each as a question/concern followed by reassuring resolution
        - Include risk-reversal elements (guarantees, social proof)
        
        [CALL TO ACTION - 15% of script]
        - Clear, specific action direction with urgency element
        - Repeat the primary benefit as motivation for action
        - Include specific instructions formatted as steps if needed
        - End with reinforcement of positive outcome after taking action
        
        Throughout the script:
        - Maintain consistent brand voice appropriate for the target audience
        - Use short, punchy sentences for emphasis at key points
        - Incorporate power words and emotional triggers relevant to the offering
        - Include [CUT TO] or [TRANSITION] markers for scene/visual changes
        """
    elif template == "General Education":
        return """
        Create an educational script following this proven teaching structure:
        
        [ENGAGE - 10% of script]
        - Begin with a thought-provoking question, surprising fact, or relevant scenario about the subject
        - Create a "need to know" moment that sparks curiosity
        - Include a clear learning objective statement: "By the end of this lesson, you will be able to..."
        
        [ACTIVATE PRIOR KNOWLEDGE - 15% of script]
        - Reference what the audience likely already knows about the topic
        - Provide a bridge between existing knowledge and new concepts
        - Include an [ENGAGEMENT QUESTION] that prompts reflection on prior experience
        
        [DIRECT INSTRUCTION - 30% of script]
        - Present new concepts in a logical sequence with clear transitions
        - For each key concept:
          * Provide a clear definition in bold
          * Include a concrete, relatable example
          * Add a helpful analogy marked as [ANALOGY: description]
          * Connect to visual aids with [VISUAL REFERENCE: description]
          * Emphasize key points with deliberate repetition
        
        [GUIDED PRACTICE - 20% of script]
        - Create structured application opportunities with:
          * Clear instructions formatted as numbered steps
          * [PAUSE POINT: XX seconds] for audience processing
          * Sample responses or examples of correct application
          * Common misconceptions and corrections
        
        [INDEPENDENT APPLICATION - 15% of script]
        - Provide more complex application scenarios or problems
        - Include [ACTIVITY] markers with specific instructions and timing
        - Offer hints or scaffolding for different ability levels
        
        [SYNTHESIS & ASSESSMENT - 10% of script]
        - Summarize key points as a bulleted list
        - Include 3-5 [ASSESSMENT QUESTION] items of varying difficulty
        - Provide real-world relevance and future application examples
        
        Throughout the script:
        - Use clear transitions between sections
        - Include specific [ENGAGEMENT TECHNIQUE] markers (e.g., Think-Pair-Share, Quick Poll)
        - Format examples in italics to distinguish from instructional content
        - Adjust language complexity precisely to the specified audience level
        """
    elif template == "Technical Tutorial":
        return """
        Create a technical tutorial script using this comprehensive structure:
        
        [OVERVIEW - 10% of script]
        - Begin with a clear statement of what will be accomplished
        - List specific prerequisites as bullet points, including versions/equipment
        - Include a difficulty level indicator and time estimate
        - Explain the real-world application and value of this technical skill
        
        [ENVIRONMENT SETUP - 15% of script]
        - Provide detailed setup instructions formatted as numbered steps
        - Format all commands, code, or terminal input as code blocks
        - Include expected output/results after each command
        - Add [VERIFICATION STEP] markers to confirm correct setup
        
        [CORE PROCEDURE - 50% of script]
        - Break the process into clearly numbered main steps
        - For each step:
          * Begin with the purpose/goal of this specific step
          * Provide exact commands/code needed
          * Explain what each command/parameter does
          * Include expected output or success indicators
          * Add [IMPORTANT] tags for critical warnings or notes
          * Include screenshots or visual cues with [VISUAL: description]
        
        [TROUBLESHOOTING SECTION - 15% of script]
        - Address 3-5 common issues or errors with:
          * Exact error message or symptom
          * Cause explanation
          * Step-by-step resolution instructions
          * Preventative advice
        
        [EXTENSION & APPLICATION - 10% of script]
        - Provide 2-3 variations or advanced applications
        - Reference related tutorials or documentation for further learning
        - Include a practical example of real-world implementation
        
        Throughout the script:
        - Use consistent formatting for filenames, variables, and code elements
        - Include [NOTE] blocks for important contextual information
        - Add [TIP] blocks for efficiency or best practices
        - Maintain precise technical language appropriate for the audience level
        - Include progress validation points after each major section
        """
    else:  # General template
        return """
        Create a professionally structured script that follows this effective framework:
        
        [INTRODUCTION - 15% of script]
        - Begin with an engaging hook related to the subject
        - Establish relevance to the audience with a clear "why this matters" statement
        - Preview the main points that will be covered (3-5 points)
        
        [MAIN CONTENT - 70% of script]
        - Organize content into 3-5 distinct sections with clear subheadings
        - For each section:
          * Begin with a clear topic statement
          * Develop the concept with explanations and examples
          * Include at least one engaging element (question, story, surprising fact)
          * End with a mini-summary or transition
        - Use a logical progression that builds knowledge sequentially
        - Format key points or definitions in bold for emphasis
        - Include [VISUAL ELEMENT] markers where visuals would enhance understanding
        
        [CONCLUSION - 15% of script]
        - Summarize the main points concisely
        - Reinforce the core message or takeaway
        - End with a thought-provoking statement or call to action
        
        Throughout the script:
        - Maintain consistent voice and tone appropriate for the specified audience
        - Use varied sentence structures to maintain engagement
        - Include periodic audience engagement elements marked as [ENGAGEMENT POINT]
        - Adjust technical language and complexity to match the specified audience level
        - Format examples or stories in italics to distinguish from main content
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