import gradio as gr
import os
from app.utils.openai_client import generate_script_with_openai

def create_script(prompt, subject, length, audience, tone, template="General", context=""):
    """Generate a script using OpenAI"""
    try:
        if not prompt or not prompt.strip():
            return "Please provide a prompt for script generation.", None
        
        # Generate the script
        script = generate_script_with_openai(
            prompt=prompt, 
            subject=subject, 
            length=length, 
            audience=audience, 
            tone=tone,
            template=template,
            context=context
        )
        
        if not script:
            return "Failed to generate script. Please try again with a different prompt.", None
        
        # Save the script to a file
        os.makedirs("output/scripts", exist_ok=True)
        timestamp = int(os.path.getmtime(__file__)) if os.path.exists(__file__) else 0
        script_file = f"output/scripts/script_{timestamp}.txt"
        
        with open(script_file, "w") as f:
            f.write(script)
        
        return script, script_file
    except Exception as e:
        return f"Error generating script: {str(e)}", None

def create_script_generator_tab():
    with gr.TabItem("Generate Script"):
        with gr.Row():
            with gr.Column():
                # Add industry-specific template selector
                template_selector = gr.Dropdown(
                    label="Script Template",
                    choices=[
                        "Music Lesson",
                        "Corporate Training",
                        "Marketing",
                        "General Education",
                        "Technical Tutorial",
                        "General"
                    ],
                    value="General",
                    info="Select an industry-specific template to guide script generation"
                )
                
                prompt_input = gr.Textbox(
                    label="What is your script about?",
                    placeholder="E.g., Explain chord progressions for beginners",
                    lines=3
                )
                subject_input = gr.Textbox(
                    label="Subject",
                    placeholder="E.g., Music Theory, Piano Technique, Jazz Improvisation",
                )
                
                # Add context manager
                with gr.Group():
                    gr.Markdown("### Additional Context")
                    context_input = gr.Textbox(
                        label="Context Information",
                        placeholder="Add specific details, concepts, or internal knowledge that should be incorporated into the script",
                        lines=3,
                        info="This helps generate more accurate and relevant content"
                    )
                
                with gr.Row():
                    length_input = gr.Dropdown(
                        label="Length",
                        choices=["short", "medium", "long"],
                        value="medium"
                    )
                    audience_input = gr.Dropdown(
                        label="Target Audience",
                        choices=["general", "beginner", "intermediate", "advanced", "children"],
                        value="general"
                    )
                    tone_input = gr.Dropdown(
                        label="Tone",
                        choices=["informative", "conversational", "professional", "friendly", "enthusiastic"],
                        value="informative"
                    )
                generate_btn = gr.Button("Generate Script")
            
            with gr.Column():
                script_output = gr.Textbox(
                    label="Generated Script",
                    lines=12,
                    interactive=True
                )
                script_file_output = gr.Textbox(
                    label="Script File",
                    visible=False
                )
                
        # Connect the generate button to the create_script function
        generate_btn.click(
            fn=create_script,
            inputs=[
                prompt_input, 
                subject_input, 
                length_input, 
                audience_input, 
                tone_input,
                template_selector,
                context_input
            ],
            outputs=[script_output, script_file_output]
        )
        
        # Display template-specific guidance when template is selected
        def update_template_guidance(template):
            if template == "Music Lesson":
                return gr.update(
                    placeholder="E.g., Explain chord progressions for beginners",
                    info="Focus on educational content about music theory, instrument techniques, or practice methods"
                )
            elif template == "Corporate Training":
                return gr.update(
                    placeholder="E.g., Explain effective communication strategies for team leaders",
                    info="Focus on professional development, soft skills, or company procedures"
                )
            elif template == "Marketing":
                return gr.update(
                    placeholder="E.g., Create a script highlighting our product's key features",
                    info="Focus on benefits, features, customer needs, and call-to-action elements"
                )
            elif template == "General Education":
                return gr.update(
                    placeholder="E.g., Explain photosynthesis in a way that's easy to understand",
                    info="Focus on clear explanations of educational concepts for learning purposes"
                )
            elif template == "Technical Tutorial":
                return gr.update(
                    placeholder="E.g., Explain how to set up a development environment for Python",
                    info="Focus on step-by-step instructions, technical details, and best practices"
                )
            else:  # General
                return gr.update(
                    placeholder="E.g., Create a script about the importance of sustainability",
                    info="General purpose script without industry-specific formatting"
                )
        
        # Update placeholder and info based on selected template
        template_selector.change(
            fn=update_template_guidance,
            inputs=[template_selector],
            outputs=[prompt_input]
        )
        
        return script_output, script_file_output 