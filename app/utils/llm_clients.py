from openai import OpenAI
from .deepseek_client import generate_script_with_deepseek # Import DeepSeek generator
from ..config import OPENAI_API_KEY, OPENAI_MODEL, DEEPSEEK_MODEL # Add DEEPSEEK_MODEL

# Initialize OpenAI client
if OPENAI_API_KEY:
    openai_client = OpenAI(api_key=OPENAI_API_KEY)
else:
    openai_client = None
    print("Warning: OPENAI_API_KEY not found. OpenAI functionality will be limited.")

# OpenAI Fallback models
OPENAI_FALLBACK_MODELS = ["gpt-4", "gpt-4-turbo", "gpt-3.5-turbo"]

def generate_script_with_openai(system_message, user_message, model=OPENAI_MODEL):
    """
    Generate a script using the OpenAI API.
    
    Args:
        system_message (str): The system prompt guiding the model.
        user_message (str): The user's prompt and context.
        model (str): The OpenAI model to use.
        
    Returns:
        str: The generated script, or None if an error occurs.
    """
    if not openai_client:
        print("OpenAI client not initialized. Skipping OpenAI generation.")
        return None
        
    try:
        print(f"Attempting script generation with OpenAI model: {model}")
        completion = openai_client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_message}
            ],
            temperature=0.7,
            max_tokens=1500 # Keep OpenAI max tokens as before
        )
        
        if completion.choices and completion.choices[0].message:
            generated_content = completion.choices[0].message.content
            print(f"OpenAI ({model}) generated {len(generated_content.split())} words.")
            return generated_content
        else:
            print(f"OpenAI ({model}) response did not contain expected content.")
            return None
            
    except Exception as e:
        print(f"Error generating script with OpenAI model {model}: {str(e)}")
        return None # Return None on error, fallback handled in main generator

def generate_script(prompt, 
                   subject="", 
                   length="medium", 
                   audience="general", 
                   tone="informative",
                   template="General",
                   context=""):
    """
    Generate an educational script using the best available LLM (DeepSeek primary, OpenAI fallback).
    
    Args:
        prompt (str): The main script generation prompt
        subject (str): Subject matter of the script
        length (str): Desired length - short, medium, long
        audience (str): Target audience - general, beginner, advanced, etc.
        tone (str): Tone of the script - informative, conversational, etc.
        template (str): Industry-specific template to use
        context (str): Additional context information
        
    Returns:
        str: The generated script or None if all models fail.
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
        if template == "Music Lesson":
            user_message = f"""
{prompt}

BACKGROUND KNOWLEDGE (Do not reference this directly in your script):
The student has the following background and capabilities. Use this information to tailor the content appropriately without explicitly mentioning what they already know or have learned:
{context}

Remember to build naturally on this background without phrases like "as you've learned before" or "now that you know X". Simply assume this knowledge is present and create a natural progression.
"""
        else:
            user_message = f"{prompt}\n\nAdditional context to incorporate:\n{context}"
    
    # --- Generation Logic --- 
    
    # 1. Try DeepSeek Primary Model
    print("--- Starting Script Generation --- ")
    script = generate_script_with_deepseek(system_message, user_message, model=DEEPSEEK_MODEL)
    if script:
        print("--- Script generated successfully with DeepSeek --- ")
        return script
        
    print("--- DeepSeek failed, attempting OpenAI fallback --- ")
    
    # 2. Try OpenAI Primary Model (configured in .env)
    script = generate_script_with_openai(system_message, user_message, model=OPENAI_MODEL)
    if script:
        print(f"--- Script generated successfully with OpenAI ({OPENAI_MODEL}) --- ")
        return script
        
    # 3. Try OpenAI Fallback Models
    print(f"--- OpenAI ({OPENAI_MODEL}) failed, attempting other OpenAI fallbacks --- ")
    for fallback_model in OPENAI_FALLBACK_MODELS:
        # Skip if it's the same as the primary OpenAI model we already tried
        if fallback_model == OPENAI_MODEL:
            continue 
            
        script = generate_script_with_openai(system_message, user_message, model=fallback_model)
        if script:
            print(f"--- Script generated successfully with OpenAI ({fallback_model}) --- ")
            return script
            
    # 4. If all models fail
    print("--- All models failed to generate the script. --- ")
    return None

def edit_script_with_openai(original_script, edit_instructions, context=""):
    """
    Edit a script using the OpenAI API.
    
    Args:
        original_script (str): The script to be edited.
        edit_instructions (str): Instructions on how to edit the script.
        context (str): Additional context to consider during editing.
        
    Returns:
        str: The edited script, or None if an error occurs.
    """
    if not openai_client:
        print("OpenAI client not initialized. Skipping OpenAI editing.")
        return None

    system_message = "You are an expert script editor. Modify the provided script based on the user's instructions. Maintain the original tone and style unless asked otherwise. Apply the edits precisely."    
    user_message = f"Original Script:\n{original_script}\n\nEdit Instructions:\n{edit_instructions}"
    if context:
        user_message += f"\n\nAdditional Context for Editing:\n{context}"
        
    try:
        # Use the primary OpenAI model for editing
        print(f"Attempting script editing with OpenAI model: {OPENAI_MODEL}")
        completion = openai_client.chat.completions.create(
            model=OPENAI_MODEL, 
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_message}
            ],
            temperature=0.5, # Lower temperature for more precise editing
            max_tokens=2000 # Allow ample tokens for potentially longer edited scripts
        )
        
        if completion.choices and completion.choices[0].message:
            edited_content = completion.choices[0].message.content
            print("Script edited successfully with OpenAI.")
            return edited_content
        else:
            print(f"OpenAI ({OPENAI_MODEL}) editing response did not contain expected content.")
            return None
            
    except Exception as e:
        print(f"Error editing script with OpenAI model {OPENAI_MODEL}: {str(e)}")
        # Consider adding fallback for editing if critical
        return None

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