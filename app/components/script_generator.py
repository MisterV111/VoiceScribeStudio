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
                    guide_markdown = gr.Markdown("""
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
                    - Relevant background knowledge
                    - Specific concepts to emphasize
                    - Goals or outcomes
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
                    ),
                    gr.update(value="""
                    ### Music Lesson Parameter Guide
                    
                    **Length**: Determines demonstration complexity
                    - **Short**: 1-2 minute lesson, focus on a single technique
                    - **Medium**: 3-5 minute lesson, covers technique with examples
                    - **Long**: 5-8 minute lesson, includes theory, practice and application
                    
                    **Target Audience**: Adjusts terminology and pace
                    - **Beginner/Children**: Very simple terms, more hand position guidance
                    - **Intermediate**: Introduces music theory concepts
                    - **Advanced**: Uses proper musical terminology, complex techniques
                    
                    **Tone**: Sets instructional approach
                    - **Informative**: Clear, methodical explanation of technique
                    - **Conversational**: Friendly, casual teaching style
                    - **Enthusiastic**: Motivational, energetic instruction
                    
                    **Additional Context**: For music lessons, include:
                    - Student's existing skills (chords, scales they know)
                    - Specific instruments and equipment available
                    - Related songs/repertoire to reference
                    - Prior lessons or techniques to build upon
                    """)
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
                    ),
                    gr.update(value="""
                    ### Corporate Training Parameter Guide
                    
                    **Length**: Controls training session duration
                    - **Short**: 5-10 minute briefing or quick update
                    - **Medium**: 15-25 minute focused training module
                    - **Long**: 30-45 minute comprehensive training session
                    
                    **Target Audience**: Adapts content to organizational roles
                    - **General**: All-staff appropriate material
                    - **Beginner**: New employee onboarding content
                    - **Intermediate**: Department-specific training
                    - **Advanced**: Management or specialist-level material
                    
                    **Tone**: Sets professional environment
                    - **Informative**: Direct, data-driven approach
                    - **Professional**: Formal, authoritative instruction
                    - **Conversational**: Collaborative, workshop-style approach
                    
                    **Additional Context**: For corporate training, include:
                    - Company policies or procedures relevant to the topic
                    - Industry regulations or compliance requirements
                    - Specific workplace scenarios to address
                    - Organizational hierarchy considerations
                    """)
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
                    ),
                    gr.update(value="""
                    ### Marketing Parameter Guide
                    
                    **Length**: Adapts to marketing format
                    - **Short**: 30-second ad or social media post
                    - **Medium**: 1-2 minute promotional video
                    - **Long**: 3-5 minute detailed product presentation
                    
                    **Target Audience**: Tailors to customer segments
                    - **General**: Broad market appeal
                    - **Beginner**: New customers, simple explanations
                    - **Intermediate**: Returning customers, more features
                    - **Advanced**: Industry professionals, technical details
                    
                    **Tone**: Sets brand personality
                    - **Conversational**: Relatable, customer-focused approach
                    - **Professional**: Industry authority positioning
                    - **Enthusiastic**: High-energy, promotional style
                    - **Friendly**: Approachable, solution-oriented
                    
                    **Additional Context**: For marketing, include:
                    - Key product specifications and pricing
                    - Unique selling propositions vs competitors
                    - Target demographics and customer pain points
                    - Campaign goals and desired call-to-action
                    """)
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
                    ),
                    gr.update(value="""
                    ### Educational Content Parameter Guide
                    
                    **Length**: Adapts to lesson format
                    - **Short**: 3-5 minute concept introduction
                    - **Medium**: 8-12 minute lesson segment
                    - **Long**: 15-20 minute complete lesson
                    
                    **Target Audience**: Adjusts to educational level
                    - **Children**: Elementary/primary school level
                    - **Beginner**: Secondary/high school basics
                    - **Intermediate**: Advanced high school/early college
                    - **Advanced**: College/university level content
                    
                    **Tone**: Sets instructional approach
                    - **Informative**: Clear, factual presentation
                    - **Conversational**: Engaging, dialogue-style teaching
                    - **Enthusiastic**: Dynamic, curiosity-building approach
                    
                    **Additional Context**: For educational content, include:
                    - Curriculum standards or learning objectives
                    - Prior knowledge students should have
                    - Common misconceptions to address
                    - Visual aids or demonstrations available
                    """)
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
                    ),
                    gr.update(value="""
                    ### Technical Tutorial Parameter Guide
                    
                    **Length**: Controls tutorial depth
                    - **Short**: Quick tip or single feature overview
                    - **Medium**: Focused walkthrough of one concept
                    - **Long**: Comprehensive implementation guide
                    
                    **Target Audience**: Adjusts technical complexity
                    - **Beginner**: New to the technology, needs basics
                    - **Intermediate**: Familiar but needs detailed steps
                    - **Advanced**: Experienced users needing optimization
                    
                    **Tone**: Sets instructional style
                    - **Informative**: Clear, precise technical instructions
                    - **Professional**: Industry standard approaches
                    - **Conversational**: Accessible technical guidance
                    
                    **Additional Context**: For technical tutorials, include:
                    - Software versions and dependencies
                    - System requirements or constraints
                    - Prerequisites or required knowledge
                    - Common errors and troubleshooting tips
                    """)
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
                    ),
                    gr.update(value="""
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
                    - Relevant background knowledge
                    - Specific concepts to emphasize
                    - Goals or outcomes
                    - Time constraints or format requirements
                    """)
                ]
        
        # Update all fields based on selected template
        template_selector.change(
            fn=update_template_fields,
            inputs=[template_selector],
            outputs=[prompt_input, subject_input, context_input, guide_markdown]
        )
        
        return script_output, script_file_output 