# Context Reference Input Features

VoiceScribe Studio now supports generating scripts based on various reference sources through the Context Reference Input feature. This document explains how to use these features and best practices.

## Overview

The Context Reference Input allows you to provide additional context to the AI when generating scripts. You can choose from three different reference types:

1. **Document Upload**: Upload a document file (.txt, .md, .pdf, .docx)
2. **Web URL Reference**: Provide a URL to extract content from a web page
3. **YouTube Link Reference**: Use a YouTube video's transcript as context

These features help the AI generate more accurate, relevant, and informative scripts by using the provided materials as references.

## Using Context Reference Input

### General Usage

1. In the "Generate Script" tab, locate the "Context / Reference Input" section
2. Choose a reference type using the radio buttons (None, Document Upload, Web URL Reference, YouTube Link Reference)
3. Provide the appropriate input based on your selection
4. Fill in the other script generation fields as usual
5. Click "Generate Script"

The AI will incorporate the reference content into its script generation process, resulting in a more informed output.

### Document Upload

**Supported File Types:**
- Text files (.txt)
- Markdown files (.md)
- PDF documents (.pdf)
- Word documents (.docx)

**File Size Limit:** 75,000 tokens (approximately 60,000 words)

**Best Practices:**
- Use clearly formatted documents with well-structured content
- Avoid extremely large documents as they may be truncated
- For best results, use documents directly relevant to your script topic

**Process:**
1. Select "Document Upload" as the Input Type
2. Upload your document using the file uploader
3. The system will automatically extract and process the content
4. A warning will appear if your document exceeds the token limit

### Web URL Reference

**Supported URLs:**
- Most standard web pages with text content
- News articles, blog posts, educational resources, etc.

**Best Practices:**
- Use URLs that point to information-rich pages
- Avoid pages with minimal text content
- For optimal results, use pages with clear, well-structured text
- Pages requiring login or with heavy JavaScript may not extract properly

**Process:**
1. Select "Web URL Reference" as the Input Type
2. Enter the complete URL (including http:// or https://)
3. The system will validate the URL format
4. When you click "Generate Script," the content will be extracted automatically

### YouTube Link Reference

**Supported URLs:**
- Standard YouTube watch URLs (https://www.youtube.com/watch?v=VIDEO_ID)
- YouTube Shorts URLs
- Shortened youtu.be URLs
- Embed URLs

**Requirements:**
- The video must have captions/transcripts available
- English transcripts are preferred, but the system will try to find available transcripts in other languages if English is not available

**Best Practices:**
- Use videos with high-quality, accurate captions/transcripts
- Educational content, interviews, and presentations generally work best
- Verify the video has captions before using (look for the CC button in YouTube player)

**Process:**
1. Select "YouTube Link Reference" as the Input Type
2. Enter the YouTube video URL
3. The system will validate the URL format
4. When you click "Generate Script," the transcript will be extracted automatically

## Technical Details

### Document Processing
Documents are processed locally with text extraction based on file type. Token counting uses the `tiktoken` library with the `cl100k_base` encoding (compatible with Claude/GPT models) to measure content size.

### Web Content Extraction
Web content is extracted using a combination of `trafilatura` (primary) and `BeautifulSoup` (fallback) libraries. The extraction process focuses on retrieving the main content while filtering out navigation, ads, and other non-essential elements.

### YouTube Transcript Extraction
YouTube transcripts are obtained using the `youtube-transcript-api` library. The system attempts to retrieve manually created transcripts first, falling back to auto-generated ones if necessary. Multiple language support is provided with preference for English.

## Troubleshooting

### Document Upload Issues
- If your document fails to upload, check that it's one of the supported file types
- Large documents may take longer to process
- If a file looks corrupted, try resaving it in a different format (e.g., from .docx to .txt)

### Web URL Issues
- If content extraction fails, try a different URL from the same source
- Some websites block content extraction; news sites and educational resources typically work best
- Ensure you're using the full URL including the protocol (https://)

### YouTube Issues
- If transcript extraction fails, verify the video has captions available
- Some creators disable transcripts for their videos
- Try another video on the same topic if transcript extraction fails
- Ensure you're using a direct link to a YouTube video, not a playlist or channel 