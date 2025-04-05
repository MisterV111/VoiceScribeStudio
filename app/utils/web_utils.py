import requests
from bs4 import BeautifulSoup
import trafilatura
import re
from urllib.parse import urlparse
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def is_valid_url(url):
    """
    Check if the provided URL is valid.
    
    Args:
        url (str): The URL to validate
        
    Returns:
        bool: True if URL is valid, False otherwise
    """
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc]) and result.scheme in ['http', 'https']
    except Exception as e:
        logger.error(f"URL validation error: {e}")
        return False

def extract_content_from_url(url, max_length=100000):
    """
    Extract content from a given URL using trafilatura with BeautifulSoup as fallback.
    
    Args:
        url (str): The URL to extract content from
        max_length (int, optional): Maximum number of characters to extract
        
    Returns:
        dict: A dictionary containing the extracted content and metadata
              - 'title': Page title
              - 'content': Main text content
              - 'success': Boolean indicating if extraction was successful
              - 'error': Error message if extraction failed
    """
    result = {
        'title': '',
        'content': '',
        'success': False,
        'error': None
    }
    
    if not is_valid_url(url):
        result['error'] = "Invalid URL format"
        return result
    
    try:
        # Try to download the webpage content
        downloaded = trafilatura.fetch_url(url)
        if downloaded is None:
            # Fallback to requests if trafilatura fetch fails
            response = requests.get(url, timeout=10)
            response.raise_for_status()  # Raise exception for HTTP errors
            downloaded = response.text
        
        # First try extraction with trafilatura
        extracted = trafilatura.extract(downloaded, include_comments=False, 
                                       include_tables=True, 
                                       no_fallback=False)
        
        if extracted:
            # Use trafilatura extraction which provides cleaner text
            result['content'] = extracted[:max_length]
            # Try to get title from trafilatura metadata
            trafila_metadata = trafilatura.metadata.extract_metadata(downloaded, url)
            if trafila_metadata and hasattr(trafila_metadata, 'title'):
                result['title'] = trafila_metadata.title
            else:
                # Fallback to BeautifulSoup for title
                soup = BeautifulSoup(downloaded, 'html.parser')
                result['title'] = soup.title.string if soup.title else url
        else:
            # Fallback to BeautifulSoup extraction
            soup = BeautifulSoup(downloaded, 'html.parser')
            result['title'] = soup.title.string if soup.title else url
            
            # Extract text from paragraphs
            paragraphs = soup.find_all('p')
            text = '\n\n'.join([p.get_text() for p in paragraphs])
            
            # If almost no paragraphs found, get text from body
            if len(text) < 100:
                text = soup.body.get_text(' ', strip=True) if soup.body else ''
            
            result['content'] = text[:max_length]
        
        # Check if we got meaningful content
        if len(result['content']) < 50:
            result['error'] = "Could not extract meaningful content from the URL"
            return result
            
        result['success'] = True
        
    except requests.exceptions.RequestException as e:
        result['error'] = f"Failed to fetch URL: {str(e)}"
    except Exception as e:
        result['error'] = f"Error processing URL: {str(e)}"
    
    return result

def format_web_content_for_llm(extracted_data):
    """
    Format the extracted web content for use with LLM.
    
    Args:
        extracted_data (dict): The dictionary returned by extract_content_from_url
        
    Returns:
        str: Formatted content ready to use as context for an LLM
    """
    if not extracted_data['success']:
        return f"Error retrieving content from URL: {extracted_data['error']}"
    
    formatted_content = f"Title: {extracted_data['title']}\n\n"
    formatted_content += "Content:\n" + extracted_data['content']
    
    return formatted_content 