from openai import OpenAI
from anthropic import Anthropic
from ..config import (
    DEEPSEEK_API_KEY, DEEPSEEK_MODEL,
    DEEPSEEK_BASE_URL,
    ANTHROPIC_API_KEY, CLAUDE_MODEL
)

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
    anthropic_client = Anthropic(api_key=ANTHROPIC_API_KEY)
else:
    anthropic_client = None
    print("Warning: ANTHROPIC_API_KEY not found. Claude functionality disabled.")

# --- Generation Helper Functions --- 

def _generate_with_openai_sdk(client_instance, system_message, user_message, model):
    """Helper to generate script using an OpenAI-compatible SDK client instance (like DeepSeek)."""
    if not client_instance:
        print(f"Client instance for model {model} not available. Skipping.")
        return None
        
    try:
        print(f"Attempting script generation with model: {model} via client: {getattr(client_instance, 'base_url', 'Unknown Base URL')}")
        completion = client_instance.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_message}
            ],
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
        # --- End Token Tracking ---
            
        if completion.choices and completion.choices[0].message:
            generated_content = completion.choices[0].message.content
            print(f"Model {model} generated {len(generated_content.split())} words.")
            # TODO: Store token usage data (prompt_tokens, completion_tokens) here later
            return generated_content
        else:
            print(f"Model {model} response did not contain expected content.")
            return None
            
    except Exception as e:
        print(f"Error generating script with OpenAI-SDK compatible model {model}: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

def _generate_with_claude(system_message, user_message, model=CLAUDE_MODEL):
    """Helper to generate script using the Anthropic Claude API."""
    if not anthropic_client:
        print(f"Anthropic client not available. Skipping Claude generation.")
        return None
        
    try:
        print(f"Attempting script generation with Claude model: {model}")
        message = anthropic_client.messages.create(
            model=model,
            system=system_message, 
            messages=[
                {"role": "user", "content": user_message}
            ],
            temperature=0.7,
            max_tokens=3000 
        )
        
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
        # --- End Token Tracking ---
            
        if message.content and isinstance(message.content, list) and message.content[0].text:
            generated_content = message.content[0].text
            print(f"Claude model {model} generated {len(generated_content.split())} words.")
            # TODO: Store token usage data (input_tokens, output_tokens) here later
            return generated_content
        else:
            print(f"Claude model {model} response did not contain expected content structure.")
            return None
            
    except Exception as e:
        print(f"Error generating script with Claude model {model}: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

# --- Main Generation Function --- 

def generate_script(prompt, 
                   subject="", 
                   length="medium", 
                   audience="general", 
                   tone="informative",
                   template="General",
                   context=""):
    """
    Generate an educational script using the best available LLM 
    (DeepSeek primary via OpenAI SDK, Claude fallback).
    
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
    
    # Prepare a system message
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
    
    # Prepare user message
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
    
    # --- Simplified Generation Logic --- 
    print("--- Starting Script Generation --- ")
    
    # 1. Try DeepSeek (via OpenAI SDK)
    if deepseek_client_via_openai_sdk:
        script = _generate_with_openai_sdk(deepseek_client_via_openai_sdk, system_message, user_message, model=DEEPSEEK_MODEL)
        if script:
            print("--- Script generated successfully with DeepSeek (via OpenAI SDK) --- ")
            return script
        else:
             print("--- DeepSeek (via OpenAI SDK) failed, attempting Claude fallback --- ")
    else:
        print("--- DeepSeek client not configured, attempting Claude fallback --- ")

    # 2. Try Claude Model
    if anthropic_client:
        script = _generate_with_claude(system_message, user_message, model=CLAUDE_MODEL)
        if script:
             print(f"--- Script generated successfully with Claude ({CLAUDE_MODEL}) --- ")
             return script
        else:
            print(f"--- Claude ({CLAUDE_MODEL}) also failed. --- ")
    else:
        print("--- Anthropic client not configured. Cannot fallback to Claude. --- ")
            
    # 3. If all configured models fail
    print("--- All configured models failed to generate the script. --- ")
    return None

# --- Editing Function (Now using Claude) --- 
def edit_script_with_claude(original_script, edit_instructions, context=""):
    """
    Edit a script using the Anthropic Claude API.
    
    Args:
        original_script (str): The script to be edited.
        edit_instructions (str): Instructions on how to edit the script.
        context (str): Additional context to consider during editing.
        
    Returns:
        str: The edited script, or None if an error occurs.
    """
    if not anthropic_client:
        print("Anthropic client not initialized. Skipping Claude editing.")
        return None

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
        # --- End Token Tracking ---
             
        if message.content and isinstance(message.content, list) and message.content[0].text:
            edited_content = message.content[0].text
            print("Script edited successfully with Claude.")
            # TODO: Store token usage data (input_tokens, output_tokens) here later
            return edited_content
        else:
            print(f"Claude ({CLAUDE_MODEL}) editing response did not contain expected content structure.")
            return None
            
    except Exception as e:
        print(f"Error editing script with Claude model {CLAUDE_MODEL}: {str(e)}")
        import traceback
        traceback.print_exc()
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