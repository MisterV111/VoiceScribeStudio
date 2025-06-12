# Technical Context

*   **Technologies Used:**
    *   **Language:** Python 3.9+
    *   **UI Framework:** Gradio (`gradio`)
    *   **LLMs:** DeepSeek R1 (via API), Claude 3.7 Sonnet (via `anthropic` SDK)
    *   **TTS:** ElevenLabs (via `elevenlabs` SDK)
    *   **Core Libraries:** `python-dotenv` (config), `openai` (for DeepSeek API interaction), `requests`, `httpx` (API calls)
    *   **Data Handling:** `json`, `pandas`, `numpy`, `sqlite3` (for token usage analytics)
    *   **Visualization:** `plotly` (token usage dashboards), `matplotlib` (charts)
    *   **Audio:** `pydub` (audio manipulation), `ffmpy` (ffmpeg wrapper for audio conversion)
    *   **Document Processing:** `PyMuPDF` (aka `fitz`, for PDFs), `python-docx` (DOCX)
    *   **Web Content:** `beautifulsoup4`, `lxml` (HTML parsing)
    *   **YouTube:** `youtube-transcript-api` (transcript extraction)
    *   **Token Counting:** `tiktoken` (OpenAI-compatible tokenization)
    *   **Development/Utility:** `ruff` (linter), `pytest` (implied by tests directory), `typer`
    *   **Future:** APIs/SDKs for FireCrawl, Perplexity, Suno AI, EverArt.
*   **Development Setup:**
    1.  Clone repository: `git clone https://github.com/MisterV111/VoiceScribeStudio.git`
    2.  Navigate to directory: `cd VoiceScribeStudio`
    3.  Create virtual environment: `python -m venv venv`
    4.  Activate environment: `source venv/bin/activate` (or `venv\Scripts\activate` on Windows)
    5.  Install dependencies: `pip install -r requirements.txt`
    6.  Create `.env` file in the root directory.
    7.  Add required API keys to `.env`: `DEEPSEEK_API_KEY`, `ANTHROPIC_API_KEY`, `ELEVENLABS_API_KEY`.
    8.  Run application: `python run.py` (or `python -m app.main`). Access at http://localhost:7862 (or next available port).
*   **Technical Constraints:**
    *   Requires internet connectivity for API calls.
    *   Dependent on external API availability, rate limits, and costs (DeepSeek, Anthropic, ElevenLabs).
    *   ElevenLabs limitations: Custom voices must be in user's account; specific characters (↗↘) cause audio artifacts.
    *   YouTube transcript extraction requires available captions; not all videos have them.
    *   PDF and DOCX processing adds dependencies (PyMuPDF, python-docx) that might not be available in all environments.
    *   Performance may vary based on LLM response times and complexity of processing.
    *   Current authentication for admin panel (`admin`/`admin123` hardcoded in `app/utils/config.py`) is basic and not suitable for production without enhancement.
*   **Dependencies:**
    *   **External Services:** DeepSeek API, Anthropic API, ElevenLabs API. (Future: YouTube Data API, Perplexity API, Suno AI API, EverArt API, potentially others for MCPs).
    *   **Python Packages:** Listed in `requirements.txt` (see Technologies Used).
    *   **System Dependencies:** `ffmpeg` likely required for audio conversions (`ffmpy`, `pydub`).
    *   **Storage:** SQLite database for token usage analytics (`data/token_usage.db`).

## Framework and Libraries

### Template System
- **Purpose**: Provides industry-specific guidance for script generation
- **Key Files**: 
  - `app/utils/llm_clients.py` - contains template definitions and implementation
- **Dependencies**: None (pure Python implementation)
- **Design Pattern**: Strategy Pattern (different templates for different scenarios)

### Content Analysis
- **Purpose**: Extracts key information from external sources to enhance script generation
- **Key Files**:
  - `app/components/content_analyzer.py` - main implementation
  - `app/utils/reference_handlers/youtube_utils.py` - YouTube transcript extraction
- **Dependencies**:
  - `json` - for structured data formatting
  - Claude API (via `call_claude_sonnet_for_analysis()`)
- **Design Pattern**: Command Pattern (encapsulates analysis requests)

### Admin Interface
- **Purpose**: Provides restricted access to advanced features and analytics dashboards
- **Key Files**:
  - `app/main.py` - implementation of interface switching and authentication
  - `docs/ADMIN_INTERFACE.md` - detailed documentation
- **Dependencies**:
  - Gradio (for UI components)
  - State variables (for authentication tracking)
- **Design Pattern**: State Pattern (manages interface visibility based on authentication state)

### Configuration System
- **Purpose**: Manages environment variables and application settings
- **Key Files**:
  - `app/config.py` - main implementation
  - `.env` - environment variable storage
- **Dependencies**:
  - `dotenv` - for loading environment variables
  - `os` - for accessing environment variables
- **Design Pattern**: Singleton Pattern (single point of access for configuration) 