import gradio as gr
import os
from app.utils.elevenlabs_client import generate_voiceover, convert_mp3_to_ogg

# These will be set from main.py
preset_voice_names = []
preset_voice_ids = []
voice_names = []
voice_ids = []

def set_voice_data(p_names, p_ids, v_names, v_ids):
    """Set the voice data from main.py"""
    global preset_voice_names, preset_voice_ids, voice_names, voice_ids
    preset_voice_names = p_names
    preset_voice_ids = p_ids
    voice_names = v_names
    voice_ids = v_ids

def create_voiceover(script, voice_selection="Dan Teacher - Natural", custom_voice_id="", output_format="mp3",
                    stability=0.5, similarity=0.75, style=0.0, speed=1.0, speaker_boost=False):
    """Generate a voiceover from the script"""
    try:
        if not script or not script.strip():
            return "Please generate or provide a script first.", None, None
            
        # Determine which voice ID to use
        print(f"Voice selection: '{voice_selection}', Custom ID: '{custom_voice_id}'")
        
        if custom_voice_id and custom_voice_id.strip():
            # Use custom voice ID if provided
            voice_id = custom_voice_id.strip()
            print(f"Using custom voice ID: {voice_id}")
        elif voice_selection in preset_voice_names:
            # Use selected preset voice (with friendly name)
            index = preset_voice_names.index(voice_selection)
            voice_id = preset_voice_ids[index]
            print(f"Using preset voice: {voice_selection} (ID: {voice_id})")
        elif voice_selection in voice_names:
            # Use selected voice from ElevenLabs account
            index = voice_names.index(voice_selection)
            voice_id = voice_ids[index]
            print(f"Using account voice: {voice_selection} (ID: {voice_id})")
        else:
            # Default fallback - use first preset voice
            voice_id = preset_voice_ids[0] if preset_voice_ids else "default"
            print(f"Using default voice ID: {voice_id}")
        
        # Generate the voiceover
        timestamp = int(os.path.getmtime(__file__)) if os.path.exists(__file__) else 0
        output_path = f"output/audio/voiceover_{timestamp}.mp3"
        
        audio_data, mp3_path = generate_voiceover(
            script=script,
            voice_id=voice_id,
            output_path=output_path,
            stability=stability,
            similarity=similarity,
            style=style,
            speed=speed,
            use_speaker_boost=speaker_boost
        )
        
        if not audio_data:
            return f"Failed to generate voiceover with voice: {voice_selection}. Please check your API key and try again.", None, None
            
        # Convert to OGG if requested
        if output_format.lower() == "ogg":
            ogg_path = mp3_path.replace(".mp3", ".ogg")
            _, ogg_file = convert_mp3_to_ogg(mp3_path, ogg_path)
            return "Voiceover generated successfully!", mp3_path, ogg_file
            
        return "Voiceover generated successfully!", mp3_path, None
    except Exception as e:
        return f"Error generating voiceover: {str(e)}", None, None

def create_voiceover_tab():
    with gr.TabItem("Generate Voiceover"):
        with gr.Row():
            # Left column - Script input and basic controls
            with gr.Column(scale=1):
                # Add script formatting guide at the top
                with gr.Row():
                    gr.Markdown("### Script Formatting")
                    format_guide_btn = gr.Button("📖 Guide", elem_id="format-guide-btn", size="sm")
                
                # Help section for script formatting
                with gr.Accordion("Script Formatting Guide", open=False, visible=False) as format_help:
                    gr.Markdown("""
                    ## Script Formatting Guide
                    
                    ### 1. Pauses and Timing
                    Use these commands to control the timing and flow of your voiceover:
                    ```
                    <break time="0.5s" />   - Add a half-second pause
                    <break time="1s" />     - Add a 1-second pause
                    <break time="1.5s" />   - Add a 1.5-second pause
                    <break time="2s" />     - Add a 2-second pause
                    <break time="3s" />     - Add a 3-second pause
                    ...                     - Natural hesitation
                    —                       - Brief pause (em dash)
                    ```
                    
                    ### 2. Emphasis and Emotion
                    Control the delivery through natural writing:
                    ```
                    - Use exclamation marks (!) for excitement
                    - Use question marks (?) for inquiry
                    - CAPITALIZE words for emphasis
                    - Use ellipsis (...) for thoughtful pauses
                    ```
                    
                    ### Example Script:
                    ```
                    Welcome to today's music lesson!
                    <break time="1s" />
                    Today we'll learn about chord progressions...
                    <break time="0.5s" />
                    Let me demonstrate this IMPORTANT concept.
                    <break time="2s" />
                    Listen carefully to these chords...
                    <break time="3s" />
                    Isn't that beautiful?
                    <break time="1.5s" />
                    Let's continue with the next example.
                    ```
                    
                    ### Tips:
                    - Use breaks sparingly (too many can cause instability)
                    - Keep pauses consistent and natural
                    - Test small sections first
                    - Combine with voice settings for best results
                    - Adjust stability and style settings to fine-tune delivery
                    """)
                
                voiceover_script = gr.Textbox(
                    label="Script for Voiceover",
                    placeholder="Paste your script here or generate one in the previous tabs. Use the formatting guide above for controlling pauses and delivery.",
                    lines=10
                )
                
                # Voice selection section with visual separation
                with gr.Group():
                    gr.Markdown("### Voice Selection")
                    
                    voice_type = gr.Radio(
                        label="Voice Selection Method",
                        choices=["Preset Voices", "Custom Voice ID"],
                        value="Preset Voices"
                    )
                    
                    # Preset voices selection
                    with gr.Group(visible=True) as preset_group:
                        preset_voice_selector = gr.Dropdown(
                            label="Select Voice",
                            choices=preset_voice_names,
                            value=preset_voice_names[0] if preset_voice_names else None,
                            info="These voices will work with a valid ElevenLabs API key"
                        )
                    
                    # Custom voice ID input
                    with gr.Group(visible=False) as custom_group:
                        custom_voice_id_input = gr.Textbox(
                            label="ElevenLabs Voice ID",
                            placeholder="e.g., 21m00Tcm4TlvDq8ikWAM",
                            info="Find voice IDs in your ElevenLabs account dashboard"
                        )
                        
                        # Add information about where to find voice IDs in a collapsible section
                        with gr.Accordion("How to find voice IDs", open=False):
                            gr.Markdown("""
                            1. Go to [ElevenLabs Voice Library](https://elevenlabs.io/voice-library) or "My voices"
                            2. Find the voice you want to use and click on view 
                            3. **Important:** The voice must be added to your personal voice collection first to work with the API
                            4. Click the "ID" button to copy the ID (at the bottom of the view window)
                            5. Paste it in the field above
                            """)
                
                # Audio format in a separate group
                with gr.Group():
                    gr.Markdown("### Audio Settings")
                    format_selector = gr.Dropdown(
                        label="Audio Format",
                        choices=["MP3", "OGG"],
                        value="MP3",
                        info="OGG format provides better compression"
                    )
                
                # Add some spacing before the button
                gr.Markdown("")
                voiceover_btn = gr.Button("Generate Voiceover", size="lg")
            
            # Right column - Output and voice settings
            with gr.Column(scale=1):
                # Status and output
                voiceover_status = gr.Textbox(
                    label="Status",
                    value="Input a script > select a voice > select the audio format > generate voiceover."
                )
                
                with gr.Group():
                    gr.Markdown("### Voiceover Output")
                    mp3_output = gr.Audio(
                        label="Voiceover (MP3)", 
                        type="filepath"
                    )
                    ogg_output = gr.Audio(
                        label="Voiceover (OGG)", 
                        type="filepath", 
                        visible=False
                    )
                
                # Voice Settings in a group with better visual structure
                with gr.Group():
                    with gr.Row():
                        gr.Markdown("### Voice Settings")
                        # Guide button in top right
                        guide_btn = gr.Button("Guide", elem_id="guide-btn", size="sm")
                    
                    # Help popup for voice settings
                    with gr.Accordion("Voice Settings Guide", open=False, visible=False) as settings_help:
                        gr.Markdown("""
                        ## Voice Settings Guide
                        
                        **Stability (0.0-1.0)**
                        - **Low values (0.0-0.3)**: More emotional variety, spontaneous, but can sound random
                        - **Medium values (0.4-0.6)**: Balanced expressiveness and consistency
                        - **High values (0.7-1.0)**: Very consistent, stable delivery but less emotional range
                        - **Recommended**: Start with 0.5 for most uses
                        
                        **Similarity (0.0-1.0)**
                        - Controls how closely the output matches the original voice
                        - **Low values**: More variation from original voice
                        - **High values**: Closer to the original voice
                        - **Note**: Values above 0.75 may reproduce artifacts in low-quality voices
                        - **Recommended**: 0.75 for most uses
                        
                        **Speed (0.7-1.2)**
                        - Adjusts speaking rate of the voice
                        - **Values closer to 0.7**: Slower speech
                        - **Values closer to 1.2**: Faster speech
                        - **Note**: ElevenLabs API only allows speeds between 0.7 and 1.2
                        - **Recommended**: 1.0 (normal speed)
                        
                        **Style Exaggeration (0.0-1.0)**
                        - Amplifies the distinctive character of the voice
                        - Higher values emphasize the voice's unique style but may reduce stability
                        - **Recommended**: 0.0 for most uses (increases processing time if higher)
                        
                        **Speaker Boost**
                        - Enhances clarity and similarity to the original speaker
                        - Useful for voices with multiple speakers to emphasize the main speaker
                        - Slightly increases processing time
                        - **Recommended**: Off for most single-speaker content
                        
                        **Best Practice Combinations:**
                        - **Audiobooks**: Stability 0.5, Similarity 0.75, Speed 1.0, Style 0.0
                        - **Conversational**: Stability 0.3, Similarity 0.6, Speed 1.0, Style 0.2
                        - **Narration**: Stability 0.7, Similarity 0.8, Speed 0.9, Style 0.0
                        """)
                    
                    # Two columns for the sliders
                    with gr.Row():
                        # Left column of sliders
                        with gr.Column():
                            stability_slider = gr.Slider(
                                label="Stability",
                                minimum=0.0,
                                maximum=1.0,
                                value=0.5,
                                step=0.01,
                                info="Higher values make voice more consistent but less expressive"
                            )
                            similarity_slider = gr.Slider(
                                label="Similarity",
                                minimum=0.0,
                                maximum=1.0,
                                value=0.75,
                                step=0.01,
                                info="Higher values make voice more similar to the original"
                            )
                        
                        # Right column of sliders
                        with gr.Column():
                            speed_slider = gr.Slider(
                                label="Speed",
                                minimum=0.7,
                                maximum=1.2,
                                value=1.0,
                                step=0.01,
                                info="Adjust speaking speed (0.7=slower, 1.2=faster)"
                            )
                            style_slider = gr.Slider(
                                label="Style Exaggeration",
                                minimum=0.0,
                                maximum=1.0,
                                value=0.0,
                                step=0.01,
                                info="Increase to enhance the unique character of the voice"
                            )
                    
                    # Speaker boost option
                    speaker_boost = gr.Checkbox(
                        label="Speaker Boost",
                        value=False,
                        info="Emphasize the main speaker in a recording"
                    )
                    
                    # Reset button at bottom right
                    with gr.Row():
                        with gr.Column():
                            # Empty column for spacing
                            gr.Markdown("")
                        with gr.Column():
                            reset_btn = gr.Button("Reset Voice Settings", size="sm")
        
        # Function definitions for interactivity
        
        # Function to toggle help visibility
        def toggle_guide():
            return gr.update(visible=not settings_help.visible, open=True)
        
        # Connect guide button to toggle function
        guide_btn.click(
            fn=toggle_guide,
            inputs=[],
            outputs=[settings_help]
        )
        
        # Toggle between preset and custom voice input
        def toggle_voice_input(voice_type):
            if voice_type == "Preset Voices":
                return gr.update(visible=True), gr.update(visible=False)
            else:
                return gr.update(visible=False), gr.update(visible=True)
        
        voice_type.change(
            fn=toggle_voice_input,
            inputs=[voice_type],
            outputs=[preset_group, custom_group]
        )
        
        # Function to reset voice settings
        def reset_voice_settings():
            return gr.update(value=0.5), gr.update(value=0.75), gr.update(value=0.0), gr.update(value=1.0), gr.update(value=False)
        
        # Connect reset button to reset function
        reset_btn.click(
            fn=reset_voice_settings,
            inputs=[],
            outputs=[stability_slider, similarity_slider, style_slider, speed_slider, speaker_boost]
        )
        
        # Connect the voiceover button to the create_voiceover function
        voiceover_btn.click(
            fn=create_voiceover,
            inputs=[
                voiceover_script, 
                preset_voice_selector, 
                custom_voice_id_input, 
                format_selector,
                stability_slider,
                similarity_slider,
                style_slider,
                speed_slider,
                speaker_boost
            ],
            outputs=[voiceover_status, mp3_output, ogg_output]
        )
        
        # Show/hide OGG output based on format selection
        def update_format_visibility(fmt):
            is_ogg = fmt.lower() == "ogg"
            return gr.update(visible=is_ogg), gr.update(visible=not is_ogg)
        
        format_selector.change(
            fn=update_format_visibility,
            inputs=[format_selector],
            outputs=[ogg_output, mp3_output]
        )
        
        # Add function to toggle format guide visibility
        def toggle_format_guide():
            return gr.update(visible=not format_help.visible)
        
        # Connect the format guide button
        format_guide_btn.click(
            fn=toggle_format_guide,
            inputs=[],
            outputs=[format_help]
        )
        
        return voiceover_script, voiceover_status, mp3_output, ogg_output 