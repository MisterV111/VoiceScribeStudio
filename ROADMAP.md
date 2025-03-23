# VoiceScribe Studio Roadmap

## Current Implementation (MVP)

### Voice Generation
- Single API key approach: The application uses one ElevenLabs API key stored in `.env`
- Preset voices: Adam, Antoni, Bella, Rachel are available by default
- Custom Voice ID: Users can enter any ElevenLabs voice ID from their personal collection
- MP3 and OGG output formats supported

### Script Generation
- OpenAI integration for script generation and editing
- Customizable parameters for script length, tone, and audience
- Script saving and management

### Technical Implementation
- Environment variables for API key management
- Error handling for invalid API keys or voice IDs
- Unified interface for all features

## Future Development Plans

### Phase 1: LLM Enhancement - DeepSeek R1 Integration
- DeepSeek R1 API integration for superior script generation
- Claude 3.7 Sonnet as fallback and content processing system
- Dual-model architecture for optimized performance
- Database schema enhancements for future user management
- Token tracking instrumentation for usage monitoring

### Phase 2: Advanced Content Processing
- Document analysis and information extraction
- Web content processing capabilities
- Source attribution and metadata management
- Content structuring for optimized script generation
- Claude-DeepSeek handoff protocol implementation

### Phase 3: Web Search Integration
- FireCrawl MCP server integration
- Real-time information retrieval capabilities
- Web content acquisition for up-to-date scripts
- Source transparency and citation features
- Multi-source content testing and validation

### Phase 4: Analytics & Reporting
- Token usage analytics dashboard
- Cost tracking and projections
- CSV export with Google Sheets compatibility
- Usage pattern analysis
- Performance monitoring

### Phase 5: UI & User Experience Enhancements
- Document upload functionality
- URL input interface
- Search interface for information retrieval
- Source citation display
- Progress indicators for multi-stage processing
- Session-based content tracking
- Comprehensive testing and deployment

### Future Phases

#### User Management
- User registration and login system
- Secure profile management
- Session handling for application state
- Personal history panel for past scripts

#### API Key Integration
- **Dual API Key System:**
  - During onboarding, ask users if they have an ElevenLabs account
  - For users with accounts: Guide them to securely add their ElevenLabs API key
  - For users without accounts: Utilize the application's default API key
- Secure storage and encryption of user API keys
- Clear transparency about how API keys are used
- Option to remove API keys from the system

#### Enhanced Voice Options
- Voice preview feature before generating full voiceovers
- Voice customization options (speed, pitch, emphasis)
- Batch processing for multiple scripts
- Voice favorites and history

#### Advanced Features
- Project management for organizing scripts and voiceovers
- Team collaboration features
- Export options for various platforms
- Advanced editing tools for both scripts and audio

#### Monetization and Scaling
- Subscription tiers for different usage levels
- Enterprise features for high-volume users
- API for integration with other systems
- White-label solutions

## Implementation Notes

### API Key Security Considerations:
- All user API keys will be securely encrypted
- Keys will only be used for the specific operations requested by the user
- Users will maintain full control over their keys with ability to remove at any time
- Clear usage reporting to help users monitor their ElevenLabs consumption

### LLM Architecture Considerations:
- DeepSeek R1 provides superior script quality with 32K token output capacity
- Claude 3.7 Sonnet offers efficient content processing with 200K context window
- Multi-model approach optimizes cost efficiency while maximizing quality
- Source attribution ensures transparency and proper citation

### Voice ID Compatibility:
- The application will continue to support custom Voice IDs
- Users will need to add voices to their personal ElevenLabs collection before using them
- This is a limitation of the ElevenLabs platform: API access is restricted to voices in a user's collection

---

This roadmap is subject to change based on user feedback and market conditions. The core focus remains providing an easy-to-use solution for generating high-quality educational scripts and voiceovers. 