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

### Phase 1: User Management
- User registration and login system
- Secure profile management
- Session handling for application state

### Phase 2: API Key Integration
- **Dual API Key System:**
  - During onboarding, ask users if they have an ElevenLabs account
  - For users with accounts: Guide them to securely add their ElevenLabs API key
  - For users without accounts: Utilize the application's default API key
- Secure storage and encryption of user API keys
- Clear transparency about how API keys are used
- Option to remove API keys from the system

### Phase 3: Enhanced Voice Options
- Voice preview feature before generating full voiceovers
- Voice customization options (speed, pitch, emphasis)
- Batch processing for multiple scripts
- Voice favorites and history

### Phase 4: Advanced Features
- Project management for organizing scripts and voiceovers
- Team collaboration features
- Export options for various platforms
- Analytics for usage tracking
- Advanced editing tools for both scripts and audio

### Phase 5: Monetization and Scaling
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

### Voice ID Compatibility:
- The application will continue to support custom Voice IDs
- Users will need to add voices to their personal ElevenLabs collection before using them
- This is a limitation of the ElevenLabs platform: API access is restricted to voices in a user's collection

---

This roadmap is subject to change based on user feedback and market conditions. The core focus remains providing an easy-to-use solution for generating high-quality educational scripts and voiceovers. 