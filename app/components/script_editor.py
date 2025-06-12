import gradio as gr
import os
from app.utils.llm_clients import edit_script_with_claude
from app.utils.humanize_script import humanize_script, preview_humanized_markup

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

def humanize_script_handler(script_text):
    """Handle the humanize button click"""
    try:
        if not script_text or not script_text.strip() or "Please provide a script" in script_text:
            # Return an error message
            return "Please provide a script to humanize.", None, gr.update(visible=False)
        
        print(f"Humanizing script with {len(script_text)} characters...")
        
        # Call the humanize_script function
        result = humanize_script(script_text)
        
        if "error" in result and result["error"]:
            error_message = result["error"]
            print(f"Error humanizing script: {error_message}")
            return f"Error humanizing script: {error_message}", None, gr.update(visible=False)
        
        humanized_script = result.get("content", "")
        
        if not humanized_script or humanized_script.strip() == "":
            print("Warning: Humanized script is empty")
            return "Error: Humanized script is empty. Please try again.", None, gr.update(visible=False)
            
        # Log success with token metrics
        token_metrics = result.get("token_metrics", {})
        if token_metrics:
            total_tokens = token_metrics.get("total_tokens", 0)
            print(f"Successfully humanized script using {total_tokens} tokens")
        
        # Save the humanized script to a file
        os.makedirs("output/scripts", exist_ok=True)
        timestamp = int(os.path.getmtime(__file__)) if os.path.exists(__file__) else 0
        script_file = f"output/scripts/humanized_script_{timestamp}.txt"
        
        try:
            with open(script_file, "w") as f:
                f.write(humanized_script)
            print(f"Saved humanized script to {script_file}")
        except Exception as file_err:
            print(f"Warning: Could not save humanized script to file: {str(file_err)}")
            # Continue even if file save fails
        
        # Create a preview HTML showing the differences
        try:
            preview_html = preview_humanized_markup(script_text, humanized_script)
        except Exception as preview_err:
            print(f"Warning: Error creating preview: {str(preview_err)}")
            preview_html = f"<div style='color:red'>Error creating preview: {str(preview_err)}</div>"
        
        return humanized_script, script_file, gr.update(visible=True, value=preview_html)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return f"Error humanizing script: {str(e)}", None, gr.update(visible=False)

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
                
                # Add buttons with spacing between them
                with gr.Row():
                    edit_btn = gr.Button("Edit Script", elem_classes=["primary"])
                
                # Add the Humanize button with explanation
                with gr.Group():
                    gr.Markdown("### Prepare for Voiceover")
                    gr.Markdown(
                        "Optimize your script for voiceover by adding professional pause markers, emphasis, and intonation guidance.",
                        elem_classes=["humanize-description"]
                    )
                    humanize_btn = gr.Button("Humanize Script", variant="secondary", elem_classes=["humanize-button"])
            
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
                
                # Add a preview area for humanize changes
                preview_area = gr.HTML(
                    label="Humanize Preview",
                    visible=False
                )
        
        # Connect the edit button to the edit_script function
        edit_btn.click(
            fn=edit_script,
            inputs=[edit_script_input, edit_instructions, edit_context_input],
            outputs=[edited_script_output, edited_script_file]
        )
        
        # Connect the humanize button to the humanize_script_handler function
        # MODIFY THIS CONNECTION TO USE EITHER ORIGINAL OR EDITED SCRIPT
        def handle_humanize_click(original_script, edited_script):
            # Use edited script if it's not empty and doesn't contain error messages
            if (edited_script and edited_script.strip() and 
                "Please provide a script" not in edited_script):
                script_to_use = edited_script
            else:
                # Fall back to original script
                script_to_use = original_script
                
            # If both are empty, return an error
            if not script_to_use or not script_to_use.strip():
                return "Please provide a script to humanize.", None, gr.update(visible=False)
                
            # Call the handler with the selected script
            return humanize_script_handler(script_to_use)
            
        humanize_btn.click(
            fn=handle_humanize_click,
            inputs=[edit_script_input, edited_script_output],  # Now using both script inputs
            outputs=[edited_script_output, edited_script_file, preview_area]
        )
        return edit_script_input, edited_script_output
        # Connect the humanize button to the humanize_script_handler function
        # MODIFY THIS CONNECTION TO USE EITHER ORIGINAL OR EDITED SCRIPT
        def handle_humanize_click(original_script, edited_script):
            # Use edited script if it's not empty and doesn't contain error messages
            if (edited_script and edited_script.strip() and 
                "Please provide a script" not in edited_script):
                script_to_use = edited_script
            else:
                # Fall back to original script
                script_to_use = original_script
                
            # If both are empty, return an error
            if not script_to_use or not script_to_use.strip():
                return "Please provide a script to humanize.", None, gr.update(visible=False)
                
            # Call the handler with the selected script
            return humanize_script_handler(script_to_use)
            
        humanize_btn.click(
            fn=handle_humanize_click,
            inputs=[edit_script_input, edited_script_output],  # Now using both script inputs
            outputs=[edited_script_output, edited_script_file, preview_area]
        )
        edit_btn.click(
            fn=edit_script,
            inputs=[edit_script_input, edit_instructions, edit_context_input],
            outputs=[edited_script_output, edited_script_file]
        )
        
        return edit_script_input, edited_script_output
        # Connect the humanize button to the humanize_script_handler function
        # MODIFY THIS CONNECTION TO USE EITHER ORIGINAL OR EDITED SCRIPT
        def handle_humanize_click(original_script, edited_script):
            # Use edited script if it's not empty and doesn't contain error messages
            if (edited_script and edited_script.strip() and 
                "Please provide a script" not in edited_script):
                script_to_use = edited_script
            else:
                # Fall back to original script
                script_to_use = original_script
                
            # If both are empty, return an error
            if not script_to_use or not script_to_use.strip():
                return "Please provide a script to humanize.", None, gr.update(visible=False)
                
            # Call the handler with the selected script
            return humanize_script_handler(script_to_use)
            
        humanize_btn.click(
            fn=handle_humanize_click,
            inputs=[edit_script_input, edited_script_output],  # Now using both script inputs
            outputs=[edited_script_output, edited_script_file, preview_area]
        )
        
        return edit_script_input, edited_script_output 