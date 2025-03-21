import gradio as gr
import os
from app.utils.openai_client import edit_script_with_openai

def edit_script(original_script, edit_instructions, context=""):
    """Edit a script using OpenAI"""
    try:
        if not original_script or not original_script.strip():
            return "Please provide a script to edit.", None
            
        if not edit_instructions or not edit_instructions.strip():
            return "Please provide instructions for editing.", None
        
        # Edit the script
        edited_script = edit_script_with_openai(original_script, edit_instructions, context)
        
        if not edited_script:
            return "Failed to edit script. Please try with different instructions.", None
        
        # Save the edited script to a file
        os.makedirs("output/scripts", exist_ok=True)
        timestamp = int(os.path.getmtime(__file__)) if os.path.exists(__file__) else 0
        script_file = f"output/scripts/edited_script_{timestamp}.txt"
        
        with open(script_file, "w") as f:
            f.write(edited_script)
            
        return edited_script, script_file
    except Exception as e:
        return f"Error editing script: {str(e)}", None

def create_script_editor_tab():
    with gr.TabItem("Edit Script"):
        with gr.Row():
            with gr.Column():
                edit_script_input = gr.Textbox(
                    label="Original Script",
                    placeholder="Paste your script here or generate one in the previous tab",
                    lines=10
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
                
                edit_btn = gr.Button("Edit Script", elem_classes=["primary"])
            
            with gr.Column():
                edited_script_output = gr.Textbox(
                    label="Edited Script",
                    lines=10,
                    interactive=True
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