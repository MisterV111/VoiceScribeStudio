# Active Context

## Current Focus

The project is currently moving from Phase 2 to Phase 3, focusing on the following aspects:

1. **Translation Feature Implementation (Phase 3)**: Building a context-aware translation system using Claude 3.7 Sonnet with template-specific glossaries.

2. **Testing Infrastructure Optimization**: Enhancing the testing dashboard and integrating token tracking metrics to improve test coverage and resource monitoring.

## Recent Changes

1. **Token Tracking Integration with Testing**: The testing framework is now fully integrated with the token tracking system, allowing for:
   - Test-specific token usage tracking (via `is_test=True` flag)
   - Token usage estimation before running tests
   - Separation of test and production usage in analytics
   - Detailed tracking of token metrics by template in test results

2. **Script Humanization Enhancements**: Improved the script humanization process for better voiceover delivery with robust error handling.

3. **Voice Loading Mechanism Consolidation**: Resolved the conflicting voice loading logic by implementing a consolidated solution:
   - Created a centralized `load_all_voices()` function in `app/utils/elevenlabs_client.py` that serves as the single source of truth
   - Implemented a hybrid approach that prioritizes hardcoded preset voices for reliability while also attempting to fetch additional voices from the API
   - Used a timeout mechanism with threading to prevent startup delays when the API is slow or unavailable
   - Maintained backward compatibility by adding an alias in `tts_clients.py`
   - Updated `main.py` to use the consolidated function, eliminating redundancy and clarifying the data flow
   - Ensured Dan Teacher voices remain at the top of the voice list

## Translation Implementation Plan

The Translation Feature (Phase 3) is currently in development with a detailed implementation plan:

1. **Architecture Design** (2 weeks):
   - Creating a `TranslationService` module in the Content Processing Layer
   - Designing Claude 3.7 Sonnet prompts for context-aware translation
   - Implementing template-specific glossary structure (JSON format)
   - Developing UI components in the Script Editor tab

2. **Core Translation Functionality** (3 weeks):
   - Context-aware prompt construction
   - Glossary system with template-specific terminology
   - Claude 3.7 integration with error handling

3. **Template-Specific Enhancements** (2 weeks):
   - Automatic template detection
   - Contextual element extraction
   - Developing initial glossaries for high-priority templates

4. **UI Implementation and User Experience** (2 weeks):
   - Language selector
   - Translation button with loading states
   - Result display with comparison options

5. **Testing and Optimization** (2 weeks)
6. **Cost Management and Production Deployment** (1 week)

The feature will support nine target languages (French, Spanish, German, Italian, Portuguese, Russian, Japanese, Korean, Chinese) and use a template-specific glossary system to ensure accurate translation of specialized terminology.

Estimated cost per average translation: $0.045 ($0.0075 input + $0.0375 output) with projected monthly costs ranging from $4.50 (100 translations) to $45.00 (1,000 translations).

## Translation Implementation Plan Details

Based on the detailed implementation plan in `docs/TRANSLATION_IMPLEMENTATION_PLAN.md`, the Translation Feature (Phase 3) includes the following key components:

### Technical Approach
- **Translation Processing Architecture**:
  - User-facing components: Language selection dropdown, "Translate" button with loading indicator, result display area
  - Backend processing flow: Template detection, glossary retrieval, context-aware prompt construction, Claude 3.7 processing
  - Glossary management system: Template-specific terminology databases in JSON format

### Prompt Strategy
The translation system uses carefully crafted prompts that include:
1. Role definition (expert translator in the specific domain)
2. Task specification (clear translation instructions)
3. Context provision (template type and intended audience)
4. Terminology guidance (template-specific glossary terms)
5. Format instructions (maintaining formatting, structure, and tone)

### Implementation Code Examples
- **Prompt Construction**:
  ```python
  def build_translation_prompt(script_text, template_type, source_lang, target_lang, glossary_terms):
      prompt = f"""You are an expert translator specializing in {template_type} content.
      Translate the following script from {source_lang} to {target_lang}.
      Pay special attention to technical terminology.
      
      Use these specific translations for technical terms:
      {format_glossary_terms(glossary_terms)}
      
      Script to translate:
      {script_text}
      """
      return prompt
  ```

- **Glossary System**:
  ```python
  def get_glossary_terms(template_type, target_language):
      # Load appropriate glossary based on template and language
      return glossary_terms
  ```

### Glossary Structure Example
```json
{
  "music_lesson": {
    "spanish": {
      "quarter note": "negra",
      "treble clef": "clave de sol",
      "time signature": "indicación de compás"
    },
    "french": {
      "quarter note": "noire",
      "treble clef": "clé de sol",
      "time signature": "chiffrage de mesure"
    }
  }
}
```

### Cost Analysis
- **Token Usage per Translation**:
  - Average input size: 2,500 tokens (script + prompt with glossary)
  - Average output size: 2,500 tokens (translated script)
  - Cost per translation: $0.045 ($0.0075 input + $0.0375 output)
- **Projected Monthly Costs**:
  - Basic usage (100 translations/month): $4.50
  - Medium usage (500 translations/month): $22.50
  - Heavy usage (1,000 translations/month): $45.00

### Success Metrics
- Translation quality: Manual review scores of 4+ on 5-point scale
- User satisfaction: >85% positive feedback
- Performance: Translation completion in <5 seconds for typical scripts
- Token efficiency: <10% token wastage in prompts
- Error rate: <2% failed translations

### Future Enhancements
1. Additional languages beyond the initial nine
2. Dialect options (e.g., European vs. Latin American Spanish)
3. Bidirectional translation (from non-English sources)
4. Style preservation enhancements
5. Translation memory system for reusing previous translations

This plan provides a comprehensive roadmap for implementing the translation feature, with clear technical details, cost projections, and success metrics.

## Next Steps

1. **Continue Translation Feature Implementation**: Follow the phased plan with focus on the architecture design and glossary system first.

2. **Update Testing Framework**: Enhance validation criteria beyond basic template markers and implement more sophisticated content quality metrics.

3. **Token Analytics Enhancements**: Develop more fine-grained filtering and comparative metrics between test and production environments.

## Active Decisions

1. **Translation Service Architecture**: Using Claude 3.7 Sonnet for all translations due to its superior context-awareness and ability to handle specialized terminology.

2. **Glossary System Design**: Building a JSON-based glossary structure organized by template types and target languages.

## Component Analysis Updates

*   **Template System Implementation:** Analysis of the template system in `app/utils/llm_clients.py` reveals:
    *   Industry-specific templates implemented via the `get_template_guidance()` function
    *   Specialized templates for Music Lessons, Corporate Training, Marketing, General Education, and Technical Tutorials 
    *   Each template provides detailed structural guidance with section proportions and specialized formatting
    *   Templates are designed to prevent formatting artifacts in the final outputs
    *   Integration with token tracking to monitor usage by template type
    *   Implementation uses Strategy pattern for selecting appropriate template instructions

*   **Content Analysis System:** The `app/components/content_analyzer.py` implements:
    *   Document content analysis using Claude 3.7 Sonnet with structured JSON output
    *   Specialized analysis for YouTube transcripts via reference handlers
    *   Extraction of key information including summaries, topics, structure outlines, and keywords
    *   Integration with script generation to incorporate analysis results into prompts
    *   Placeholder functionality for web URL analysis (not fully implemented)

*   **Admin Interface Architecture:** The admin interface in `app/main.py` demonstrates:
    *   Clear separation between public-facing features and admin-only functionalities
    *   Simple username/password authentication (admin/admin123)
    *   State-based interface switching between public interface, login form, and admin dashboard
    *   Admin-only access to token analytics and testing suite
    *   Detailed documentation in `docs/ADMIN_INTERFACE.md`
    *   Security considerations for production deployments

*   **Configuration System:** Analysis of `app/config.py` shows:
    *   Environment variable loading from `.env` file using `load_dotenv()`
    *   Validation of required API keys (ELEVENLABS_API_KEY, DEEPSEEK_API_KEY, ANTHROPIC_API_KEY)
    *   Function to update `.env` file with new configuration values
    *   Integration with application startup and error handling
    *   No UI for configuration management (command-line or file editing only)

*   **Component Analysis:**
    *   **Script Editor Component:** Analysis of `app/components/script_editor.py` shows a complete UI implementation with:
        *   Original script input area with placeholder guidance
        *   Edit instructions input with context manager
        *   Edit button connected to `edit_script` function
        *   Humanize button with HTML preview capabilities
        *   Integration with `edit_script_with_claude` for AI-powered editing
        *   Error handling for empty inputs and API failures
        *   File saving functionality with timestamp-based filenames
    *   **Script Editing Function:** The `edit_script_with_claude` function in `app/utils/llm_clients.py`:
        *   Uses Claude 3.7 Sonnet with a specialized system prompt for editing
        *   Implements error handling and retry logic
        *   Tracks token usage with the `token_tracker` system
        *   Returns structured data including edited content and usage metrics
    *   **Elevenlabs Integration:** The `app/utils/elevenlabs_client.py` implements:
        *   Voice listing and retrieval from the ElevenLabs API
        *   Voice generation with customizable parameters (stability, similarity, style, speed)
        *   Format conversion utilities (MP3 to OGG, WAV conversion)
        *   Fallback mechanisms when the API key is missing
        *   Error handling for API failures and format compatibility issues
    *   **Humanize Script Feature:** Detailed analysis of the `humanize_script` function reveals a sophisticated implementation that:
        *   Uses Claude 3.7 to transform plain scripts into voiceover-optimized formats with professional markup
        *   Implements robust error handling with multiple fallback mechanisms
        *   Provides preview functionality with color-coded highlighting of markup elements
        *   Integrates with the token tracking system to monitor API usage
        *   Addresses artifact prevention in the TTS output through careful markup and post-processing
    *   **Token Tracking System:** Analysis shows a comprehensive tracking implementation that:
        *   Uses a singleton `TokenTracker` instance created at line 346 in `app/utils/token_counter.py`
        *   Records model usage, template types, success/failure rates, and cost metrics
        *   Provides visualization through the admin dashboard in `app/components/token_dashboard.py`
        *   Integrates with both DeepSeek and Claude API calls throughout the application
    *   **Translation Feature Planning:** Detailed documentation in `docs/TRANSLATION_IMPLEMENTATION_PLAN.md` outlines:
        *   Implementation of a new `TranslationService` module in the Content Processing Layer
        *   Nine target languages: French, Spanish, German, Italian, Portuguese, Russian, Japanese, Korean, Chinese
        *   Claude 3.7 Sonnet as the primary translation engine with context-aware prompting
        *   Template-specific glossary system in JSON format for technical terminology
        *   UI plans for language selector dropdown, translation button, and result display in the Editing Tab
        *   Cost projections at ~$0.045 per average translation with detailed token usage estimates
        *   Complete implementation phases spanning architecture design, core functionality, template enhancements, UI, testing, and deployment
*   **Recent Changes:** 
    *   Completion of Phase 2: Content Processing Core (Reference Input UI for Docs/URLs/YouTube) and the **Humanize Feature** (script optimization for TTS).
    *   Completion of Phase 1: DeepSeek R1 integration (primary), Claude 3.7 fallback, MCP framework setup, Cross-template testing suite UI/auth enhancements, general UI/UX improvements (batch output display, status messages).
    *   Fixes implemented (from `CHANGELOG.md`): Removed artifact-causing intonation markers (↗↘), updated Humanize prompt, improved script preview highlighting, fixed Token Analytics dashboard SQL query.
*   **Next Steps:** 
    1.  Complete Phase 3 (Translation) following the implementation plan:
        *   Design and implement the `TranslationService` backend module
        *   Create the glossary management system for template-specific terminology
        *   Build the UI components in the Script Editor tab
        *   Integrate with Claude 3.7 and token tracking 
    2.  Proceed to Phase 4 (Multi-Source Data & Initial Reference Enhancement - FireCrawl, Perplexity, Browser Tools MCPs, Memory MCP).
    3.  Implement Phase 5 (Advanced Reference Processing System - Semantic Pinpointing, Style Matching).
    4.  Implement Phase 6 (Media Enhancement & Output - File System MCP, Doc Conversion MCP, EverArt MCP, Suno AI).
    5.  Complete remaining Phase 7 tasks (Full Analytics, UI polishing, Deployment).
*   **Active Decisions/Considerations:**
    *   Continuous improvement of the Humanize feature, possibly incorporating user feedback on markup effectiveness
    *   Enhancing token tracking analytics to provide more actionable insights on API usage patterns
    *   Finalizing translation glossary structure and maintenance strategy for the nine target languages
    *   Determining if advanced translation features become part of a Premium tier.
    *   Refining style matching effectiveness and reference pinpointing accuracy (Phase 5).
    *   Mitigating risks related to API costs, stability, and quality (ongoing).
    *   Completing test coverage for the testing suite.

## Project and Product Context Updates

The VoiceScribe Studio project is defined by the following key aspects:

### Core Requirements & Goals
- Development of an "Intelligent Agent-driven Content Production Studio" leveraging advanced AI (LLMs, TTS)
- Primary goal is to enhance content quality, reduce manual effort, and integrate AI agents directly into the workflow
- Key features include script generation from prompts/references, script editing, voice synthesis with customization
- Future capabilities include translation, AI research assistance, and multimedia production

### Project Scope
- **Completed (v0.1.0 / Phase 1 & 2)**: Advanced script generation, multiple templates, script editing, enhanced voice synthesis, basic reference input UI, "Humanize" feature, admin dashboard, cross-template testing suite, token analytics
- **Future Phases**: Full reference content processing, multilingual translation, AI research/fact-checking, multimedia generation, professional document exports, user preference memory
- **Likely Out of Scope**: Real-time collaboration, mobile application version, video editing capabilities

### Problems Solved
- Addresses the time-consuming and potentially complex process of creating high-quality, engaging scripts
- Improves script quality, ensures factual accuracy (future), optimizes voice delivery, and integrates multimedia elements efficiently

### User Experience Goals
- Provides a polished, intuitive UI with clear visual feedback
- Offers customization through templates and parameters
- Enhances output quality via advanced AI models and features like "Humanize"
- Streamlines the workflow from script to audio

### Why it Exists
- To leverage state-of-the-art AI models and a structured workflow to create a powerful, efficient content production tool
- To go beyond simple generation towards an intelligent, agent-driven studio

This context aligns with the current focus on the Translation Feature implementation (Phase 3) and ongoing enhancements to optimize voice delivery through the humanize feature.

## README Insights

Reviewing the README.md provides additional context about the project:

### Development & Versioning
- **main**: Latest stable, released version (currently v0.1.0)
- **phase-2-features**: Active development branch for Phase 2 features
- **Tags**: Specific versions (like `v0.1.0`) are marked using Git tags on the `main` branch
- Development for upcoming features occurs on dedicated branches and is merged into `main` upon completion

### Installation Requirements
- Python 3.9+
- API keys for DeepSeek, Anthropic (Claude), and ElevenLabs
- Future requirements will include YouTube Data API, Perplexity API, Suno AI API, and EverArt API

### Application Structure
- Single Gradio application on port 7860
- Main interface for script generation, editing, and voiceover production
- Admin dashboard accessible via login (`admin`/`admin123`)

### Humanize Feature Details
The README describes the specific markup techniques used in the Humanize feature:

- **Enhanced Pause Markers**: 
  - `<break time="0.5s" />` for minor phrase breaks
  - `<break time="1s" />` for pauses between sentences
  - `<break time="1.5s" />` for emphasis points
  - `<break time="2s" />` for paragraph breaks

- **Artifact Prevention**:
  - `. <break time="2s" /> [text starts here...]` at the beginning
  - `[...text ends here] <break time="2s" /> .` at the end

- **Emotional Expression**:
  - Book-style narration: `"Our options are limited", he said angrily.`
  - Emotion tags: `<cheerful, happily>Great news!</cheerful, happily>`

- **Emphasis Markers**:
  - `*word*` for emphasis
  - `**word**` for strong emphasis

- **Known Issues**:
  - Arrow symbols like `↗` or `↘` cause artifacts in ElevenLabs voiceovers

This detailed markup information aligns with and expands upon our understanding of the Humanize feature implementation documented in `systemPatterns.md`. 