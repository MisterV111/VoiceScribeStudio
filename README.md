# VoiceScribe Studio (Version 0.1.0)

<div align="center">
  <img src="app/assets/VoiceScribe Studio Banner.png" alt="VoiceScribe Studio Banner" width="800">
  
  **Professional AI-Powered Content Creation Suite**  
  *Proprietary Software by INSPIRED CREATIVE GROUP INC.*
</div>

## About

VoiceScribe Studio leverages advanced AI workflow backend integrations to enhance content creation. This version (v0.1.0) focuses on providing a high-quality script generation core and a polished voiceover production experience.

Our vision is to build VoiceScribe into an **Intelligent Agent-driven Content Production Studio**, integrating AI agents directly into the workflow to streamline both the creative and production processes, from initial concept to final multimedia output.

### Current Capabilities (v0.1.0 - Phase 1 Complete)

- 📝 **Smarter Script Generation**: Significantly upgraded AI engine using:
  - **DeepSeek R1** as the primary model for high-quality, creative scripts across various templates.
  - **Claude 3.7 Sonnet** as a robust fallback for reliability.
- 🗣️ **Enhanced Voice Synthesis & Output**: A more polished experience for generating voiceovers:
  - Support for multiple audio formats: **MP3 (High Quality 192kbps)**, **OGG (Game Audio Quality)**, and **High Quality WAV (48kHz/24-bit)**.
  - **Batch Generation**: Create all formats with a single click.
  - **Format Preview**: See which formats will be generated when selecting "Generate All Formats".
  - **Professional Download Interface**: Clean, responsive cards with format-specific icons and file details.
  - **Styled Status Messages**: Clear visual feedback (e.g., colored success messages) for generation status.
- 📄 **Reference Input Options**: Multiple ways to provide context for enhanced script generation:
  - **Document Upload**: Support for various file formats (.txt, .md, .pdf, .docx)
  - **Web URL Reference**: Extract context directly from web pages
  - **YouTube Reference**: Use YouTube videos as style or content references
- 🎭 **Humanize Feature**: Intelligent script formatting that automatically adds natural pauses, emotional emphasis, and timing cues to optimize voiceover delivery.
- 🔧 **Voice Customization**: Fine-tune voice parameters (stability, similarity, style, speed).
- ✏️ **Script Editing**: Built-in editor to refine generated scripts.
- 🔀 **Multiple Templates**: Specialized templates (General Education, Technical Tutorial, Marketing, Business Training, Music Lesson).
- 📊 **Audience & Content Adaptation**: Customize scripts for different audience levels, tones, and lengths.
- 💾 **Local Storage**: Save generated scripts and audio files to your machine.
- 🧪 **Admin & Testing Tools**:
  - **Secure Admin Dashboard**: Separate interface for testing and analytics (Login: `admin`/`admin123`).
  - **Cross-Template Testing Suite**: Ensures reliability and quality across templates.
  - **Token Analytics Dashboard**: Track token usage, costs, and model efficiency for both DeepSeek and Claude models.

### Future Vision (Planned Enhancements)

The roadmap includes transforming VoiceScribe into a full AI content **production** partner through phased development:

- **Phase 2: Active Development Branch**: 
  - Feature fixes and bug resolutions for enhanced stability
  - Performance optimizations and user experience improvements
  - Ongoing maintenance and quality assurance updates
- **Phase 3: Multilingual Translation**: AI-powered translation to multiple languages using Claude 3.7 Sonnet and custom glossaries.
- **Phase 4: AI Research Assistant**: Web browsing (FireCrawl) and fact-verification (Perplexity MCP) capabilities for accurate, informed scripts.
- **Phase 5: Multimedia Production**: AI-generated background music (Suno AI), visual content (EverArt MCP), and professional document exports.
- **Phase 6: Polishing & Professional Tools**: User dashboards for cost tracking, enhanced input methods (URLs, docs), media previews, and final deployment.

## Development & Versioning (Private Deployment)

### Branch Strategy
- **main**: Production-ready stable releases (currently v0.1.0)
- **phase-2-features**: Active development for bug fixes and feature enhancements
- **hotfix/***: Critical bug fixes for immediate deployment
- **feature/***: Individual feature development branches
- **release/***: Release preparation and testing branches

### Version Management
- **Semantic Versioning**: `MAJOR.MINOR.PATCH` (e.g., v0.1.0)
- **Git Tags**: All versions tagged on `main` branch for deployment tracking
- **Release Notes**: Documented in `docs/CHANGELOG.md`
- **Branch Protection**: `main` branch requires pull request reviews

### Development Workflow
1. Create feature branch from `main`: `git checkout -b feature/feature-name`
2. Develop and test locally using development environment
3. Submit pull request to `phase-2-features` for review
4. After approval, merge to `phase-2-features` for integration testing
5. When stable, merge to `main` and tag new version
6. Deploy to production environment

### Environment Management
- **Development**: Local development with test API keys and debug mode
- **Staging**: Pre-production testing with limited API quotas
- **Production**: Live deployment with full API access and monitoring

## Private Deployment Installation

### System Requirements
- **Operating System**: macOS, Windows 10+, or Linux (Ubuntu 20.04+)
- **Python**: 3.9+ (3.11 recommended for optimal performance)
- **Memory**: Minimum 4GB RAM (8GB recommended)
- **Storage**: 2GB free space for dependencies and output files
- **Network**: Stable internet connection for API calls

### API Keys & Prerequisites
```bash
# Required API Keys (Get from respective providers)
DEEPSEEK_API_KEY=your_deepseek_api_key_here       # Primary LLM
ANTHROPIC_API_KEY=your_anthropic_api_key_here     # Fallback LLM
ELEVENLABS_API_KEY=your_elevenlabs_api_key_here   # Voice synthesis

# Optional API Keys (Future features)
YOUTUBE_DATA_API_KEY=your_youtube_data_api_key_here
PERPLEXITY_API_KEY=your_perplexity_api_key_here
SUNO_API_KEY=your_suno_api_key_here
EVERART_API_KEY=your_everart_api_key_here
```

### Local Development Setup

1. **Licensed Access**: Contact INSPIRED CREATIVE GROUP INC. for repository access.
   ```bash
   git clone https://github.com/MisterV111/VoiceScribeStudio.git
   cd VoiceScribeStudio
   ```

2. **Environment Setup**:
   ```bash
   # Create virtual environment
   python -m venv venv
   
   # Activate virtual environment
   # macOS/Linux:
   source venv/bin/activate
   # Windows:
   venv\Scripts\activate
   
   # Verify Python version
   python --version  # Should be 3.9+
   ```

3. **Dependency Installation**:
   ```bash
   # Install core dependencies
   pip install --upgrade pip
   pip install -r requirements.txt
   
   # Verify installation
   pip list | grep -E "(gradio|anthropic|openai)"
   ```

4. **Environment Configuration**:
   ```bash
   # Copy environment template
   cp env.example .env
   
   # Edit .env file with your API keys
   # Use your preferred editor (nano, vim, VSCode, etc.)
   nano .env
   ```

5. **Database Initialization**:
   ```bash
   # Token tracking database is auto-created on first run
   # Verify database directory exists
   mkdir -p data/
   ```

6. **Initial Testing**:
   ```bash
   # Run application in development mode
   python run.py
   
   # Verify access at http://localhost:7860
   # Test admin access with credentials: admin/admin123
   ```

### Production Deployment Configuration

#### Security Settings
```bash
# Production environment variables
export GRADIO_SERVER_NAME="0.0.0.0"  # Allow external connections
export GRADIO_SERVER_PORT="7860"     # Default port
export GRADIO_DEBUG="False"          # Disable debug mode

# Admin credentials (change these!)
export ADMIN_USERNAME="your_admin_username"
export ADMIN_PASSWORD="your_secure_password"
```

#### File Permissions & Storage
```bash
# Set appropriate permissions
chmod 755 run.py
chmod -R 755 app/
chmod 600 .env  # Protect API keys

# Create output directories
mkdir -p output/scripts output/audio temp_output/
chmod 755 output/ temp_output/
```

#### Network Configuration
- **Port**: Default 7860 (configurable in run.py)
- **Access**: Local network access by default
- **SSL**: Consider reverse proxy (nginx) for HTTPS in production
- **Firewall**: Configure firewall rules as needed

### Local Development Features

#### Debug Mode
- Set `DEBUG=True` in .env for detailed logging
- Access logs in `logs/` directory
- Real-time API call monitoring in admin dashboard

#### Development Tools
```bash
# Run tests
python -m pytest tests/

# Check code quality
python -m flake8 app/

# Generate documentation
python -m pydoc app.main

# Monitor token usage
tail -f logs/token_usage.log
```

#### Hot Reload Development
```bash
# Install development dependencies
pip install watchdog

# Run with auto-reload (if available)
gradio app/main.py --reload
```

### Troubleshooting Common Issues

#### API Connection Issues
- Verify API keys in `.env` file
- Check internet connectivity
- Monitor API quotas and rate limits
- Review logs in `logs/` directory

#### Performance Optimization
- Increase system memory allocation
- Use SSD storage for better I/O performance
- Monitor CPU usage during batch operations
- Consider API call caching for development

#### File Upload Issues
- Check file size limits (default: 75,000 tokens)
- Verify supported file formats (.txt, .md, .pdf, .docx)
- Ensure proper file permissions
- Clear temp_output/ directory if full

### Monitoring & Analytics

#### Built-in Monitoring
- **Token Usage**: Real-time tracking via admin dashboard
- **API Performance**: Response times and error rates
- **System Health**: Memory and storage usage
- **User Activity**: Script generation and voiceover metrics

#### Log Files
```bash
logs/
├── application.log      # General application logs
├── token_usage.log     # API usage and costs
├── error.log          # Error tracking
└── performance.log    # Performance metrics
```

## Application Structure

VoiceScribe Studio runs as a single Gradio application with modular architecture:

### Core Components
- **app/main.py**: Application entry point and interface orchestration
- **app/components/**: UI components (script generator, voiceover generator, etc.)
- **app/utils/**: Core utilities (LLM clients, token tracking, etc.)
- **app/tests/**: Testing framework and admin tools
- **data/**: Local database and storage
- **output/**: Generated scripts and audio files

### Interface Organization
- **Main Interface (Port 7860)**: User-facing tools for content creation
- **Admin Dashboard**: Testing suite, analytics, and monitoring tools
- **API Endpoints**: Internal API for component communication

## Usage Guide (Private Deployment)

### Basic Workflow
1. **Access Application**: Navigate to `http://localhost:7860`
2. **Script Generation**: Use templates and reference materials
3. **Content Editing**: Refine scripts with built-in editor
4. **Voice Generation**: Create audio with customizable parameters
5. **Download & Export**: Save files locally or to network storage

### Advanced Features
- **Batch Processing**: Generate multiple formats simultaneously
- **Template Customization**: Modify templates for specific use cases
- **Voice Parameter Tuning**: Fine-tune stability, similarity, and style
- **Reference Integration**: Use documents, URLs, and YouTube videos
- **Quality Assurance**: Built-in testing and validation tools

### Admin Dashboard Features
- **Token Analytics**: Cost tracking and usage optimization
- **Testing Suite**: Cross-template validation and quality assurance
- **System Monitoring**: Performance metrics and health status
- **User Management**: Access control and activity tracking

## Templates & Customization

VoiceScribe Studio offers specialized templates optimized for different content types:

- **General Education**: Academic and instructional content
- **Technical Tutorial**: Step-by-step technical guides
- **Marketing**: Promotional and advertising content
- **Business Training**: Corporate training and development
- **Music Lesson**: Music education and instruction

### Template Customization (Authorized Users)
- Modify existing templates in `app/templates/`
- Create custom templates following established patterns
- Test templates using admin dashboard before deployment

## Security & Compliance

### Data Protection
- **API Keys**: Encrypted storage and secure transmission
- **User Data**: Local processing with no external data sharing
- **File Uploads**: Temporary storage with automatic cleanup
- **Access Control**: Admin authentication and session management

### Privacy Considerations
- **Local Processing**: All data processing occurs on local machine
- **No Data Collection**: No user data transmitted to unauthorized parties
- **API Usage**: Only necessary data sent to API providers (DeepSeek, Anthropic, ElevenLabs)
- **Output Security**: Generated content stored locally by default

## Contributing (Authorized Personnel Only)

**VoiceScribe Studio** is proprietary software owned by INSPIRED CREATIVE GROUP INC.

### Authorized Contributor Guidelines
1. **Access Approval**: Contact INSPIRED CREATIVE GROUP INC. for contributor access
2. **Development Environment**: Follow local deployment setup instructions
3. **Code Standards**: Maintain existing code quality and documentation standards
4. **Testing Requirements**: All changes must pass existing test suite
5. **Review Process**: Submit pull requests to `phase-2-features` branch

### Development Standards
- **Code Quality**: Follow PEP 8 for Python code style
- **Documentation**: Update relevant documentation for all changes
- **Testing**: Write tests for new features and bug fixes
- **Version Control**: Use descriptive commit messages and proper branching

## License

This software is proprietary and owned by **INSPIRED CREATIVE GROUP INC.** All rights reserved.

**VoiceScribe Studio** is licensed under a proprietary license agreement. Unauthorized copying, distribution, modification, or commercial use is strictly prohibited without explicit written permission from INSPIRED CREATIVE GROUP INC.

For licensing inquiries, please contact INSPIRED CREATIVE GROUP INC.
- Email: licensing@inspiredcreativegroup.com
- Website: https://inspiredcreativegroup.com

See the [LICENSE](LICENSE) file for complete terms and conditions.

## Support & Maintenance

### Technical Support (Authorized Users)
- **Email**: support@inspiredcreativegroup.com
- **Documentation**: Comprehensive docs in `docs/` directory
- **Issue Tracking**: Internal issue tracking for authorized users
- **Updates**: Regular maintenance and feature updates

### Maintenance Schedule
- **Security Updates**: As needed for critical vulnerabilities
- **Feature Updates**: Monthly releases with new capabilities
- **Bug Fixes**: Bi-weekly maintenance releases
- **Performance Optimization**: Quarterly performance reviews

## Acknowledgments

- [DeepSeek AI](https://www.deepseek.com/) for the DeepSeek R1 model
- [Anthropic](https://www.anthropic.com/) for the Claude 3.7 Sonnet model
- [ElevenLabs](https://elevenlabs.io/) for the text-to-speech technology
- [Gradio](https://gradio.app/) for the web interface
- Future Acknowledgments: Suno AI, Perplexity AI, YouTube Data API, FireCrawl, EverArt, etc.

## Humanize Feature Documentation

The Humanize feature transforms your scripts to sound more natural with ElevenLabs by adding optimized markup based on research from experienced users:

### Enhanced Pause Markers
- `<break time="0.2s" />` for minor phrase breaks
- `<break time="0.5s" />` for pauses between sentences
- `<break time="0.8s" />` for emphasis points
- `<break time="1s" />` for paragraph breaks

### Artifact Prevention
- `. <break time="1s" /> [text starts here...]` at the beginning
- `[...text ends here] <break time="1s" /> .` at the end

### Emotional Expression
- Book-style narration: `"Our options are limited", he said angrily.`
- Emotion tags: `<cheerful, happily>Great news!</cheerful, happily>`

### Emphasis Markers
- `*word*` for emphasis
- `**word**` for strong emphasis

### Known Issues
- Avoid using arrow symbols like `↗` or `↘` as they cause artifacts in ElevenLabs voiceovers

See `docs/ELEVENLABS_OPTIMIZATION.md` for detailed documentation and `examples/optimized_elevenlabs_script.txt` for a complete demonstration of these techniques.

These optimizations make ElevenLabs voices sound more natural, with better emotional range and fewer artifacts. The Humanize feature applies these techniques automatically to any script.

---
*© 2024 INSPIRED CREATIVE GROUP INC. All Rights Reserved.* 