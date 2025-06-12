"""Web URL content extraction utilities."""

import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import importlib.util
import time

# Check if required packages are installed
def check_dependencies():
    """Check if required dependencies are installed."""
    missing_deps = []
    
    # Check for requests
    if importlib.util.find_spec("requests") is None:
        missing_deps.append("requests")
    
    # Check for BeautifulSoup
    if importlib.util.find_spec("bs4") is None:
        missing_deps.append("beautifulsoup4")
        
    # Check for lxml
    if importlib.util.find_spec("lxml") is None:
        missing_deps.append("lxml")
        
    return missing_deps

def extract_web_content(url):
    """
    Extract content from a web URL.
    
    Args:
        url (str): URL to extract content from
        
    Returns:
        tuple: (content, error) where content is the extracted text and error is an error message if any
    """
    # Check dependencies first
    missing_deps = check_dependencies()
    if missing_deps:
        return None, f"Missing required dependencies: {', '.join(missing_deps)}. Please install with: pip install {' '.join(missing_deps)}"
    
    try:
        # Validate URL format
        if not url.startswith(('http://', 'https://')):
            return None, "URL must start with http:// or https://"
            
        parsed_url = urlparse(url)
        if not parsed_url.netloc:
            return None, "Invalid URL format"
        
        # List of User-Agent strings to try if we get a 403
        user_agents = [
            # Chrome on Windows
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            # Firefox on Windows
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
            # Safari on macOS
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 14_3) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.3 Safari/605.1.15',
            # Chrome on macOS
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            # Mobile Chrome on Android
            'Mozilla/5.0 (Linux; Android 13; SM-S908B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Mobile Safari/537.36',
            # Mobile Safari on iOS
            'Mozilla/5.0 (iPhone; CPU iPhone OS 17_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1'
        ]
        
        # Attempt using different user agents and methods if needed
        response = None
        for attempt, user_agent in enumerate(user_agents[:2]):  # Start with just two attempts
            try:
                # Create headers with the current user agent
                headers = {
                    'User-Agent': user_agent,
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'Referer': 'https://www.google.com/',
                    'Cache-Control': 'max-age=0',
                    'Connection': 'keep-alive',
                    'Sec-Fetch-Dest': 'document',
                    'Sec-Fetch-Mode': 'navigate',
                    'Sec-Fetch-Site': 'cross-site',
                    'Upgrade-Insecure-Requests': '1',
                    'Sec-Ch-Ua': '"Not A(Brand";v="99", "Google Chrome";v="121", "Chromium";v="121"',
                    'Sec-Ch-Ua-Mobile': '?0',
                    'Sec-Ch-Ua-Platform': '"Windows"'
                }
                
                # For some attempts, also try without verification
                verify_ssl = True
                if attempt > 0:
                    # Slightly different approach for later attempts
                    verify_ssl = False
                
                # Make request with current configuration
                response = requests.get(url, headers=headers, timeout=15, verify=verify_ssl)
                
                # If successful, break out of the loop
                if response.status_code == 200:
                    break
                
                # If we got a 403 but have more user agents to try, continue to the next iteration
                if response.status_code == 403 and attempt < len(user_agents) - 1:
                    print(f"Received 403 with User-Agent: {user_agent}, trying next agent...")
                    time.sleep(1)  # Short delay between attempts
                    continue
                    
                # If we got to this point, raise the HTTP error to be caught below
                response.raise_for_status()
                
            except requests.exceptions.RequestException as e:
                # If this is our last attempt, re-raise to be caught by the outer exception handler
                if attempt == len(user_agents) - 1:
                    raise
                # Otherwise try the next user agent
                print(f"Error on attempt {attempt+1}: {str(e)}")
                time.sleep(0.5)
        
        # If we didn't get a response after all attempts, raise an exception
        if response is None:
            raise requests.exceptions.RequestException("All request attempts failed")
            
        # Check content type
        content_type = response.headers.get('Content-Type', '').lower()
        if 'text/html' not in content_type and 'application/xhtml+xml' not in content_type:
            # Check if it's plain text, which can also be processed
            if 'text/plain' in content_type:
                # For text/plain, just return the text content
                return response.text, None
            else:
                return None, (f"Unsupported content type: {content_type}. "
                             "Only HTML and plain text content are supported.")
            
        # Parse the HTML
        try:
            soup = BeautifulSoup(response.text, 'html.parser')
        except Exception as e:
            return None, f"Failed to parse HTML: {str(e)}"
        
        # Remove script, style elements, and navigation elements
        for element in soup(['script', 'style', 'nav', 'footer', 'header', 'aside']):
            element.extract()
            
        # Check for article or main content
        main_content = None
        
        # First try to find the main content area
        for selector in ['article', 'main', '[role="main"]', '.main-content', 
                         '#main-content', '.content', '#content']:
            content_element = soup.select_one(selector)
            if content_element:
                main_content = content_element
                break
                
        # If no main content area found, use the body
        if not main_content:
            main_content = soup.body
            
        # Extract text
        if main_content:
            # Get all text nodes
            texts = main_content.find_all(text=True)
            
            # Filter out empty lines and join
            text = ' '.join(t.strip() for t in texts if t.strip())
            
            # If text is too short, try the entire page content
            if len(text) < 100 and main_content != soup.body:
                texts = soup.body.find_all(text=True)
                text = ' '.join(t.strip() for t in texts if t.strip())
                
            # Clean up the text
            # Remove excess whitespace
            text = re.sub(r'\s+', ' ', text)
            
            # Remove very short lines that might be remnants of menus
            lines = [line for line in text.split('\n') if len(line.strip()) > 10]
            text = '\n'.join(lines)
            
            # If we still don't have meaningful content
            if len(text.strip()) < 50:
                return None, ("Could not extract meaningful content from the page. "
                              "The page may contain mostly images or JavaScript-rendered content.")
            
            return text, None
        else:
            return None, "Could not extract content from the page. No main content area found."
            
    except requests.exceptions.SSLError:
        # Try one more time without certificate verification
        try:
            print("SSL error encountered, trying without verification...")
            headers = {
                'User-Agent': ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                              '(KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'),
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Referer': 'https://www.google.com/'
            }
            response = requests.get(url, headers=headers, timeout=10, verify=False)
            
            # Use BeautifulSoup to extract text content
            soup = BeautifulSoup(response.text, 'html.parser')
            for element in soup(['script', 'style', 'nav', 'footer', 'header', 'aside']):
                element.extract()
                
            texts = soup.body.find_all(text=True)
            text = ' '.join(t.strip() for t in texts if t.strip())
            text = re.sub(r'\s+', ' ', text)
            
            if len(text.strip()) < 50:
                return None, ("Could not extract meaningful content using fallback method. "
                             "The site may be protected or mostly contain non-text content.")
                
            return text, None
            
        except Exception as e:
            return None, f"SSL verification failed and fallback method also failed: {str(e)}"
            
    except requests.exceptions.ConnectionError:
        return None, "Connection error. Please check the URL and your internet connection."
        
    except requests.exceptions.Timeout:
        return None, "Request timed out. The website may be slow or unreachable."
        
    except requests.exceptions.HTTPError as e:
        status_code = e.response.status_code if hasattr(e, 'response') and hasattr(e.response, 'status_code') else None
        
        if status_code == 403:
            # For 403 errors, try to be more helpful
            return None, ("Access forbidden (403). This might not be due to blocking scrapers - "
                         "consider trying to view the URL manually in your browser to confirm it's accessible.")
        if status_code == 404:
            return None, "Page not found (404). Please check the URL."
        if status_code >= 500:
            return None, f"Server error ({status_code}). The website may be experiencing issues."
            
        return None, f"HTTP error: {status_code if status_code else 'unknown'}"
        
    except requests.exceptions.RequestException as e:
        return None, f"Request error: {str(e)}"
        
    except Exception as e:
        return None, f"Error extracting content: {str(e)}" 