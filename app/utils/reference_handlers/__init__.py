"""
Reference handlers for document, web, and YouTube content.

This module provides utilities for extracting and analyzing content from:
- Documents (.txt, .md, .pdf, .docx)
- Web URLs
- YouTube videos
"""

from app.utils.reference_handlers.web_utils import extract_web_content
from app.utils.reference_handlers.youtube_utils import extract_youtube_transcript 