"""
Google Docs Content Fetcher
Fetches text content from public Google Docs links
"""
import requests
import re
from typing import Optional

def extract_doc_id(url: str) -> Optional[str]:
    """Extract Google Doc ID from various URL formats."""
    # Pattern for Google Docs URLs
    patterns = [
        r'/document/d/([a-zA-Z0-9-_]+)',
        r'/open\?id=([a-zA-Z0-9-_]+)',
        r'id=([a-zA-Z0-9-_]+)'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None

def fetch_google_doc_content(url: str) -> dict:
    """
    Fetch content from a Google Doc URL.
    Returns dict with 'success', 'content', and 'error' keys.
    """
    if not url or url == "nan" or "google" not in url.lower():
        return {"success": False, "content": "", "error": "Not a valid Google Docs URL"}
    
    doc_id = extract_doc_id(url)
    if not doc_id:
        return {"success": False, "content": "", "error": "Could not extract document ID"}
    
    # Google Docs export as plain text URL
    export_url = f"https://docs.google.com/document/d/{doc_id}/export?format=txt"
    
    try:
        response = requests.get(export_url, timeout=10)
        
        if response.status_code == 200:
            content = response.text.strip()
            # Clean up common artifacts
            content = re.sub(r'\r\n', '\n', content)
            return {"success": True, "content": content, "error": None}
        elif response.status_code == 403:
            return {"success": False, "content": "", "error": "Access restricted (requires login)"}
        elif response.status_code == 404:
            return {"success": False, "content": "", "error": "Document not found"}
        else:
            return {"success": False, "content": "", "error": f"HTTP {response.status_code}"}
    
    except requests.Timeout:
        return {"success": False, "content": "", "error": "Request timeout"}
    except Exception as e:
        return {"success": False, "content": "", "error": str(e)}

def fetch_multiple_docs(urls: list) -> list:
    """Fetch content from multiple Google Doc URLs."""
    results = []
    for url in urls:
        result = fetch_google_doc_content(url)
        result["url"] = url
        results.append(result)
    return results

if __name__ == "__main__":
    # Test with sample URL
    test_urls = [
        "https://docs.google.com/document/d/1ABC123/edit",
        "not a url",
    ]
    
    for url in test_urls:
        print(f"\nTesting: {url[:50]}...")
        result = fetch_google_doc_content(url)
        print(f"Success: {result['success']}")
        if result['success']:
            print(f"Content preview: {result['content'][:100]}...")
        else:
            print(f"Error: {result['error']}")
