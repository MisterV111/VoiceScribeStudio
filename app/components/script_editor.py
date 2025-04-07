import gradio as gr
import os
from app.utils.llm_clients import edit_script_with_claude
from app.utils.humanize_script import humanize_script

def edit_script(original_script, edit_instructions, context=""):
    """Edit a script using Claude"""
    try:
        if not original_script or not original_script.strip():
            return "Please provide a script to edit.", None
            
        if not edit_instructions or not edit_instructions.strip():
            return "Please provide instructions for editing.", None
        
        # Edit the script using Claude
        result = edit_script_with_claude(original_script, edit_instructions, context)
        
        # Handle the new dict return format
        if isinstance(result, dict) and "content" in result:
            edited_script = result["content"]
            # We could also use result["token_metrics"] here if needed
            model_used = result.get("model_used", "claude")
            
            # Add a small note about which model was used (optional)
            model_info = f"Edited with: {model_used}"
        else:
            # Handle legacy return format (just the script text)
            edited_script = result
            model_info = ""
        
        if not edited_script:
            return "Failed to edit script with Claude. Please check API key and try again.", None
        
        # Save the edited script to a file
        os.makedirs("output/scripts", exist_ok=True)
        timestamp = int(os.path.getmtime(__file__)) if os.path.exists(__file__) else 0
        script_file = f"output/scripts/edited_script_{timestamp}.txt"
        
        with open(script_file, "w") as f:
            f.write(edited_script)
            
            # Optionally add model info to the file
            if model_info:
                f.write(f"\n\n{model_info}")
            
        return edited_script, script_file
    except Exception as e:
        return f"Error editing script: {str(e)}", None

def apply_humanize(script_text):
    """
    Apply humanization to a script to optimize it for voiceover delivery
    
    Args:
        script_text (str): The script to humanize
        
    Returns:
        str: The humanized script with pause markers, emphasis, and emotions
    """
    if not script_text or not script_text.strip():
        return "Please provide a script to humanize."
    
    # Call the humanize_script function from app.utils.humanize_script
    result = humanize_script(script_text)
    
    # Check if humanization was successful
    if result.get("error"):
        return f"Error humanizing script: {result['error']}"
    
    # Return the humanized content
    return result["content"]

def create_script_editor_tab():
    with gr.TabItem("Edit Script"):
        with gr.Row():
            # Left column for input controls
            with gr.Column():
                edit_script_input = gr.Textbox(
                    label="Original Script",
                    placeholder="Paste your script here or generate one in the previous tab",
                    lines=12
                )
                edit_instructions = gr.Textbox(
                    label="Edit Instructions",
                    placeholder="Describe how you want to edit the script, e.g., Make it more conversational, Add a section about...",
                    lines=3
                )
                
                # Add context manager for editing
                with gr.Group():
                    gr.Markdown("### Additional Context")
                    edit_context_input = gr.Textbox(
                        label="Context Information",
                        placeholder="Add specific details, concepts, or knowledge that should be incorporated into the edited script",
                        lines=3,
                        info="This helps ensure edits align with your specific requirements"
                    )
                
                # Add buttons in a row - one for editing, one for humanizing
                with gr.Row():
                    edit_btn = gr.Button("Edit Script", elem_classes=["primary"])
                    humanize_btn = gr.Button("Humanize for Voiceover", variant="secondary")
            
            # Right column for output
            with gr.Column():
                edited_script_output = gr.Textbox(
                    label="Edited Script",
                    lines=20,
                    interactive=True,
                    elem_classes=["edited-script-output-container"]
                )
                edited_script_file = gr.Textbox(
                    label="Edited Script File",
                    visible=False
                )
                
                # Add Humanize Guide
                with gr.Accordion("Humanize Feature Guide", open=False):
                    gr.Markdown("""
                    ## 🎙️ Humanize Feature Guide
                    
                    The **Humanize** feature transforms your script into a format optimized for natural-sounding voiceovers by adding:
                    
                    ### Added Markup
                    
                    - **Pause Markers**: `<break time="1s" />` for natural pauses between sentences and sections
                    - **Emphasis**: `*important words*` to emphasize key terms
                    - **Emotion Tags**: `<cheerful>text</cheerful>` to indicate tone and emotion
                    
                    ### Benefits
                    
                    1. **More Natural Delivery**: Properly timed pauses for better comprehension
                    2. **Artifact Prevention**: Special handling to prevent audio glitches
                    3. **Professional Sound**: Book-style narration techniques for engaging delivery
                    4. **Better Emphasis**: Clear marking of important terms and concepts
                    
                    ### Usage
                    
                    1. Input or generate your script
                    2. Click the "Humanize for Voiceover" button
                    3. Review the transformed script with added markup
                    4. Use the output directly in the Voiceover tab
                    
                    The humanize process uses Claude 3.7 Sonnet to analyze your script and add professional
                    voiceover markup based on content, structure, and natural speech patterns.
                    """)
        
        # Connect the edit button to the edit_script function
        edit_btn.click(
            fn=edit_script,
            inputs=[edit_script_input, edit_instructions, edit_context_input],
            outputs=[edited_script_output, edited_script_file]
        )
        
        # Connect the humanize button to the apply_humanize function
        humanize_btn.click(
            fn=apply_humanize,
            inputs=[edited_script_output],
            outputs=[edited_script_output]
        )
        
        return edit_script_input, edited_script_output 