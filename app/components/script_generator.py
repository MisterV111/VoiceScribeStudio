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
                    placeholder="E.g., Create a script about the importance of sustainability",
                    lines=3
                )
                subject_input = gr.Textbox(
                    label="Subject",
                    placeholder="E.g., Environmental Science, Sustainable Practices, Conservation",
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
                
                # Add collapsible guide section
                with gr.Accordion("Additional Context Guide", open=False):
                    gr.Markdown("""
                    ### Parameter Quick Guide
                    
                    **Length**: Controls script word count
                    - **Short**: 150-250 words, brief overview
                    - **Medium**: 300-500 words, balanced detail
                    - **Long**: 600-900 words, comprehensive coverage
                    
                    **Target Audience**: Adapts complexity and examples
                    - **General**: Universal approach
                    - **Beginner/Children**: Simplified concepts, more explanation
                    - **Intermediate**: More detailed techniques
                    - **Advanced**: Specialized terminology and complex concepts
                    
                    **Tone**: Sets the voice and style
                    - **Informative**: Clear, fact-focused delivery
                    - **Conversational**: Casual, friendly dialogue
                    - **Professional**: Formal, authoritative approach
                    - **Friendly**: Warm, encouraging language
                    - **Enthusiastic**: Energetic, motivational style
                    
                    **Additional Context**: Provide background information that informs the script generation without being directly referenced. Include:
                    - Student's existing knowledge and skills
                    - Specific concepts to emphasize
                    - Learning goals or outcomes
                    - Time constraints or format requirements
                    """)
                    
                generate_btn = gr.Button("Generate Script", elem_classes=["primary"])
            
            with gr.Column():
                script_output = gr.Textbox(
                    label="Generated Script",
                    lines=20,
                    interactive=True,
                    elem_classes=["script-output-container"]
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
        def update_template_fields(template):
            if template == "Music Lesson":
                return [
                    gr.update(
                        placeholder="E.g., Explain chord progressions for beginners",
                        info="Focus on educational content about music theory, instrument techniques, or practice methods"
                    ),
                    gr.update(
                        placeholder="E.g., Music Theory, Piano Technique, Jazz Improvisation"
                    ),
                    gr.update(
                        placeholder="Include specific concepts to cover, instrument references, prerequisite knowledge, or teaching techniques to incorporate",
                        info="For music lessons, consider including: skill level assumptions, instrument specifics, related concepts, or musical examples to reference"
                    )
                ]
            elif template == "Corporate Training":
                return [
                    gr.update(
                        placeholder="E.g., Explain effective communication strategies for team leaders",
                        info="Focus on professional development, soft skills, or company procedures"
                    ),
                    gr.update(
                        placeholder="E.g., Leadership, Team Management, Communication Skills"
                    ),
                    gr.update(
                        placeholder="Include company-specific terminology, existing processes, skill gaps to address, or industry compliance requirements",
                        info="For corporate training, consider including: company culture context, specific workplace scenarios, industry challenges, or required competencies"
                    )
                ]
            elif template == "Marketing":
                return [
                    gr.update(
                        placeholder="E.g., Create a script highlighting our product's key features",
                        info="Focus on benefits, features, customer needs, and call-to-action elements"
                    ),
                    gr.update(
                        placeholder="E.g., Product Launch, Brand Awareness, Customer Testimonial"
                    ),
                    gr.update(
                        placeholder="Include product specifications, competitive advantages, target customer demographics, or brand voice guidelines",
                        info="For marketing, consider including: unique selling points, customer pain points, competitor comparisons, or specific metrics/claims to include"
                    )
                ]
            elif template == "General Education":
                return [
                    gr.update(
                        placeholder="E.g., Explain photosynthesis in a way that's easy to understand",
                        info="Focus on clear explanations of educational concepts for learning purposes"
                    ),
                    gr.update(
                        placeholder="E.g., Biology, Chemistry, Physics, History, Mathematics"
                    ),
                    gr.update(
                        placeholder="Include curriculum requirements, related concepts, visual aids to reference, or misconceptions to address",
                        info="For educational content, consider including: grade level context, specific learning objectives, key vocabulary to use, or supporting examples"
                    )
                ]
            elif template == "Technical Tutorial":
                return [
                    gr.update(
                        placeholder="E.g., Explain how to set up a development environment for Python",
                        info="Focus on step-by-step instructions, technical details, and best practices"
                    ),
                    gr.update(
                        placeholder="E.g., Software Development, Data Analysis, System Administration"
                    ),
                    gr.update(
                        placeholder="Include software versions, prerequisites, technical specifications, or common pitfalls to address",
                        info="For technical tutorials, consider including: environment details, dependency requirements, troubleshooting tips, or expected outcomes"
                    )
                ]
            else:  # General
                return [
                    gr.update(
                        placeholder="E.g., Create a script about the importance of sustainability",
                        info="General purpose script without industry-specific formatting"
                    ),
                    gr.update(
                        placeholder="E.g., Environmental Science, Sustainable Practices, Conservation"
                    ),
                    gr.update(
                        placeholder="Add specific details, concepts, or internal knowledge that should be incorporated into the script",
                        info="This helps generate more accurate and relevant content"
                    )
                ]
        
        # Update all fields based on selected template
        template_selector.change(
            fn=update_template_fields,
            inputs=[template_selector],
            outputs=[prompt_input, subject_input, context_input]
        )
        
        return script_output, script_file_output 