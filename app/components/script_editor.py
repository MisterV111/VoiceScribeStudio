import gradio as gr
import os
from app.utils.llm_clients import edit_script_with_claude

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
                
                # Add spacer to push button to bottom
                with gr.Row():
                    edit_btn = gr.Button("Edit Script", elem_classes=["primary"])
            
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
        
        # Connect the edit button to the edit_script function
        edit_btn.click(
            fn=edit_script,
            inputs=[edit_script_input, edit_instructions, edit_context_input],
            outputs=[edited_script_output, edited_script_file]
        )
        
        return edit_script_input, edited_script_output 