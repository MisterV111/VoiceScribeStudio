# System Patterns

*   **System Architecture:** Multi-Tier system built using Python and Gradio.
    *   **UI Layer:** Gradio web interface (`app/main.py`, `app/components/`) with state-based navigation between Public and Admin sections.
    *   **Core Logic:** Resides primarily in `app/main.py` (orchestration), `app/components/` (UI logic), and `app/utils/` (clients, helpers).
    *   **LLM Layer:** Primary/Fallback pattern using DeepSeek R1 (via OpenAI SDK) and Claude 3.7 Sonnet (`app/utils/llm_clients.py`). Specific prompts and guidance based on templates.
    *   **TTS Layer:** Facade (`app/utils/tts_clients.py`) interacting with ElevenLabs (`app/utils/elevenlabs_client.py`) for voice generation. Includes a "Humanize" preprocessing step using Claude 3.7 (`app/utils/humanize_script.py`).
        *   **Voice Loading Mechanism:** Consolidated implementation with a single source of truth:
            *   **In `app/utils/elevenlabs_client.py`:** Centralized `load_all_voices()` function serves as the primary voice loading mechanism. It:
                *   Provides hardcoded preset voices for reliability (including Dan Teacher voices at the top)
                *   Attempts to fetch additional voices from the ElevenLabs API in a separate thread with a timeout
                *   Returns both preset voices and the combined list of all voices (preset + API-fetched)
                *   Handles API failures gracefully, falling back to preset voices when needed
            *   **In `app/utils/tts_clients.py`:** Re-exports the consolidated function as `load_voices = load_all_voices` for backward compatibility.
            *   **In `app/main.py`:** Uses the consolidated function from elevenlabs_client.py via `preset_voice_names, preset_voice_ids, voice_names, voice_ids = load_all_voices()`.
            *   **Data Flow:** Voice data is loaded at startup in `main.py` via the consolidated function, then passed to both the global context and to the voiceover component via `set_voice_data()`.
        *   **Script Humanization:** The `humanize_script` function transforms plain script text into formats optimized for voiceover delivery:
            *   **Process:** Uses Claude 3.7 to add professional voiceover markup, including SSML pause tags (`<break time="Xs" />`), emphasis markers (`*word*`, `**word**`), emotional cues, and artifact prevention techniques.
            *   **System Prompt:** Provides Claude with detailed instructions for script formatting, including standardized markup conventions, emphasis guidelines, and rules for handling production notes.
            *   **Input Processing:** Cleans input script of triple backticks and potential confusion points before sending to Claude.
            *   **Workflow:**
                *   Validates input script (checks for empty content)
                *   Generates unique session_id for token tracking
                *   Constructs specialized system prompt for Claude with detailed markup instructions
                *   Calls Claude 3.7 Sonnet via `call_anthropic_with_retry` for reliable processing
                *   Processes response to extract and verify the humanized script
                *   Handles errors at every step with comprehensive checks
                *   Returns formatted output with original script on failure
            *   **Markup Elements:** Adds specific markup including:
                *   Pause markers with precise timing (0.5s, 1s, 1.5s, 2s, 3s)
                *   Emphasis for important words using asterisks
                *   Book-style narration for emotional context (e.g., `"Text", he said angrily.`)
                *   Emotion tags (e.g., `<cheerful>text</cheerful>`)
                *   Artifact prevention markers at script beginning/end
            *   **Post-Processing:** Cleans Claude's response by removing code blocks, introductory text, and checking for suspicious outputs that might indicate API issues.
            *   **Error Detection:** Implements robust pattern matching with regex to identify HTTP error codes and error messages in Claude responses.
            *   **Error Handling:** Multiple error handling mechanisms for:
                *   Empty or invalid script content
                *   API unavailability
                *   API call failures (with retry logic via `call_anthropic_with_retry`)
                *   Rate limiting (HTTP 529)
                *   Error codes in responses
                *   Suspiciously short outputs
                *   General exceptions (with traceback logging)
            *   **Graceful Degradation:** Returns original script with appropriate error messages when issues occur.
            *   **Preview:** The `preview_humanized_markup` function generates HTML showing differences between original and humanized scripts with:
                *   Color-coded highlighting for different markup elements
                *   Warning indicators for problematic characters (↗↘) that cause audio artifacts
                *   Side-by-side comparison of original and transformed text
                *   Visual indicators for pause markers, emphasis, emotion tags, and book-style narration
            *   **Token Tracking:** Tracks all Claude API usage via `token_tracker.track_generation()` for both successful (with output) and failed attempts (with empty output).
            *   **Integration:** Called from `app/components/script_editor.py` via the `humanize_script_handler` function which handles UI interaction and file saving.
    *   **Token Tracking Layer:** Comprehensive token usage tracking implemented in `app/utils/token_counter.py`. A singleton `TokenTracker` instance is created at line 346 and imported across the application. The system:
        *   **Database:** Uses SQLite database at `data/token_usage.db` to persistently store token usage metrics
        *   **Token Counting:** Uses OpenAI's `tiktoken` library to count tokens with a fallback character-based estimation
        *   **Usage Tracking:** `track_generation()` method records input/output tokens, model, template, success/failure, and metadata
        *   **Cost Estimation:** `estimate_cost()` calculates API costs based on current pricing for DeepSeek/Claude
        *   **Analytics:** `get_usage_summary()` provides aggregated metrics by model, template, and time period
        *   **Testing Integration:** The token tracking system is fully integrated with the testing framework:
            *   **Test Flagging:** All scripts generated during test runs are tagged with `is_test=True` in the database via the `is_test` parameter in `track_generation()`
            *   **Test Estimation:** Before running tests, the `estimate_time_and_tokens()` function in `filter_presets.py` provides token usage and cost estimates based on test count
            *   **Test Results:** Token metrics are recorded in individual test results via the `token_usage` field
            *   **Test Filtering:** The token dashboard allows filtering out test runs in analytics via the `include_tests` parameter in both UI and database queries
            *   **Resource Planning:** Testing dashboard displays estimated token usage and costs before executing test runs to help users make informed decisions
            *   **Token Aggregation:** The `TestRunner._generate_summary()` method aggregates token usage data across tests for template-level statistics
        *   **Integration Points:** 
            *   In `llm_clients.py`, tracks both DeepSeek (line 178) and Claude (line 299) generation attempts, including failed calls
            *   In `humanize_script.py`, tracks Claude usage for script humanization (line 243)
            *   In `test_runner.py`, propagates the `is_test=True` flag through `generate_script()` calls
            *   In `token_dashboard.py`, visualizes usage metrics through the admin dashboard
    *   **Reference Processing Layer:**
        *   **Web Content:** `app/utils/reference_handlers/web_utils.py` extracts text from web URLs using BeautifulSoup with fallback methods for various user agents and handling of SSL issues.
        *   **YouTube Content:** `app/utils/reference_handlers/youtube_utils.py` extracts transcripts from YouTube videos using the youtube-transcript-api library with robust error handling and fallback methods.
        *   **Document Content:** Integrated directly in `app/components/script_generator.py` with support for TXT, MD, PDF (via PyMuPDF/fitz), and DOCX (via python-docx) formats. Uses temp files for processing.
        *   **Content Analysis:** `app/components/content_analyzer.py` provides structured analysis of extracted content, primarily using Claude 3.7 Sonnet. The `analyze_content()` function in `llm_clients.py` serves as a central dispatcher to route content to the appropriate analyzer. Uses an adaptation of the Decorator pattern via `ensure_analyze_function()` for graceful degradation when components are unavailable. Analysis produces structured JSON with summaries, key topics, structure outline, and keywords.
    *   **MCP Layer (Planned):** Future integration with Model Context Protocol servers for specialized tasks (FireCrawl, Perplexity, Memory, File System, Document Conversion, EverArt).
    *   **Data Layer:** Token usage tracked in SQLite database (`data/token_usage.db`) via `app/utils/token_counter.py`. Test results likely stored in SQLite (based on `CROSS_TEMPLATE_TESTING.md`).
    *   **Analytics Layer:** Token usage dashboard (`app/components/token_dashboard.py`) with visualizations using Plotly for model usage, costs, template usage, fallback rates, and historical trends.
    *   **Configuration:** Loaded from `.env` file via `app/config.py`.
*   **Key Technical Decisions:** 
    *   Using Gradio for the UI.
    *   Employing a multi-LLM strategy (DeepSeek primary, Claude fallback) for script generation quality and reliability.
    *   Utilizing Claude 3.7 specifically for fallback, script editing, content analysis, and the "Humanize" feature.
    *   Implementing specific ElevenLabs optimization techniques (breaks, artifact prevention, no arrows) via the Humanize feature.
    *   Creating a separate, authenticated admin interface for testing and analytics.
    *   Building token tracking and analytics with SQLite + Plotly for monitoring API usage and costs.
    *   Using structured JSON output from Claude for content analysis to enable predictable processing.
    *   Implementing robust fallback mechanisms throughout the system to handle API failures, missing dependencies, and edge cases.
    *   Planning for future modularity using MCP servers.
    *   Using detailed, template-specific prompts for LLMs.
*   **Design Patterns:**
    *   **Facade:** `app/utils/tts_clients.py` simplifies interaction with ElevenLabs and Humanize logic.
    *   **Primary/Fallback:** Used for LLM script generation and in reference handlers (multiple fallback strategies for web content and YouTube).
    *   **Singleton/Command Pattern:** Global token tracking with a shared instance (`token_tracker = TokenTracker()` at line 346 in `app/utils/token_counter.py`) used across modules to centralize usage tracking from any point in the application.
    *   **Decorator/Adapter:** `ensure_analyze_function()` wraps the content analyzer functions to provide graceful degradation.
    *   **Strategy Pattern:** Content analysis dispatches different strategies based on content type (document, YouTube, web).
    *   **State Management:** Gradio's `gr.State` used in `app/main.py` to control UI visibility (public/login/admin).
    *   **Modular Design:** Separation of concerns into `components` (UI), `utils` (backend logic/clients), `docs`, `tests`.
    *   **Dependency Injection:** References to models are passed between components rather than hardcoded.
    *   **Configuration Management:** Centralized loading from `.env` via `app/config.py`.
*   **Component Relationships:**
    *   `run.py` executes `app.main.main()`.
    *   `app/main.py` initializes the Gradio app, loads config/voices, sets up UI tabs by calling functions from `app/components/`, and handles UI state/authentication.
    *   UI components (`app/components/*.py`) define Gradio layouts and call utility functions (`app/utils/*`) for backend operations (LLM calls, TTS calls, etc.).
    *   `llm_clients.py` interacts with DeepSeek/Anthropic APIs, uses `token_counter.py`, and provides the `analyze_content()` dispatcher for content analysis.
    *   `token_counter.py` provides token counting and usage tracking, storing data in SQLite and used by `token_dashboard.py` for analytics.
    *   `tts_clients.py` acts as facade for `elevenlabs_client.py` and `humanize_script.py`.
    *   `humanize_script.py` uses `llm_clients.py` (Claude) for transformation and calls `token_tracker.track_generation()` to log usage.
    *   Reference handlers (`web_utils.py`, `youtube_utils.py`) extract content from external sources.
    *   Document processing is integrated directly in `script_generator.py` component.
    *   `content_analyzer.py` provides structured analysis of document content using Claude, which is used to enhance script generation prompts.
    *   `token_dashboard.py` creates a Gradio interface that visualizes token usage data via `token_tracker.get_usage_summary()`. 
    *   `test_runner.py` orchestrates automated tests, using `token_tracker` to mark all test-generated content in the database and store token metrics in test results.
    *   `testing_dashboard.py` provides a Gradio interface for running tests and visualizing results, including pre-test estimates of token usage and costs. 

## Template System

The Template System provides industry-specific guidance for script generation, enhancing the quality and relevance of outputs based on domain requirements.

### Implementation Details:
- Implemented in `app/utils/llm_clients.py` via the `get_template_guidance()` function
- Templates define specialized script structures for different domains:
  - **Music Lesson**: Structured for instrument tutorials with specialized markers for talking heads, demonstrations, and view angles
  - **Corporate Training**: Organized for business environments with engagement points, key concepts, and facilitator notes
  - **Marketing**: Optimized for engagement with specialized sections for hooks, benefits, social proof, and calls to action
  - **General Education**: Structured for educational content with explanations, examples, and learning objectives
  - **Technical Tutorial**: Focused on step-by-step guidance with code snippets and verification steps
  - **General**: Default template with basic structural guidance

### Usage Flow:
1. The user selects a template type in the script generator interface
2. `generate_script()` (line ~462 in `llm_clients.py`) retrieves template-specific guidance
3. Template guidance is incorporated into the system message for the LLM
4. Token tracking records which templates are used for analytics purposes

### Key Features:
- Templates provide domain-specific structure without requiring marker removal
- Each template includes detailed instructions on content organization and presentation
- The system prevents template formatting artifacts from appearing in final outputs
- Templates are designed to work with both DeepSeek and Claude models

## Content Analysis Layer

The Content Analysis Layer extracts key information from external sources to enhance script generation with relevant context.

### Implementation Details:
- Implemented in `app/components/content_analyzer.py`
- Uses Claude 3.7 Sonnet to analyze document content via structured prompts
- Designed to work with various content types:
  - Document text (PDF, DOCX, TXT)
  - YouTube transcripts (via `youtube_utils.py`)
  - Web URLs (planned functionality)

### Analysis Process:
1. Source content is extracted using appropriate reference handlers
2. `analyze_document_content()` constructs a structured prompt for Claude
3. Analysis request is sent to the API via `call_claude_sonnet_for_analysis()`
4. Results are returned as JSON with predefined structure:
   - Summary (2-4 sentences)
   - Key topics (3-5 main themes)
   - Structure outline (potential section headings)
   - Extracted keywords (5-10 important terms)

### Integration:
- Analysis results are incorporated into script generation prompts
- This ensures that generated scripts align with and reference key information from source materials
- Token tracking records analysis API calls with appropriate template attribution

## Admin Interface

The Admin Interface provides restricted access to advanced features and analytics dashboards.

### Implementation Details:
- Implemented in `app/main.py` using a state-based interface switcher
- Features simple username/password authentication:
  - Default credentials: Username: `admin` / Password: `admin123`
  - Credentials defined by `ADMIN_USERNAME` and `ADMIN_PASSWORD` constants

### Architecture:
- Single Gradio app with three distinct interfaces:
  1. **Public Interface**: Core script generation and voiceover features
  2. **Login Form**: Authentication gateway to admin features
  3. **Admin Dashboard**: Restricted analytics and testing features

### Admin Features:
- **Token Analytics**: Track API usage, costs, and patterns across models
- **Testing Suite**: Run automated tests and view detailed results

### Security Approach:
- State variables track authentication status and current interface
- Interface visibility is controlled based on authentication state
- Simple but effective credential verification
- Seamless navigation between interfaces without page reloads

## Configuration System

The Configuration System manages environment variables and application settings.

### Implementation Details:
- Primary implementation in `app/config.py`
- Utilizes Python's `load_dotenv()` to load variables from `.env` file
- Configuration settings include API keys, model selections, and feature flags

### Key Functions:
- `validate_config()`: Verifies required API keys are present
- `save_config_to_env()`: Updates the `.env` file with new configuration values
- Error handling for missing or invalid configuration values

### Configuration Categories:
- **API Keys**: ELEVENLABS_API_KEY, DEEPSEEK_API_KEY, ANTHROPIC_API_KEY
- **Model Selections**: Which LLM models to use for generation and analysis
- **Feature Flags**: Enable/disable specific features like analytics

### Integration:
- Configuration is loaded at application startup in `app/main.py`
- Users are prompted to update their `.env` file if required keys are missing
- Admin interface can modify certain configuration values (planned enhancement) 