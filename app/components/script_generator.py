import gradio as gr
import os
from app.utils.llm_clients import generate_script
import tiktoken
import tempfile
import io
from pathlib import Path
import re
import urllib.parse
import json  # Add this import if it's not already there

# Below imports for document processing
try:
    import fitz  # PyMuPDF
    import docx
    HAS_DOCUMENT_LIBS = True
except ImportError:
    HAS_DOCUMENT_LIBS = False
    print("Warning: Document processing libraries not installed. PDF and DOCX support limited.")

# Import content analysis components
# The analyze_document_content will be imported through ensure_analyze_function when needed

# Attempt to import reference handlers
try:
    from app.utils.reference_handlers.web_utils import extract_web_content
    from app.utils.reference_handlers.youtube_utils import extract_youtube_transcript
    HAS_REFERENCE_HANDLERS = True
except ImportError:
    HAS_REFERENCE_HANDLERS = False
    print("Warning: Reference handlers not found. Creating fallback implementations.")
    
    # Fallback implementation for web content extraction
    def extract_web_content(url):
        """Fallback implementation for web content extraction"""
        try:
            import requests
            from bs4 import BeautifulSoup
            
            response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.extract()
                
            # Get text
            text = soup.get_text()
            
            # Break into lines and remove leading/trailing space
            lines = (line.strip() for line in text.splitlines())
            # Break multi-headlines into a line each
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            # Drop blank lines
            text = '\n'.join(chunk for chunk in chunks if chunk)
            
            return text, None
        except Exception as e:
            return None, f"Error extracting web content: {str(e)}"
    
    # Fallback implementation for YouTube transcript extraction
    def extract_youtube_transcript(url):
        """Fallback implementation for YouTube transcript extraction"""
        try:
            from youtube_transcript_api import YouTubeTranscriptApi
            
            # Extract video ID from URL
            video_id = None
            patterns = [
                r'(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([\w-]+)',
                r'youtube\.com\/watch.*?[?&]v=([\w-]+)',
                r'youtube\.com\/shorts\/([\w-]+)'
            ]
            
            for pattern in patterns:
                match = re.search(pattern, url)
                if match:
                    video_id = match.group(1)
                    break
                    
            if not video_id:
                return None, "Could not extract YouTube video ID from URL"
                
            # Get transcript
            transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
            transcript_text = " ".join([item['text'] for item in transcript_list])
            
            return transcript_text, None
        except Exception as e:
            return None, f"Error extracting YouTube transcript: {str(e)}"

# Add variables to store reference text and analysis results
document_text = None
document_analysis = None
web_url_content = None
youtube_transcript = None

# Make sure analyze_document_content is a function
def ensure_analyze_function(text):
    """Fallback implementation for document analysis when the real function is not available"""
    real_analyze = None
    try:
        # Try to import the function from content_analyzer
        from app.components.content_analyzer import analyze_document_content as real_analyze
        
        # Test if the imported function is callable
        if callable(real_analyze):
            try:
                result = real_analyze(text)
                # Check that the result is a dictionary - if not, create a fallback
                if not isinstance(result, dict):
                    print(f"Warning: analyze_document_content returned non-dict result: {type(result)}")
                    return {
                        "summary": f"Analysis result was {type(result).__name__}, expected dict",
                        "key_topics": ["Result type error"],
                        "structure_outline": ["Content analysis returned invalid type"],
                        "extracted_keywords": ["error", "invalid result"]
                    }
                
                # Ensure all required keys are present
                required_keys = ['summary', 'key_topics', 'structure_outline', 'extracted_keywords']
                for key in required_keys:
                    if key not in result:
                        print(f"Warning: analyze_document_content result missing required key: {key}")
                        # Add the missing key with a default value
                        if key == 'summary':
                            result[key] = "No summary available"
                        else:
                            result[key] = ["No data available"]
                
                # Ensure all list attributes are actually lists
                list_keys = ['key_topics', 'structure_outline', 'extracted_keywords']
                for key in list_keys:
                    if key in result and not isinstance(result[key], list):
                        print(f"Warning: {key} is not a list, converting")
                        if result[key] is None:
                            result[key] = []
                        else:
                            # Try to convert to a list if possible, otherwise use a default
                            try:
                                result[key] = [str(result[key])]
                            except:
                                result[key] = ["Conversion error"]
                
                return result
            except Exception as e:
                print(f"Error calling analyze_document_content: {e}")
                return {
                    "summary": f"Error during analysis execution: {str(e)}",
                    "key_topics": ["Error", "Analysis execution failed"],
                    "structure_outline": ["Error during content analysis"],
                    "extracted_keywords": ["error", "analysis", "execution", "failed"]
                }
        else:
            print(f"Warning: analyze_document_content is not callable, type: {type(real_analyze)}")
            # Return a basic analysis result
            return {
                "summary": "Content analysis unavailable",
                "key_topics": ["Unable to analyze document"],
                "structure_outline": ["Content analysis unavailable"],
                "extracted_keywords": ["analysis", "unavailable"]
            }
    except ImportError as e:
        print(f"Error importing analyze_document_content: {e}")
        # Return a basic analysis result
        return {
            "summary": "Content analysis module not available",
            "key_topics": ["Unable to analyze document"],
            "structure_outline": ["Content analysis unavailable"],
            "extracted_keywords": ["analysis", "unavailable"]
        }
    except Exception as e:
        print(f"Error using analyze_document_content: {e}")
        # Return a basic analysis result
        return {
            "summary": f"Error during content analysis: {str(e)}",
            "key_topics": ["Error", "Analysis unavailable"],
            "structure_outline": ["Content analysis unavailable"],
            "extracted_keywords": ["error", "analysis", "unavailable"]
        }

def extract_text_from_file(file_obj):
    """Extract text from various file formats and analyze content"""
    global document_text, document_analysis
    
    if not file_obj:
        return None, "No file provided."
    
    try:
        # Debug info about the file object
        print(f"File object type: {type(file_obj)}")
        print(f"File object attributes: {dir(file_obj)}")
        
        # Print all attributes and their values for debugging
        for attr in ['name', 'orig_name', 'path', 'file', 'filepath', 'filename']:
            if hasattr(file_obj, attr):
                value = getattr(file_obj, attr)
                print(f"  - {attr}: {value} (type: {type(value)})")
                
                # If it's a file attribute, check its attributes too
                if attr == 'file' and value is not None:
                    print(f"  - file attributes: {dir(value)}")
                    for subattr in ['name', 'path', 'mode']:
                        if hasattr(value, subattr):
                            subvalue = getattr(value, subattr)
                            print(f"    - file.{subattr}: {subvalue}")
        
        # Special handling for Gradio File components which return special object structure
        if hasattr(file_obj, 'name') and file_obj.name:
            # Modern Gradio (1.27+) returns FileData objects with direct .name
            print(f"Detected Gradio FileData object with name: {file_obj.name}")
        elif hasattr(file_obj, 'path') and file_obj.path:
            # Some versions use path attribute directly
            print(f"Detected object with path attribute: {file_obj.path}")
            if os.path.exists(file_obj.path):
                file_obj = file_obj.path  # Use the path directly
        elif isinstance(file_obj, dict) and 'name' in file_obj:
            # Some Gradio versions use a dict representation
            print(f"Detected Gradio File dict with name: {file_obj['name']}")
        elif isinstance(file_obj, tuple) and len(file_obj) == 2:
            # Older Gradio versions may return a tuple of (temp_path, orig_name)
            print(f"Detected Gradio tuple format: {file_obj}")
            temp_path, orig_name = file_obj
            if temp_path and os.path.exists(temp_path):
                print(f"Using temp_path from tuple: {temp_path}")
                file_obj = temp_path  # Use the path directly
            
        # Handle cases where Gradio returns a list of files even with file_count="single"
        if isinstance(file_obj, list) and len(file_obj) > 0:
            print(f"Unwrapping file object from list: {file_obj}")
            file_obj = file_obj[0]  # Take the first file
            
        # Get file extension
        file_path = None
        ext = None
        orig_name = None
        
        # Handle different possible file object types from Gradio
        if isinstance(file_obj, str):
            # Path string
            file_path = file_obj
            ext = os.path.splitext(file_path)[1].lower()
            print(f"File is a string path: {file_path}")
        elif isinstance(file_obj, bytes):
            # Direct bytes content - try to get name from orig_name if available
            orig_name = getattr(file_obj, 'orig_name', None)
            if orig_name:
                ext = os.path.splitext(orig_name)[1].lower()
            else:
                # Can't determine type from bytes, default to txt
                ext = '.txt'
            print(f"File is bytes content with orig_name: {orig_name}")
        elif hasattr(file_obj, 'name'):
            # File-like object with name
            file_path = file_obj.name
            ext = os.path.splitext(file_path)[1].lower()
            print(f"File has name attribute: {file_path}")
        elif hasattr(file_obj, 'orig_name'):
            # Gradio file object with orig_name
            orig_name = file_obj.orig_name
            ext = os.path.splitext(orig_name)[1].lower()
            print(f"File has orig_name attribute: {orig_name}")
        else:
            # Try as file-like object or Gradio's special format
            try:
                # Check if it's a Gradio UploadedFile or dictionary with file info
                if hasattr(file_obj, 'name'):
                    file_path = file_obj.name
                    ext = os.path.splitext(file_path)[1].lower()
                    print(f"Found name in file object: {file_path}")
                elif isinstance(file_obj, dict) and 'name' in file_obj:
                    file_path = file_obj['name']
                    ext = os.path.splitext(file_path)[1].lower()
                    print(f"File is a dict with name: {file_path}")
                elif hasattr(file_obj, 'file') and hasattr(file_obj.file, 'name'):
                    file_path = file_obj.file.name
                    ext = os.path.splitext(file_path)[1].lower()
                    print(f"File has nested file.name: {file_path}")
                else:
                    # Get attributes that might help identify the file
                    attrs = dir(file_obj)
                    print(f"No standard attributes found, available attrs: {attrs}")
                    # Look for interesting attributes
                    for attr in ['filepath', 'path', 'filename', 'file', 'data']:
                        if hasattr(file_obj, attr):
                            value = getattr(file_obj, attr)
                            print(f"Found attribute {attr}: {value}")
                    
                    # Last resort - try to read and treat as text
                    ext = '.txt'
                    print(f"Using default extension: {ext}")
            except Exception as e:
                print(f"Error determining file type: {e}")
                return None, "Could not determine file type."
                
        print(f"Determined file extension: {ext}")
        
        # Process based on file type
        if ext == '.txt':
            # Text file
            try:
                if isinstance(file_obj, bytes):
                    text = file_obj.decode('utf-8', errors='replace')
                elif hasattr(file_obj, 'read'):
                    # File-like object
                    content = file_obj.read()
                    if isinstance(content, bytes):
                        text = content.decode('utf-8', errors='replace')
                    else:
                        text = content
                else:
                    # Path
                    with open(file_obj, 'r', encoding='utf-8', errors='replace') as f:
                        text = f.read()
                
                document_text = text
                
                # Analyze the document content if text was extracted successfully
                try:
                    document_analysis = ensure_analyze_function(text)
                    if isinstance(document_analysis, dict) and "error" in document_analysis:
                        print(f"Warning: Document analysis error: {document_analysis['error']}")
                except Exception as e:
                    print(f"Error during document analysis: {e}")
                    document_analysis = None
                    
                return text, None
            except Exception as e:
                return None, f"Error processing text file: {str(e)}"
            
        elif ext == '.md':
            # Markdown file - treat as text
            try:
                if isinstance(file_obj, bytes):
                    text = file_obj.decode('utf-8', errors='replace')
                elif hasattr(file_obj, 'read'):
                    content = file_obj.read()
                    if isinstance(content, bytes):
                        text = content.decode('utf-8', errors='replace')
                    else:
                        text = content
                else:
                    # Path
                    with open(file_obj, 'r', encoding='utf-8', errors='replace') as f:
                        text = f.read()
                
                document_text = text
                
                # Analyze the document content if text was extracted successfully
                try:
                    document_analysis = ensure_analyze_function(text)
                    if isinstance(document_analysis, dict) and "error" in document_analysis:
                        print(f"Warning: Document analysis error: {document_analysis['error']}")
                except Exception as e:
                    print(f"Error during document analysis: {e}")
                    document_analysis = None
                    
                return text, None
            except Exception as e:
                return None, f"Error processing markdown file: {str(e)}"
            
        elif ext == '.pdf':
            if not HAS_DOCUMENT_LIBS:
                return None, "PDF processing libraries not installed."
                
            # Create a temporary file to work with
            temp_path = None
            try:
                with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp:
                    # Handle various file object types
                    print(f"Processing PDF file: {type(file_obj)}")
                    
                    if isinstance(file_obj, bytes):
                        print("Writing bytes directly to temp file")
                        temp.write(file_obj)
                    elif isinstance(file_obj, str):
                        print("Opening file path and writing content")
                        with open(file_obj, 'rb') as src:
                            temp.write(src.read())
                    elif hasattr(file_obj, 'read'):
                        try:
                            print("Using read() method on file object")
                            content = file_obj.read()
                            temp.write(content if isinstance(content, bytes) else content.encode('utf-8'))
                        except Exception as read_err:
                            print(f"Error reading file: {read_err}")
                            # Try alternative approaches
                            if hasattr(file_obj, 'file') and hasattr(file_obj.file, 'read'):
                                print("Trying nested file.read()")
                                content = file_obj.file.read()
                                temp.write(content if isinstance(content, bytes) else content.encode('utf-8'))
                            elif hasattr(file_obj, 'name') or isinstance(file_obj, dict) and 'name' in file_obj:
                                # Try to open the file by name
                                filename = getattr(file_obj, 'name', None) or file_obj.get('name')
                                print(f"Opening file by name: {filename}")
                                with open(filename, 'rb') as src:
                                    temp.write(src.read())
                            else:
                                raise ValueError("Could not read file content")
                    elif isinstance(file_obj, dict) and 'name' in file_obj:
                        print(f"File is dictionary with name: {file_obj['name']}")
                        if 'content' in file_obj:
                            # Some APIs provide content directly
                            content = file_obj['content']
                            temp.write(content if isinstance(content, bytes) else content.encode('utf-8'))
                        else:
                            # Try to open the file by name
                            with open(file_obj['name'], 'rb') as src:
                                temp.write(src.read())
                    elif hasattr(file_obj, 'filepath') and file_obj.filepath:
                        # Handle the case where filepath is provided
                        print(f"Using filepath attribute: {file_obj.filepath}")
                        with open(file_obj.filepath, 'rb') as src:
                            temp.write(src.read())
                    else:
                        # Try to extract information about the file
                        filepath = None
                        for attr_name in ['filepath', 'path', 'filename', 'name', 'orig_name']:
                            if hasattr(file_obj, attr_name):
                                filepath = getattr(file_obj, attr_name)
                                if filepath:
                                    print(f"Found path from attribute {attr_name}: {filepath}")
                                    break
                                    
                        if filepath:
                            # Read content from the filepath
                            with open(filepath, 'rb') as src:
                                temp.write(src.read())
                        else:
                            # Last resort - try to serialize the object itself
                            temp.write(str(file_obj).encode('utf-8'))
                            print("Warning: Could not extract file content properly")
                            
                    temp_path = temp.name
                    print(f"Created temporary file: {temp_path}")
                
                # Extract text from PDF
                try:
                    print(f"Opening PDF with PyMuPDF: {temp_path}")
                    doc = fitz.open(temp_path)
                    text = ""
                    for page in doc:
                        text += page.get_text()
                    doc.close()
                    print(f"Successfully extracted text from PDF: {len(text)} chars")
                    
                    # Store text for script generation
                    document_text = text
                    
                    # Analyze the document content if text was extracted successfully
                    try:
                        document_analysis = ensure_analyze_function(text)
                        if isinstance(document_analysis, dict) and "error" in document_analysis:
                            print(f"Warning: Document analysis error: {document_analysis['error']}")
                    except Exception as e:
                        print(f"Error during document analysis: {e}")
                        document_analysis = None
                    
                    return text, None
                except Exception as pdf_error:
                    error_msg = f"Error processing PDF: {str(pdf_error)}"
                    print(error_msg)
                    return None, error_msg
            except Exception as e:
                error_msg = f"Error preparing PDF file: {str(e)}"
                print(error_msg)
                return None, error_msg
            finally:
                # Clean up temp file
                if temp_path and os.path.exists(temp_path):
                    try:
                        os.unlink(temp_path)
                        print(f"Cleaned up temporary file: {temp_path}")
                    except Exception as clean_error:
                        print(f"Error cleaning up temporary file: {clean_error}")
                        pass
                
        elif ext == '.docx':
            if not HAS_DOCUMENT_LIBS:
                return None, "DOCX processing libraries not installed."
                
            # Create a temporary file to work with
            temp_path = None
            try:
                with tempfile.NamedTemporaryFile(delete=False, suffix='.docx') as temp:
                    # Handle various file object types
                    print(f"Processing DOCX file: {type(file_obj)}")
                    
                    if isinstance(file_obj, bytes):
                        print("Writing bytes directly to temp file")
                        temp.write(file_obj)
                    elif isinstance(file_obj, str):
                        print("Opening file path and writing content")
                        with open(file_obj, 'rb') as src:
                            temp.write(src.read())
                    elif hasattr(file_obj, 'read'):
                        try:
                            print("Using read() method on file object")
                            content = file_obj.read()
                            temp.write(content if isinstance(content, bytes) else content.encode('utf-8'))
                        except Exception as read_err:
                            print(f"Error reading file: {read_err}")
                            # Try alternative approaches
                            if hasattr(file_obj, 'file') and hasattr(file_obj.file, 'read'):
                                print("Trying nested file.read()")
                                content = file_obj.file.read()
                                temp.write(content if isinstance(content, bytes) else content.encode('utf-8'))
                            elif hasattr(file_obj, 'name') or isinstance(file_obj, dict) and 'name' in file_obj:
                                # Try to open the file by name
                                filename = getattr(file_obj, 'name', None) or file_obj.get('name')
                                print(f"Opening file by name: {filename}")
                                with open(filename, 'rb') as src:
                                    temp.write(src.read())
                            else:
                                raise ValueError("Could not read file content")
                    elif isinstance(file_obj, dict) and 'name' in file_obj:
                        print(f"File is dictionary with name: {file_obj['name']}")
                        if 'content' in file_obj:
                            # Some APIs provide content directly
                            content = file_obj['content']
                            temp.write(content if isinstance(content, bytes) else content.encode('utf-8'))
                        else:
                            # Try to open the file by name
                            with open(file_obj['name'], 'rb') as src:
                                temp.write(src.read())
                    elif hasattr(file_obj, 'filepath') and file_obj.filepath:
                        # Handle the case where filepath is provided
                        print(f"Using filepath attribute: {file_obj.filepath}")
                        with open(file_obj.filepath, 'rb') as src:
                            temp.write(src.read())
                    else:
                        # Try to extract information about the file
                        filepath = None
                        for attr_name in ['filepath', 'path', 'filename', 'name', 'orig_name']:
                            if hasattr(file_obj, attr_name):
                                filepath = getattr(file_obj, attr_name)
                                if filepath:
                                    print(f"Found path from attribute {attr_name}: {filepath}")
                                    break
                                    
                        if filepath:
                            # Read content from the filepath
                            with open(filepath, 'rb') as src:
                                temp.write(src.read())
                        else:
                            # Last resort - try to serialize the object itself
                            temp.write(str(file_obj).encode('utf-8'))
                            print("Warning: Could not extract file content properly")
                            
                    temp_path = temp.name
                    print(f"Created temporary file: {temp_path}")
                
                # Extract text from DOCX
                try:
                    print(f"Opening DOCX with python-docx: {temp_path}")
                    doc = docx.Document(temp_path)
                    text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
                    print(f"Successfully extracted text from DOCX: {len(text)} chars")
                    
                    # Store text for script generation
                    document_text = text
                    
                    # Analyze the document content if text was extracted successfully
                    try:
                        document_analysis = ensure_analyze_function(text)
                        if isinstance(document_analysis, dict) and "error" in document_analysis:
                            print(f"Warning: Document analysis error: {document_analysis['error']}")
                    except Exception as e:
                        print(f"Error during document analysis: {e}")
                        document_analysis = None
                    
                    return text, None
                except Exception as docx_error:
                    error_msg = f"Error processing DOCX: {str(docx_error)}"
                    print(error_msg)
                    return None, error_msg
            except Exception as e:
                error_msg = f"Error preparing DOCX file: {str(e)}"
                print(error_msg)
                return None, error_msg
            finally:
                # Clean up temp file
                if temp_path and os.path.exists(temp_path):
                    try:
                        os.unlink(temp_path)
                        print(f"Cleaned up temporary file: {temp_path}")
                    except Exception as clean_error:
                        print(f"Error cleaning up temporary file: {clean_error}")
                        pass
        else:
            return None, f"Unsupported file type: {ext}"
            
    except Exception as e:
        return None, f"Error processing file: {str(e)}"

def count_tokens(text):
    """Count tokens in text using tiktoken"""
    try:
        encoding = tiktoken.get_encoding("cl100k_base")
        return len(encoding.encode(text))
    except Exception as e:
        print(f"Error counting tokens: {e}")
        # Fallback: estimate ~4 chars per token
        return len(text) // 4

def process_uploaded_document(file_obj):
    """Process uploaded document, count tokens, and return warning if needed"""
    global document_text, document_analysis
    
    if not file_obj:
        return gr.update(visible=False)
    
    print(f"Processing uploaded document: {type(file_obj)}")
    
    # Extract text from file
    try:
        text, error = extract_text_from_file(file_obj)
        print(f"Extracted text: {type(text)}, error: {error}")
    except Exception as e:
        print(f"Error in extract_text_from_file: {e}")
        return gr.update(visible=True, value=f"⚠️ **Error:** Error extracting text: {str(e)}")
    
    if error:
        return gr.update(visible=True, value=f"⚠️ **Error:** {error}")
        
    if not text:
        return gr.update(visible=False)
        
    # Count tokens
    try:
        token_count = count_tokens(text)
        word_count = len(text.split())
        print(f"Token count: {token_count}, word count: {word_count}")
    except Exception as e:
        print(f"Error counting tokens: {e}")
        return gr.update(visible=True, value=f"⚠️ **Error:** Error counting tokens: {str(e)}")
    
    # Check if file exceeds token limit
    TOKEN_LIMIT = 75000
    if token_count > TOKEN_LIMIT:
        warning = (
            f"⚠️ **Warning:** File size exceeds recommended limit of {TOKEN_LIMIT:,} tokens. "
            f"Current size: {token_count:,} tokens / {word_count:,} words. "
            "Processing may be slow or incomplete."
        )
        return gr.update(visible=True, value=warning)
    
    # File is within limits
    info = f"📊 **File Statistics:** {token_count:,} tokens / {word_count:,} words"
    return gr.update(visible=True, value=info)

def process_web_url(url):
    """Process web URL and extract content"""
    global web_url_content
    
    if not url or not url.strip():
        return gr.update(visible=False)
        
    # Basic URL validation
    if not url.startswith(('http://', 'https://')):
        return gr.update(visible=True, value="⚠️ **Error:** URL must start with http:// or https://")
        
    try:
        # Extract content from URL
        content, error = extract_web_content(url)
        
        if error:
            return gr.update(visible=True, value=f"⚠️ **Error:** {error}")
            
        if not content:
            return gr.update(visible=True, value="⚠️ **Error:** No content extracted from URL")
            
        # Store content for script generation
        web_url_content = content
        
        # Count tokens and words
        token_count = count_tokens(content)
        word_count = len(content.split())
        
        # Check if content exceeds token limit
        TOKEN_LIMIT = 75000
        if token_count > TOKEN_LIMIT:
            warning = (
                f"⚠️ **Warning:** Web content exceeds recommended limit of {TOKEN_LIMIT:,} tokens. "
                f"Current size: {token_count:,} tokens / {word_count:,} words. "
                "Content will be truncated for processing."
            )
            return gr.update(visible=True, value=warning)
        
        # Content is within limits
        info = f"📊 **Web Content Stats:** {token_count:,} tokens / {word_count:,} words extracted"
        return gr.update(visible=True, value=info)
        
    except Exception as e:
        return gr.update(visible=True, value=f"⚠️ **Error:** Could not process URL: {str(e)}")

def process_youtube_url(url):
    """Process YouTube URL and extract transcript"""
    global youtube_transcript
    
    if not url or not url.strip():
        return gr.update(visible=False)
        
    # Basic YouTube URL validation
    youtube_patterns = [
        r'(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)',
        r'youtube\.com\/watch.*?[?&]v=',
        r'youtube\.com\/shorts\/'
    ]
    
    valid_url = any(re.search(pattern, url) for pattern in youtube_patterns)
    if not valid_url:
        return gr.update(visible=True, value="⚠️ **Error:** Not a valid YouTube URL")
        
    try:
        # Extract transcript from YouTube video
        transcript, error = extract_youtube_transcript(url)
        
        if error:
            return gr.update(visible=True, value=f"⚠️ **Error:** {error}")
            
        if not transcript:
            return gr.update(visible=True, value="⚠️ **Error:** No transcript available for this video")
            
        # Store transcript for script generation
        youtube_transcript = transcript
        
        # Count tokens and words
        token_count = count_tokens(transcript)
        word_count = len(transcript.split())
        
        # Check if transcript exceeds token limit
        TOKEN_LIMIT = 75000
        if token_count > TOKEN_LIMIT:
            warning = (
                f"⚠️ **Warning:** Transcript exceeds recommended limit of {TOKEN_LIMIT:,} tokens. "
                f"Current size: {token_count:,} tokens / {word_count:,} words. "
                "Transcript will be truncated for processing."
            )
            return gr.update(visible=True, value=warning)
        
        # Transcript is within limits
        info = f"📊 **Transcript Stats:** {token_count:,} tokens / {word_count:,} words extracted"
        return gr.update(visible=True, value=info)
        
    except Exception as e:
        return gr.update(visible=True, value=f"⚠️ **Error:** Could not process YouTube URL: {str(e)}")

def create_script(prompt, subject, length, audience, tone, template="General", context="", reference_type="None"):
    """Generate a script using the best available LLM"""
    try:
        if not prompt or not prompt.strip():
            return "Please provide a prompt for script generation.", None
        
        # Combine context with reference content if available
        combined_context = context
        
        # Add reference content based on type
        global document_text, document_analysis, web_url_content, youtube_transcript
        
        print(f"Reference type: {reference_type}")
        print(f"document_text type: {type(document_text)}")
        # Make sure document_analysis is a dictionary or None before proceeding
        if document_analysis is not None and not isinstance(document_analysis, dict):
            print(f"Warning: document_analysis is not a dictionary: {type(document_analysis)}")
            print(f"Resetting document_analysis to None")
            document_analysis = None
        print(f"document_analysis type: {type(document_analysis)}")
        
        if reference_type == "Document Upload":
            if document_text is None:
                print("Warning: Document Upload selected but document_text is None")
                combined_context += "\n\nNote: No document content was available for analysis."
            else:
                print(f"Using document_text (length: {len(document_text)})")
                # Use document analysis if available, otherwise use the raw text
                if document_analysis is not None and isinstance(document_analysis, dict):
                    try:
                        print(f"Using document_analysis: {list(document_analysis.keys()) if document_analysis else None}")
                        # Format the document analysis into a structured context
                        doc_context = "Document Analysis:\n"
                        if "summary" in document_analysis:
                            doc_context += f"Summary: {document_analysis['summary']}\n\n"
                        if "key_topics" in document_analysis and isinstance(document_analysis["key_topics"], list) and document_analysis['key_topics']:
                            doc_context += f"Key Topics: {', '.join(document_analysis['key_topics'])}\n\n"
                        if "structure_outline" in document_analysis and isinstance(document_analysis["structure_outline"], list) and document_analysis['structure_outline']:
                            doc_context += f"Structure: {', '.join(document_analysis['structure_outline'])}\n\n"
                        if "extracted_keywords" in document_analysis and isinstance(document_analysis["extracted_keywords"], list) and document_analysis['extracted_keywords']:
                            doc_context += f"Key Terms: {', '.join(document_analysis['extracted_keywords'])}\n\n"
                        
                        # Append to existing context
                        if combined_context:
                            combined_context += "\n\n" + doc_context
                        else:
                            combined_context = doc_context
                    except Exception as e:
                        print(f"Error processing document analysis: {e}")
                        # Fall back to using raw text
                        MAX_CHARS = 10000  # Reasonable limit for context
                        # Make sure document_text is not None
                        if document_text is None:
                            doc_text = "No document content available."
                        else:
                            doc_text = document_text[:MAX_CHARS]
                            if len(document_text) > MAX_CHARS:
                                doc_text += "... [Document truncated due to size]"
                        
                        if combined_context:
                            combined_context += "\n\n" + "Document Content:\n" + doc_text
                        else:
                            combined_context = "Document Content:\n" + doc_text
                else:
                    # Use the raw document text (truncated if very large)
                    MAX_CHARS = 10000  # Reasonable limit for context
                    # Make sure document_text is not None
                    if document_text is None:
                        doc_text = "No document content available."
                    else:
                        doc_text = document_text[:MAX_CHARS]
                        if len(document_text) > MAX_CHARS:
                            doc_text += "... [Document truncated due to size]"
                    
                    if combined_context:
                        combined_context += "\n\n" + "Document Content:\n" + doc_text
                    else:
                        combined_context = "Document Content:\n" + doc_text
        
        elif reference_type == "Web URL Reference" and web_url_content:
            # Add web URL content to context
            if combined_context:
                combined_context += "\n\n" + "Web Content:\n" + web_url_content
            else:
                combined_context = "Web Content:\n" + web_url_content
                
        elif reference_type == "YouTube Link Reference" and youtube_transcript:
            # Add YouTube transcript to context
            if combined_context:
                combined_context += "\n\n" + "Video Transcript:\n" + youtube_transcript
            else:
                combined_context = "Video Transcript:\n" + youtube_transcript
        
        # Generate the script using the primary function (which handles fallbacks)
        result = generate_script(
            prompt=prompt, 
            subject=subject, 
            length=length, 
            audience=audience, 
            tone=tone,
            template=template,
            context=combined_context
        )
        
        # Handle the new dict return format
        if isinstance(result, dict) and "content" in result:
            script = result["content"]
            # We could also use result["token_metrics"] here if needed
            model_used = result.get("model_used", "unknown")
            is_fallback = result.get("is_fallback", False)
            
            # Add a small note about which model was used (optional)
            model_info = f"Generated with: {model_used}" + (" (fallback)" if is_fallback else "")
        else:
            # Handle legacy return format (just the script text)
            script = result
            model_info = ""
        
        if not script:
            return "Failed to generate script with all available models. Please check API keys and try again.", None
        
        # Save the script to a file
        os.makedirs("output/scripts", exist_ok=True)
        timestamp = int(os.path.getmtime(__file__)) if os.path.exists(__file__) else 0
        script_file = f"output/scripts/script_{timestamp}.txt"
        
        with open(script_file, "w") as f:
            f.write(script)
            
            # Optionally add model info to the file
            if model_info:
                f.write(f"\n\n{model_info}")
        
        return script, script_file
    except Exception as e:
        return f"Error generating script: {str(e)}", None

def create_script_generator_tab():
    with gr.TabItem("Generate Script"):
        with gr.Row():
            with gr.Column():
                # Add industry-specific template selector
                template_selector = gr.Dropdown(
                    label="Script Template",
                    choices=[
                        "Music Lesson",
                        "Corporate Training",
                        "Marketing",
                        "General Education",
                        "Technical Tutorial",
                        "General"
                    ],
                    value="General",
                    info="Select an industry-specific template to guide script generation"
                )
                
                # Reference Input Section
                with gr.Group():
                    gr.Markdown("### Context / Reference Input")
                    
                    # Reference Type Selector
                    reference_type = gr.Radio(
                        label="Input Type",
                        choices=["None", "Document Upload", "Web URL Reference", "YouTube Link Reference"],
                        value="None"
                    )
                    
                    # Display document upload area when 'Document Upload' is selected
                    with gr.Column(visible=False, elem_id="document_upload_section") as document_upload_section:
                        with gr.Column(elem_classes="doc-upload-wrapper"):
                            with gr.Row():
                                with gr.Column(): # Left column: File upload
                                    file_upload = gr.File(
                                        label="Upload Document (Optional)",
                                        file_types=[".txt", ".md", ".pdf", ".docx"],
                                        elem_classes=["file-upload-container"]
                                    )
                                
                                with gr.Column(elem_classes=["file-info-container"]): # Right-side container
                                    # Combined Supported File Types and Token Limit in one HTML component
                                    gr.HTML("""
                                        <div class="supported-file-types">
                                            <h3 class="file-type-title">Supported File Types</h3>
                                            <div class="file-type-item"><span class="check-mark">✓</span> Text files (.txt)</div>
                                            <div class="file-type-item"><span class="check-mark">✓</span> Markdown files (.md)</div>
                                            <div class="file-type-item"><span class="check-mark">✓</span> PDF documents (.pdf)</div>
                                            <div class="file-type-item file-type-item-last"><span class="check-mark">✓</span> Word documents (.docx)</div>
                                            <h4 class="file-size-limit-title-text">File Size Limit</h4>
                                            <p class="token-limit-text">75,000 Tokens = 60,000 Words</p> 
                                        </div>
                                    """)
                    
                    # Web URL Input
                    with gr.Column(visible=False) as url_input_group:
                        url_reference_input = gr.Textbox(
                            label="Web URL Reference",
                            placeholder="Enter the full URL (e.g., https://www.example.com/article)"
                        )
                        # Add a placeholder for the web URL warning/info message
                        web_url_warning = gr.Markdown(visible=False, elem_classes=["warning-text"])
                    
                    # YouTube Link Input
                    with gr.Column(visible=False) as youtube_input_group:
                        youtube_reference_input = gr.Textbox(
                            label="YouTube Link Reference",
                            placeholder="Enter the full YouTube video URL"
                        )
                        # Add a placeholder for the YouTube warning/info message
                        youtube_warning = gr.Markdown(visible=False, elem_classes=["warning-text"])
                
                prompt_input = gr.Textbox(
                    label="What is your script about?",
                    placeholder="E.g., Create a script about the importance of sustainability",
                    lines=3
                )
                
                subject_input = gr.Textbox(
                    label="Subject",
                    placeholder="E.g., Environmental Science, Sustainable Practices, Conservation",
                )
                
                # Reference Type change handler - define after all components exist
                def update_reference_visibility(choice):
                    """Update visibility of reference input components and store the current selection"""
                    if choice == "Document Upload":
                        return gr.update(visible=True), gr.update(visible=False), gr.update(visible=False), choice
                    elif choice == "Web URL Reference":
                        return gr.update(visible=False), gr.update(visible=True), gr.update(visible=False), choice
                    elif choice == "YouTube Link Reference":
                        return gr.update(visible=False), gr.update(visible=False), gr.update(visible=True), choice
                    else:  # "None"
                        return gr.update(visible=False), gr.update(visible=False), gr.update(visible=False), "None"
                
                # Connect the radio buttons to the visibility function
                reference_type.change(
                    fn=update_reference_visibility,
                    inputs=[reference_type],
                    outputs=[document_upload_section, url_input_group, youtube_input_group, reference_type]
                )
                
                # Add context manager
                with gr.Group():
                    gr.Markdown("### Additional Context")
                    context_input = gr.Textbox(
                        label="Context Information",
                        placeholder="Add specific details, concepts, or internal knowledge that should be incorporated into the script",
                        lines=3,
                        info="This helps generate more accurate and relevant content"
                    )
                
                with gr.Row():
                    length_input = gr.Dropdown(
                        label="Length",
                        choices=["short", "medium", "long"],
                        value="medium"
                    )
                    audience_input = gr.Dropdown(
                        label="Target Audience",
                        choices=["general", "beginner", "intermediate", "advanced", "children"],
                        value="general"
                    )
                    tone_input = gr.Dropdown(
                        label="Tone",
                        choices=["informative", "conversational", "professional", "friendly", "enthusiastic"],
                        value="informative"
                    )
                
                # Add collapsible guide section
                with gr.Accordion("Additional Context Guide", open=False):
                    guide_markdown = gr.Markdown("""
                    ### Parameter Quick Guide
                    
                    **Length**: Controls script word count
                    - **Short**: 150-250 words, brief overview
                    - **Medium**: 300-500 words, balanced detail
                    - **Long**: 600-900 words, comprehensive coverage
                    
                    **Target Audience**: Adapts complexity and examples
                    - **General**: Universal approach
                    - **Beginner/Children**: Simplified concepts, more explanation
                    - **Intermediate**: More detailed techniques
                    - **Advanced**: Specialized terminology and complex concepts
                    
                    **Tone**: Sets the voice and style
                    - **Informative**: Clear, fact-focused delivery
                    - **Conversational**: Casual, friendly dialogue
                    - **Professional**: Formal, authoritative approach
                    - **Friendly**: Warm, encouraging language
                    - **Enthusiastic**: Energetic, motivational style
                    
                    **Additional Context**: Provide background information that informs the script generation without being directly referenced. Include:
                    - Relevant background knowledge
                    - Specific concepts to emphasize
                    - Goals or outcomes
                    - Time constraints or format requirements
                    """)
                    
                generate_btn = gr.Button("Generate Script", elem_classes=["primary"])
            
            with gr.Column():
                script_output = gr.Textbox(
                    label="Generated Script",
                    lines=20,
                    interactive=True,
                    elem_classes=["script-output-container"]
                )
                script_file_output = gr.Textbox(
                    label="Script File",
                    visible=False
                )
                
        # Connect the generate button to the create_script function
        generate_btn.click(
            fn=create_script,
            inputs=[
                prompt_input, 
                subject_input, 
                length_input, 
                audience_input, 
                tone_input,
                template_selector,
                context_input,
                reference_type  # Add reference_type as input
            ],
            outputs=[script_output, script_file_output]
        )
        
        # Display template-specific guidance when template is selected
        def update_template_fields(template):
            if template == "Music Lesson":
                return [
                    gr.update(
                    placeholder="E.g., Explain chord progressions for beginners",
                    info="Focus on educational content about music theory, instrument techniques, or practice methods"
                    ),
                    gr.update(
                        placeholder="E.g., Music Theory, Piano Technique, Jazz Improvisation"
                    ),
                    gr.update(
                        placeholder="Include specific concepts to cover, instrument references, prerequisite knowledge, or teaching techniques to incorporate",
                        info="For music lessons, consider including: skill level assumptions, instrument specifics, related concepts, or musical examples to reference"
                    ),
                    gr.update(value="""
                    ### Music Lesson Parameter Guide
                    
                    **Length**: Determines demonstration complexity
                    - **Short**: 30 seconds to 1 minute demonstration, focus on a single technique
                    - **Medium**: 2-5 minute lesson, covers technique with examples
                    - **Long**: 5-8 minute lesson, includes theory, practice and application
                    
                    **Target Audience**: Adjusts terminology and pace
                    - **General**: Balanced approach suitable for mixed skill levels
                    - **Beginner/Children**: Very simple terms, more hand position guidance
                    - **Intermediate**: Introduces music theory concepts
                    - **Advanced**: Uses proper musical terminology, complex techniques
                    
                    **Tone**: Sets instructional approach
                    - **Informative**: Clear, methodical explanation of technique
                    - **Conversational**: Friendly, casual teaching style
                    - **Professional**: Structured, authoritative instruction style
                    - **Friendly**: Encouraging, supportive guidance with positive reinforcement
                    - **Enthusiastic**: Motivational, energetic instruction
                    
                    **Additional Context**: For music lessons, include:
                    - Student's existing skills (chords, scales they know)
                    - Specific instruments and equipment available
                    - Related songs/repertoire to reference
                    - Prior lessons or techniques to build upon
                    """)
                ]
            elif template == "Corporate Training":
                return [
                    gr.update(
                    placeholder="E.g., Explain effective communication strategies for team leaders",
                    info="Focus on professional development, soft skills, or company procedures"
                    ),
                    gr.update(
                        placeholder="E.g., Leadership, Team Management, Communication Skills"
                    ),
                    gr.update(
                        placeholder="Include company-specific terminology, existing processes, skill gaps to address, or industry compliance requirements",
                        info="For corporate training, consider including: company culture context, specific workplace scenarios, industry challenges, or required competencies"
                    ),
                    gr.update(value="""
                    ### Corporate Training Parameter Guide
                    
                    **Length**: Controls training session duration
                    - **Short**: 5-10 minute briefing or quick update
                    - **Medium**: 15-25 minute focused training module
                    - **Long**: 30-45 minute comprehensive training session
                    
                    **Target Audience**: Adapts content to organizational roles
                    - **General**: All-staff appropriate material
                    - **Beginner**: New employee onboarding content
                    - **Intermediate**: Department-specific training
                    - **Advanced**: Management or specialist-level material
                    
                    **Tone**: Sets professional environment
                    - **Informative**: Direct, data-driven approach
                    - **Professional**: Formal, authoritative instruction
                    - **Conversational**: Collaborative, workshop-style approach
                    
                    **Additional Context**: For corporate training, include:
                    - Company policies or procedures relevant to the topic
                    - Industry regulations or compliance requirements
                    - Specific workplace scenarios to address
                    - Organizational hierarchy considerations
                    """)
                ]
            elif template == "Marketing":
                return [
                    gr.update(
                    placeholder="E.g., Create a script highlighting our product's key features",
                    info="Focus on benefits, features, customer needs, and call-to-action elements"
                    ),
                    gr.update(
                        placeholder="E.g., Product Launch, Brand Awareness, Customer Testimonial"
                    ),
                    gr.update(
                        placeholder="Include product specifications, competitive advantages, target customer demographics, or brand voice guidelines",
                        info="For marketing, consider including: unique selling points, customer pain points, competitor comparisons, or specific metrics/claims to include"
                    ),
                    gr.update(value="""
                    ### Marketing Parameter Guide
                    
                    **Length**: Adapts to marketing format
                    - **Short**: 30-second ad or social media post
                    - **Medium**: 1-2 minute promotional video
                    - **Long**: 3-5 minute detailed product presentation
                    
                    **Target Audience**: Tailors to customer segments
                    - **General**: Broad market appeal
                    - **Beginner**: New customers, simple explanations
                    - **Intermediate**: Returning customers, more features
                    - **Advanced**: Industry professionals, technical details
                    
                    **Tone**: Sets brand personality
                    - **Conversational**: Relatable, customer-focused approach
                    - **Professional**: Industry authority positioning
                    - **Enthusiastic**: High-energy, promotional style
                    - **Friendly**: Approachable, solution-oriented
                    
                    **Additional Context**: For marketing, include:
                    - Key product specifications and pricing
                    - Unique selling propositions vs competitors
                    - Target demographics and customer pain points
                    - Campaign goals and desired call-to-action
                    """)
                ]
            elif template == "General Education":
                return [
                    gr.update(
                    placeholder="E.g., Explain photosynthesis in a way that's easy to understand",
                    info="Focus on clear explanations of educational concepts for learning purposes"
                    ),
                    gr.update(
                        placeholder="E.g., Biology, Chemistry, Physics, History, Mathematics"
                    ),
                    gr.update(
                        placeholder="Include curriculum requirements, related concepts, visual aids to reference, or misconceptions to address",
                        info="For educational content, consider including: grade level context, specific learning objectives, key vocabulary to use, or supporting examples"
                    ),
                    gr.update(value="""
                    ### Educational Content Parameter Guide
                    
                    **Length**: Adapts to lesson format
                    - **Short**: 3-5 minute concept introduction
                    - **Medium**: 8-12 minute lesson segment
                    - **Long**: 15-20 minute complete lesson
                    
                    **Target Audience**: Adjusts to educational level
                    - **Children**: Elementary/primary school level
                    - **Beginner**: Secondary/high school basics
                    - **Intermediate**: Advanced high school/early college
                    - **Advanced**: College/university level content
                    
                    **Tone**: Sets instructional approach
                    - **Informative**: Clear, factual presentation
                    - **Conversational**: Engaging, dialogue-style teaching
                    - **Enthusiastic**: Dynamic, curiosity-building approach
                    
                    **Additional Context**: For educational content, include:
                    - Curriculum standards or learning objectives
                    - Prior knowledge students should have
                    - Common misconceptions to address
                    - Visual aids or demonstrations available
                    """)
                ]
            elif template == "Technical Tutorial":
                return [
                    gr.update(
                    placeholder="E.g., Explain how to set up a development environment for Python",
                    info="Focus on step-by-step instructions, technical details, and best practices"
                    ),
                    gr.update(
                        placeholder="E.g., Software Development, Data Analysis, System Administration"
                    ),
                    gr.update(
                        placeholder="Include software versions, prerequisites, technical specifications, or common pitfalls to address",
                        info="For technical tutorials, consider including: environment details, dependency requirements, troubleshooting tips, or expected outcomes"
                    ),
                    gr.update(value="""
                    ### Technical Tutorial Parameter Guide
                    
                    **Length**: Controls tutorial depth
                    - **Short**: Quick tip or single feature overview
                    - **Medium**: Focused walkthrough of one concept
                    - **Long**: Comprehensive implementation guide
                    
                    **Target Audience**: Adjusts technical complexity
                    - **Beginner**: New to the technology, needs basics
                    - **Intermediate**: Familiar but needs detailed steps
                    - **Advanced**: Experienced users needing optimization
                    
                    **Tone**: Sets instructional style
                    - **Informative**: Clear, precise technical instructions
                    - **Professional**: Industry standard approaches
                    - **Conversational**: Accessible technical guidance
                    
                    **Additional Context**: For technical tutorials, include:
                    - Software versions and dependencies
                    - System requirements or constraints
                    - Prerequisites or required knowledge
                    - Common errors and troubleshooting tips
                    """)
                ]
            else:  # General
                return [
                    gr.update(
                    placeholder="E.g., Create a script about the importance of sustainability",
                    info="General purpose script without industry-specific formatting"
                    ),
                    gr.update(
                        placeholder="E.g., Environmental Science, Sustainable Practices, Conservation"
                    ),
                    gr.update(
                        placeholder="Add specific details, concepts, or internal knowledge that should be incorporated into the script",
                        info="This helps generate more accurate and relevant content"
                    ),
                    gr.update(value="""
                    ### Parameter Quick Guide
                    
                    **Length**: Controls script word count
                    - **Short**: 150-250 words, brief overview
                    - **Medium**: 300-500 words, balanced detail
                    - **Long**: 600-900 words, comprehensive coverage
                    
                    **Target Audience**: Adapts complexity and examples
                    - **General**: Universal approach
                    - **Beginner/Children**: Simplified concepts, more explanation
                    - **Intermediate**: More detailed techniques
                    - **Advanced**: Specialized terminology and complex concepts
                    
                    **Tone**: Sets the voice and style
                    - **Informative**: Clear, fact-focused delivery
                    - **Conversational**: Casual, friendly dialogue
                    - **Professional**: Formal, authoritative approach
                    - **Friendly**: Warm, encouraging language
                    - **Enthusiastic**: Energetic, motivational style
                    
                    **Additional Context**: Provide background information that informs the script generation without being directly referenced. Include:
                    - Relevant background knowledge
                    - Specific concepts to emphasize
                    - Goals or outcomes
                    - Time constraints or format requirements
                    """)
                ]
        
        # Update all fields based on selected template
        template_selector.change(
            fn=update_template_fields,
            inputs=[template_selector],
            outputs=[prompt_input, subject_input, context_input, guide_markdown]
        )
        
        # Add event handlers for document upload, web URL, and YouTube URL
        file_upload.change(
            fn=process_uploaded_document,
            inputs=[file_upload],
            outputs=[document_upload_section]
        )
        
        # Add event handler for web URL input
        url_reference_input.change(
            fn=process_web_url,
            inputs=[url_reference_input],
            outputs=[web_url_warning]
        )
        
        # Add event handler for YouTube URL input
        youtube_reference_input.change(
            fn=process_youtube_url,
            inputs=[youtube_reference_input],
            outputs=[youtube_warning]
        )
        
        return script_output, script_file_output 