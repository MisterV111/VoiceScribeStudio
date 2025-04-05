# VoiceScribe Studio - Enhanced Implementation Plan

**Project Start Date:** March 23, 2025  
**Estimated Completion:** August 26, 2025 (Updated for Translation Feature)
**Current Status:** Planning Phase

## Project Overview

This implementation plan outlines the process of enhancing VoiceScribe Studio with a multi-LLM architecture and Model Context Protocol (MCP) server integrations to improve script generation quality, accuracy, and media production capabilities. The system will utilize DeepSeek R1 for high-quality script generation combined with Claude 3.7 Sonnet for content processing, various MCP servers for specialized functions, and direct API integrations for media enhancement.

## Architecture Summary

### Multi-Tier Enhanced System

1. **Data Acquisition Layer**
   - **FireCrawl**: Web content retrieval and extraction
   - **Perplexity MCP**: Fact-checking and knowledge enhancement
   - **Browser Tools MCP**: Direct URL content processing
   - **YouTube API**: Style and content reference extraction

2. **Content Processing Layer**
   - **Claude 3.7 Sonnet**: Document/web content analysis, **Translation Service**
   - **Memory MCP**: User preference and context retention
   - **Content verification system**: Cross-referencing and fact validation

3. **Script Generation Layer**
   - **DeepSeek R1**: High-quality script creation across all templates
   - **Template-specific formatting**: Professional output generation

4. **Media Enhancement Layer** (Premium Features)
   - **EverArt MCP**: Visual content generation
   - **Suno AI**: Background music generation
   - **Document Conversion MCP**: Professional export formats

5. **File Management Layer**
   - **File System MCP**: Content organization and metadata
   - **Version control**: Script iteration management
   - **Export system**: Multi-format document generation

## Implementation Phases & Milestones

### Phase 1: Foundation & DeepSeek R1 Integration
**Timeline: 2-3 weeks**

- [✓] DeepSeek API integration setup
- [✓] Modify script generation to use DeepSeek
- [✓] Claude 3.7 fallback implementation
- [✓] Database schema update for user-ready fields
- [✓] Token tracking instrumentation
- [✓] Cross-template testing suite
  - [✓] Testing framework implementation
  - [✓] Enhanced user interface with formatted results display
  - [✓] Test configuration visualization improvements
  - [✓] Secure admin interface with authentication
  - [✓] Public/admin interface separation
  - [ ] Complete test coverage across all templates
- [✓] MCP server management framework setup
- [✓] UI/UX Enhancements
  - [✓] Enhanced batch output display with styled download cards
  - [✓] Format preview functionality for multi-format generation
  - [✓] Improved HTML rendering for status messages
  - [✓] Visual styling improvements with better contrast
  - [✓] Responsive audio format grid with format-specific icons
  - [✓] Status messages with custom styling and enhanced readability

**Milestone:** Basic DeepSeek script generation functional with MCP framework and enhanced UI/UX

### Phase 2: Content Processing Enhancement
**Timeline: 3-4 weeks**

- [✓] **Backend:** Create content processing module (`content_analyzer.py`)
- [✓] **Backend:** Implement Claude 3.7 API integration for document analysis
- [✓] **Backend:** Design initial structured content format (JSON) for analysis output
- [✓] **Backend:** Develop Claude-DeepSeek handoff protocol (Update DeepSeek prompt)
- [✓] **UI:** Implement Gradio file upload component for documents
  - [ ] Add token counting logic for uploaded files (`tiktoken`)
  - [ ] Implement `.upload()` event handler to check file size
  - [ ] Add UI warning message for large documents (>75k tokens)
- [✓] **UI:** Implement Gradio input component for YouTube URLs
- [✓] **UI:** Implement Gradio input component for general URLs
- [✓] **UI:** Create unified reference input UI with conditional visibility
- [ ] **Integration:** Connect file upload UI to the backend analysis module
- [ ] **Backend:** Direct YouTube API integration for style reference
- [ ] **Backend:** Style reference processing module
- [ ] **Integration:** Connect YouTube URL UI to backend processing
- [ ] **Backend:** Implement *basic* URL content fetching (Note: Robust MCP-based fetching in Phase 4)
- [ ] **Integration:** Connect general URL UI to basic fetching & analysis pipeline
- [ ] **Humanize Feature:** LLM-powered script optimization for voiceover delivery
  - [ ] Research professional voiceover timing & emphasis techniques
  - [ ] Develop standardized markup syntax for pauses, emphasis, and emotion
  - [ ] Create LLM prompt template with voiceover best practices
  - [ ] Implement backend processing module for script transformation
  - [ ] Design UI with single-click "Humanize" button in script editor
  - [ ] Testing across various script types and templates
- [ ] **Backend:** Implement source tracking system development
- [ ] **Backend:** Token usage storage implementation for analysis steps
- [ ] **Backend:** Memory MCP integration for context retention
- [ ] **Testing:** Test document, YouTube, and basic URL analysis pipelines

**Milestone:** Enhanced content processing pipeline functional with Document Upload, YouTube URL, Basic General URL input interfaces, and Humanize formatting feature.

### Phase 3: Translation Feature Implementation
**Timeline: 4-5 weeks** (New Phase)

- [ ] Design `TranslationService` backend module
- [ ] Implement Claude 3.7 prompt templates for translation (context-aware)
- [ ] Develop template-specific glossary structure (JSON) & management system
- [ ] Build translation UI components (dropdown, button, display area) in Editing Tab
- [ ] Integrate `TranslationService` with Claude 3.7 Sonnet API
- [ ] Develop initial glossaries for core templates (e.g., Music, Science)
- [ ] Implement end-to-end translation workflow (frontend to backend)
- [ ] Add translation operations to token usage tracking
- [ ] Unit, integration, and specialized character set testing for translation
- [ ] Optimize translation performance (caching, prompt efficiency)

**Milestone:** Core translation functionality operational with initial glossaries

### Phase 4: Multi-Source Data Acquisition
**Timeline: 3-4 weeks**

- [ ] FireCrawl MCP server integration
- [ ] Perplexity MCP integration for fact verification
- [ ] Browser Tools MCP for **robust** URL processing (Enhances Phase 2 basic fetching)
- [ ] Source selection logic implementation
- [ ] Unified data pipeline development
- [ ] FireCrawl-Claude-Perplexity workflow
- [ ] Source metadata collection implementation
- [ ] Analytics framework development
- [ ] Premium feature access control system
- [ ] Multi-source testing

**Milestone:** Comprehensive data acquisition system functional with robust URL processing.

### Phase 5: Media Enhancement & Output Management
**Timeline: 3 weeks**

- [ ] File System MCP integration
- [ ] Document Conversion MCP implementation
- [ ] EverArt MCP for visual content generation
- [ ] Suno AI integration for background music
- [ ] Content organization system
- [ ] Export format configuration
- [ ] Media asset management system
- [ ] Premium feature tier implementation
- [ ] Output testing across formats

**Milestone:** Media enhancement and output management functional

### Phase 6: Analytics, UI Enhancement & Deployment
**Timeline: 3-4 weeks**

- [ ] Token usage dashboard creation
- [ ] API cost monitoring across services
- [ ] Premium feature usage tracking
- [ ] Audio preview for generated music
- [ ] Visual content gallery
- [ ] Source citation UI component
- [ ] Session tracking implementation
- [ ] Progress indicators for multi-stage processing
- [ ] Admin analytics interface
- [ ] Comprehensive testing
- [ ] Production deployment

**Milestone:** Enhanced system fully deployed with Translation Feature

## Technical Specifications

### API Integration Details

**DeepSeek R1:**
- Base URL: [TBD]
- Authentication method: API key
- Response format: JSON
- Rate limits: [TBD]
- Timeout settings: [TBD]

**Claude 3.7 Sonnet:**
- Base URL: https://api.anthropic.com/v1/messages
- Authentication method: API key
- Response format: JSON
- Rate limits: Account-specific
- Timeout settings: 120s

**FireCrawl:**
- Self-hosted configuration
- Access mechanism: [TBD]
- Configuration parameters: [TBD]

**Perplexity API:**
- Base URL: https://api.perplexity.ai
- Authentication method: API key
- Model options: sonar-deep-research, sonar-reasoning-pro
- Timeout settings: 60s

**YouTube Data API:**
- Base URL: https://www.googleapis.com/youtube/v3
- Authentication method: API key
- Rate limits: 10,000 units/day (free tier)
- Key endpoints: videos, captions, search

**Suno AI:**
- Base URL: https://api.suno.ai
- Authentication method: API key
- Response format: JSON
- Rate limits: [TBD]
- Generation parameters: mood, style, duration

### Translation Service Details (New Section)
- **Primary LLM:** Claude 3.7 Sonnet
- **Target Languages:** French, Spanish, German, Italian, Portuguese, Russian, Japanese, Korean, Chinese
- **Glossary Format:** JSON, structured by template and target language
- **Prompt Strategy:** Contextual prompts including role definition, task specification, template context, glossary terms, and format instructions.

### MCP Server Management

**Server Configurations:**
- File System MCP
- Browser Tools MCP
- Memory MCP
- Document Conversion MCP
- EverArt MCP

**Framework Components:**
- Server lifecycle management
- Request routing
- Error handling
- Authentication flow
- Premium feature gating

### Token Management System

**Tracking Components:**
- Input token counters by source
- Output token counters by template
- Model usage distribution tracking
- API call tracking by service
- Cost calculation formulas
- Usage pattern analysis
- **Translation operation tracking** (New)

**Storage Schema:**
- Token metrics database table structure
- API usage metrics structure
- Aggregation methodology
- Retention policies

## Testing Strategy

### Unit Testing
- API client tests
- Token counter validation
- Content processing verification
- Source attribution accuracy
- MCP server communication
- **Translation prompt construction** (New)
- **Glossary injection validation** (New)

### Integration Testing
- End-to-end script generation
- Multi-model pipeline testing
- Error handling verification
- Fallback mechanism validation
- MCP service coordination
- **Translation workflow testing** (New)

### Performance Testing
- Response time benchmarking
- Token efficiency analysis
- Memory usage profiling
- Load testing parameters
- Multi-service latency
- **Translation response time benchmarking** (New)

## Risk Management

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| DeepSeek API instability | Medium | High | Robust fallback to Claude, comprehensive error handling |
| Token costs exceed projections | Medium | Medium | Usage caps, monitoring alerts, optimization reviews |
| Content processing quality issues | Low | High | Extensive prompt engineering, quality review cycles |
| Integration complexity delays | Medium | Medium | Modular approach, clear interfaces, parallel workstreams |
| MCP server compatibility issues | Medium | Medium | Testing framework, fallback capabilities, direct API alternatives |
| API rate limiting | High | Medium | Intelligent caching, queue management, premium tier controls |
| **Translation Quality/Accuracy** | Medium | High | Contextual prompts, glossary system, quality review cycles, potential fallback (manual edit) |
| **Glossary Maintenance Overhead** | Medium | Medium | Start with core templates, community contribution model?, automated suggestions? |

## Progress Tracking

| Phase | Status | Start Date | Target End Date | Actual End Date | Notes |
|-------|--------|------------|----------------|----------------|-------|
| 1     | Completed | March 25, 2025 | April 15, 2025 | April 12, 2025 | Foundation - Cross-template testing suite enhanced with formatted UI and authentication. Additional UI/UX improvements for batch output and status messages completed ahead of schedule. |
| 2     | Not Started | April 16, 2025 | May 14, 2025 |  | Content Processing Core |
| 3     | Not Started | May 15, 2025 | June 19, 2025 |  | **Translation Feature** (New) |
| 4     | Not Started | June 20, 2025 | July 18, 2025 |  | Multi-Source Data (Shifted) |
| 5     | Not Started | July 19, 2025 | August 8, 2025 |  | Media/Output (Shifted) |
| 6     | Not Started | August 9, 2025 | Sept 6, 2025 |  | UI/Deployment (Shifted) |

## Cost Projections

### API Cost Estimates
- DeepSeek R1: ~$10-20 per 1M output tokens
- Claude 3.7 Sonnet: $3 per 1M input tokens, $15 per 1M output tokens
- FireCrawl: Underlying search API costs only
- Perplexity: ~$0.15-0.20 per query (deep research)
- YouTube API: Free tier with 10,000 units/day
- Suno AI: ~$0.10-0.30 per music generation (depends on length)
- **Claude 3.7 Translation (Est.):** ~$0.045 per average translation (2.5k input + 2.5k output tokens) (New)

### Monthly Projections (1,000 scripts, **assuming 500 translations**)
- Content Processing: ~$50-100
- Script Generation: ~$100-200
- Web Search & Verification: ~$50-80
- YouTube References: ~$0-20
- Music Generation (Premium): ~$50-100
- **Translation Feature:** ~$20-25 (500 * $0.045) (New)
- **Updated Total:** ~$270-525/month (Adjusted)

## Premium Feature Tiers

### Basic Tier
- Standard script generation
- Basic voice synthesis
- Simple document exports

### Premium Tier
- Enhanced accuracy with Perplexity verification
- YouTube style reference processing
- Professional document exports
- Background music generation
- Visual content generation
- **Advanced Translation Features (Potential):** (e.g., more languages, dialect control, translation memory - TBD if premium) (New)

## Success Metrics

- [ ] Script quality improvement measured through user edits reduction
- [ ] Successful handling of real-time information in scripts
- [ ] Factual accuracy improvement with verification services
- [ ] System reliability with 99.5%+ uptime
- [ ] Source attribution accuracy > 95%
- [ ] Token usage optimization achieving <5% waste
- [ ] Cost projections accurate within 10% of actual costs
- [ ] Premium feature adoption rate > 15%
- [ ] **Translation Quality:** Manual review scores > 4.0/5.0 (New)
- [ ] **Translation Performance:** <5s completion for average scripts (New)
- [ ] **Translation User Satisfaction:** >85% positive feedback (New)

## Appendix

### Model Capabilities Overview

**DeepSeek R1:**
- 671B parameter MoE model (37B active parameters)
- 128K token input context
- 32K token output limit
- Superior creative writing capabilities

**Claude 3.7 Sonnet:**
- 200K token context window
- Strong document analysis capabilities
- Efficient content processing
- Cost-effective for large input processing

**Suno AI:**
- AI music generation from text descriptions
- Multiple style and genre options
- Commercial-use licensing available
- Length and structure customization

### Future Considerations

- User account system integration
- Personal history panel
- Advanced analytics dashboard
- Usage-based pricing tiers
- Additional LLM options
- Mobile application development
- Enterprise deployment options 

reference_type = gr.Radio(
    label="Input Type",
    choices=["None", "Document Upload", "Web URL Reference", "YouTube Link Reference"],
    value="None"
)

# Document Upload Input 
with gr.Column(visible=False) as doc_upload_group:
    # Add a placeholder for the size warning message
    doc_size_warning = gr.Markdown(visible=False, elem_classes=["warning-text"])
    document_upload_input = gr.File(
        label="Upload Document",
        file_count="single",
    ) 