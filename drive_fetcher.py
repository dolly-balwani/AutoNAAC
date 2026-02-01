"""
Google Drive API Fetcher with OAuth
Fetches files (including images) from Google Drive folders
"""
import os
import io
import re
import base64
from typing import List, Dict, Optional
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

# Scopes needed for Drive access
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

class GoogleDriveFetcher:
    """Fetches files from Google Drive folders using OAuth."""
    
    def __init__(self, credentials_path: str = "credentials.json", token_path: str = "token.json"):
        self.credentials_path = credentials_path
        self.token_path = token_path
        self.service = None
        self.authenticated = False
    
    def authenticate(self) -> bool:
        """Authenticate with Google Drive API."""
        creds = None
        
        # Check for existing token
        if os.path.exists(self.token_path):
            creds = Credentials.from_authorized_user_file(self.token_path, SCOPES)
        
        # If no valid credentials, authenticate
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists(self.credentials_path):
                    print(f"❌ credentials.json not found!")
                    print(f"   Please follow the setup guide to create OAuth credentials.")
                    return False
                
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_path, SCOPES)
                creds = flow.run_local_server(port=0)
            
            # Save token for next time
            with open(self.token_path, 'w') as token:
                token.write(creds.to_json())
        
        self.service = build('drive', 'v3', credentials=creds)
        self.authenticated = True
        print("✅ Google Drive authenticated successfully!")
        return True
    
    def extract_folder_id(self, url: str) -> Optional[str]:
        """Extract folder ID from Google Drive folder URL."""
        patterns = [
            r'/folders/([a-zA-Z0-9-_]+)',
            r'id=([a-zA-Z0-9-_]+)',
        ]
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None
    
    def extract_file_id(self, url: str) -> Optional[str]:
        """Extract file ID from Google Drive file URL."""
        patterns = [
            r'/file/d/([a-zA-Z0-9-_]+)',
            r'/d/([a-zA-Z0-9-_]+)',
        ]
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None
    
    def get_file_info(self, file_id: str) -> Optional[Dict]:
        """Get file metadata from Drive."""
        try:
            file = self.service.files().get(
                fileId=file_id,
                fields='id, name, mimeType'
            ).execute()
            return file
        except Exception as e:
            print(f"Error getting file info: {e}")
            return None
    
    def list_folder_contents(self, folder_id: str) -> List[Dict]:
        """List all files in a folder."""
        if not self.authenticated:
            self.authenticate()
        
        try:
            results = self.service.files().list(
                q=f"'{folder_id}' in parents",
                fields="files(id, name, mimeType)"
            ).execute()
            return results.get('files', [])
        except Exception as e:
            print(f"Error listing folder: {e}")
            return []
    
    def download_google_doc_as_html(self, file_id: str) -> str:
        """Download a Google Doc as HTML (includes images as base64)."""
        try:
            request = self.service.files().export_media(
                fileId=file_id,
                mimeType='text/html'
            )
            content = request.execute()
            return content.decode('utf-8')
        except Exception as e:
            print(f"Error downloading doc: {e}")
            return ""
    
    def download_google_doc_as_text(self, file_id: str) -> str:
        """Download a Google Doc as plain text."""
        try:
            request = self.service.files().export_media(
                fileId=file_id,
                mimeType='text/plain'
            )
            content = request.execute()
            return content.decode('utf-8')
        except Exception as e:
            print(f"Error downloading doc: {e}")
            return ""
    
    def download_file(self, file_id: str, output_path: str) -> bool:
        """Download a file (PDF, image, etc.) to disk."""
        try:
            request = self.service.files().get_media(fileId=file_id)
            fh = io.BytesIO()
            downloader = MediaIoBaseDownload(fh, request)
            done = False
            while not done:
                status, done = downloader.next_chunk()
            
            with open(output_path, 'wb') as f:
                f.write(fh.getvalue())
            return True
        except Exception as e:
            print(f"Error downloading file: {e}")
            return False
    
    def fetch_folder_content(self, folder_url: str, output_dir: str = "temp_downloads") -> Dict:
        """
        Fetch content from a Google Drive URL (folder or file).
        Returns dict with text content, image paths, and metadata.
        """
        if not self.authenticated:
            if not self.authenticate():
                return {"success": False, "error": "Authentication failed"}
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        result = {
            "success": True,
            "text_content": "",
            "html_content": "",
            "images": [],
            "files": []
        }
        
        # Try as folder first
        folder_id = self.extract_folder_id(folder_url)
        if folder_id:
            # It's a folder - list contents
            files = self.list_folder_contents(folder_id)
            if files:
                for file in files:
                    self._process_file(file, output_dir, result)
                return result
        
        # Try as direct file
        file_id = self.extract_file_id(folder_url)
        if file_id:
            file_info = self.get_file_info(file_id)
            if file_info:
                self._process_file(file_info, output_dir, result)
                return result
        
        return {"success": False, "error": "Could not extract ID from URL"}
    
    def _process_file(self, file: Dict, output_dir: str, result: Dict):
        """Process a single file and add to result."""
        file_name = file['name']
        file_id = file['id']
        mime_type = file['mimeType']
        
        print(f"  Processing: {file_name[:50]} ({mime_type})")
        
        if mime_type == 'application/vnd.google-apps.document':
            # Google Doc - get as text
            text = self.download_google_doc_as_text(file_id)
            result["text_content"] += f"\n\n{text}"
            result["files"].append({"name": file_name, "type": "doc"})
            
        elif mime_type.startswith('image/'):
            # Image file - download
            ext = mime_type.split('/')[1]
            if ext == 'jpeg':
                ext = 'jpg'
            img_path = os.path.join(output_dir, f"{file_id}.{ext}")
            if self.download_file(file_id, img_path):
                result["images"].append(img_path)
                result["files"].append({"name": file_name, "type": "image", "path": img_path})
                
        elif mime_type == 'application/pdf':
            # PDF - download
            safe_name = re.sub(r'[<>:"/\\|?*]', '_', file_name)[:100]
            pdf_path = os.path.join(output_dir, safe_name)
            if self.download_file(file_id, pdf_path):
                result["files"].append({"name": file_name, "type": "pdf", "path": pdf_path})
        
        elif mime_type == 'application/vnd.google-apps.folder':
            # Nested folder - skip for now
            pass


def test_drive_connection():
    """Test Google Drive API connection."""
    fetcher = GoogleDriveFetcher()
    
    if not os.path.exists("credentials.json"):
        print("❌ credentials.json not found!")
        print("\nPlease follow these steps:")
        print("1. Go to https://console.cloud.google.com/")
        print("2. Create a project and enable Google Drive API")
        print("3. Create OAuth credentials (Desktop app)")
        print("4. Download and save as 'credentials.json' in this folder")
        return False
    
    return fetcher.authenticate()


if __name__ == "__main__":
    test_drive_connection()
