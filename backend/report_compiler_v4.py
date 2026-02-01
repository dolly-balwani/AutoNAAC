"""
NAAC Report Compiler V4 - Enhanced with Clickable Index & AI Narratives
Features:
- Clickable Table of Contents with page links
- Image thumbnails with detailed captions
- AI-generated narratives per event using Gemini
- PDF bookmarks for navigation
"""

import os
import io
import shutil
import re
from typing import List, Dict, Tuple, Optional
from pypdf import PdfReader, PdfWriter
from fpdf import FPDF
from PIL import Image
from dotenv import load_dotenv
from google import genai

from excel_parser import parse_criterion_sheet
from drive_fetcher import GoogleDriveFetcher

load_dotenv()

# Initialize Gemini client
client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
MODEL_NAME = "gemini-2.0-flash"


def sanitize_text(text: str, max_len: int = 500) -> str:
    """Sanitize text for PDF - replaces Unicode special characters with ASCII equivalents."""
    if not text:
        return ""
    text = str(text)[:max_len]
    
    # Replace common Unicode characters with ASCII equivalents
    replacements = {
        '–': '-',  # en-dash
        '—': '-',  # em-dash
        ''': "'",  # left single quote
        ''': "'",  # right single quote
        '"': '"',  # left double quote
        '"': '"',  # right double quote
        '…': '...',  # ellipsis
        '•': '*',  # bullet
        '°': ' deg',  # degree
        '©': '(c)',  # copyright
        '®': '(R)',  # registered
        '™': '(TM)',  # trademark
        '\u200b': '',  # zero-width space
        '\xa0': ' ',  # non-breaking space
    }
    
    for old, new in replacements.items():
        text = text.replace(old, new)
    
    # Filter out any remaining non-ASCII characters
    return ''.join(c if ord(c) < 256 else '?' for c in text)


class EnhancedReportPDF(FPDF):
    """Enhanced PDF generator with images, captions, and AI content."""
    
    def __init__(self):
        super().__init__()
        self.set_auto_page_break(auto=True, margin=15)
    
    def safe_text(self, text: str, max_len: int = 500) -> str:
        """Safely encode text for PDF - handles Unicode special characters."""
        if not text:
            return ""
        text = str(text)[:max_len]
        
        # Replace common Unicode characters with ASCII equivalents
        replacements = {
            '–': '-',  # en-dash
            '—': '-',  # em-dash
            ''': "'",  # left single quote
            ''': "'",  # right single quote
            '"': '"',  # left double quote
            '"': '"',  # right double quote
            '…': '...',  # ellipsis
            '•': '*',  # bullet
            '°': ' deg',  # degree
            '©': '(c)',  # copyright
            '®': '(R)',  # registered
            '™': '(TM)',  # trademark
            '\u200b': '',  # zero-width space
            '\xa0': ' ',  # non-breaking space
        }
        
        for old, new in replacements.items():
            text = text.replace(old, new)
        
        # Filter out any remaining non-ASCII characters
        return ''.join(c if ord(c) < 256 else '?' for c in text)
    
    def header(self):
        """Add header to each page."""
        self.set_font("Helvetica", "I", 8)
        self.cell(0, 10, "NAAC Criterion Report", align="R")
        self.ln(5)
    
    def add_cover_page(self, criterion: str, title: str):
        """Add institutional cover page."""
        self.add_page()
        self.set_font("Helvetica", "B", 16)
        self.cell(0, 15, "Vivekanand Education Society's", new_x="LMARGIN", new_y="NEXT", align="C")
        self.cell(0, 10, "Institute of Technology", new_x="LMARGIN", new_y="NEXT", align="C")
        self.set_font("Helvetica", "", 10)
        self.cell(0, 8, "(Affiliated to University of Mumbai, Approved by AICTE)", new_x="LMARGIN", new_y="NEXT", align="C")
        self.ln(30)
        
        self.set_font("Helvetica", "B", 28)
        self.cell(0, 15, self.safe_text(criterion), new_x="LMARGIN", new_y="NEXT", align="C")
        self.ln(10)
        self.set_font("Helvetica", "B", 14)
        self.multi_cell(0, 10, self.safe_text(title), align="C")
        self.ln(40)
        
        self.set_font("Helvetica", "", 12)
        self.cell(0, 10, "NAAC Accreditation Report", new_x="LMARGIN", new_y="NEXT", align="C")
    
    def add_index_page(self, events: List[Dict], page_map: Dict[str, int]):
        """Add clickable index/table of contents."""
        self.add_page()
        self.set_font("Helvetica", "B", 18)
        self.cell(0, 15, "TABLE OF CONTENTS", new_x="LMARGIN", new_y="NEXT", align="C")
        self.ln(10)
        
        # Table header
        self.set_font("Helvetica", "B", 10)
        self.cell(10, 8, "Sr.", border=1, align="C")
        self.cell(110, 8, "Event Name", border=1, align="C")
        self.cell(25, 8, "Date", border=1, align="C")
        self.cell(20, 8, "Page", border=1, align="C", new_x="LMARGIN", new_y="NEXT")
        
        # Table rows
        self.set_font("Helvetica", "", 9)
        for i, event in enumerate(events):
            name = self.safe_text(event.get('name', ''), 55)
            date = self.safe_text(str(event.get('date', '')), 10)
            page_num = page_map.get(event.get('name', ''), '?')
            
            # Store link position for later annotation
            y_pos = self.get_y()
            self.cell(10, 7, str(i+1), border=1, align="C")
            
            # Make event name a clickable link (we'll add annotations later)
            self.set_text_color(0, 0, 180)  # Blue for links
            self.cell(110, 7, name, border=1)
            self.set_text_color(0, 0, 0)  # Reset to black
            
            self.cell(25, 7, date, border=1, align="C")
            self.cell(20, 7, str(page_num), border=1, align="C", new_x="LMARGIN", new_y="NEXT")
    
    def add_event_section(self, event: Dict, narrative: str, images: List[Dict]):
        """Add a single event section with AI narrative and images."""
        self.add_page()
        
        # Event title
        self.set_font("Helvetica", "B", 14)
        self.multi_cell(0, 8, self.safe_text(event.get('name', 'Untitled Event'), 100))
        self.ln(3)
        
        # Event metadata
        self.set_font("Helvetica", "", 10)
        if event.get('date'):
            self.cell(0, 6, f"Date: {event.get('date', '')[:20]}", new_x="LMARGIN", new_y="NEXT")
        if event.get('students'):
            self.cell(0, 6, f"Participants: {event.get('students', '')[:30]}", new_x="LMARGIN", new_y="NEXT")
        if event.get('agencies'):
            self.cell(0, 6, f"Agencies: {event.get('agencies', '')[:50]}", new_x="LMARGIN", new_y="NEXT")
        self.ln(5)
        
        # AI-generated narrative
        if narrative:
            self.set_font("Helvetica", "B", 11)
            self.cell(0, 8, "Event Summary", new_x="LMARGIN", new_y="NEXT")
            self.set_font("Helvetica", "", 10)
            self.multi_cell(0, 6, self.safe_text(narrative, 2000))
            self.ln(5)
        
        # Images with captions (thumbnails - multiple per page)
        if images:
            self.set_font("Helvetica", "B", 11)
            self.cell(0, 8, "Event Documentation", new_x="LMARGIN", new_y="NEXT")
            self.ln(3)
            
            x_start = self.get_x()
            y_start = self.get_y()
            img_width = 85  # Two images per row
            img_height = 60
            col = 0
            
            for img_info in images[:6]:  # Max 6 images per event
                img_path = img_info.get('path', '')
                caption = img_info.get('caption', img_info.get('name', ''))
                
                if os.path.exists(img_path):
                    try:
                        x = x_start + (col * (img_width + 5))
                        y = self.get_y()
                        
                        # Check if need new page
                        if y + img_height + 15 > 280:
                            self.add_page()
                            y = self.get_y()
                            col = 0
                            x = x_start
                        
                        # Add image thumbnail
                        self.image(img_path, x=x, y=y, w=img_width, h=img_height)
                        
                        # Add caption below image
                        self.set_xy(x, y + img_height + 1)
                        self.set_font("Helvetica", "I", 8)
                        self.multi_cell(img_width, 4, self.safe_text(caption, 80))
                        
                        col = (col + 1) % 2
                        if col == 0:
                            self.set_y(y + img_height + 15)
                            
                    except Exception as e:
                        print(f"    Warning: Could not add image {img_path}: {e}")


def generate_ai_narrative(event: Dict, doc_text: str = "") -> str:
    """Generate AI narrative for an event using Gemini."""
    try:
        prompt = f"""
        You are writing a professional NAAC accreditation report narrative.
        
        EVENT DETAILS:
        - Name: {event.get('name', 'Unknown')}
        - Date: {event.get('date', 'Not specified')}
        - Participants: {event.get('students', 'Not specified')}
        - Organizing Agency: {event.get('agencies', 'Not specified')}
        
        ADDITIONAL CONTENT FROM DOCUMENTS:
        {doc_text[:2000] if doc_text else 'No additional content available.'}
        
        TASK:
        Write a professional, factual 100-150 word narrative describing this event.
        Focus on:
        1. What the event was about
        2. Who participated
        3. Key outcomes or learning
        4. Alignment with NAAC quality criteria
        
        Write in third person, past tense, formal academic tone.
        """
        
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt
        )
        return response.text.strip()
        
    except Exception as e:
        print(f"    Warning: AI narrative generation failed: {e}")
        return ""


def generate_image_caption(image_path: str, event_name: str) -> str:
    """Generate detailed caption for an image using Gemini Vision."""
    try:
        # Read image as base64
        with open(image_path, 'rb') as f:
            image_data = f.read()
        
        prompt = f"""
        This image is from an educational event called "{event_name}".
        Write a detailed, professional caption (1-2 sentences) describing what you see.
        Focus on: activity shown, participants visible, setting/venue if clear.
        Keep it factual and suitable for an accreditation report.
        """
        
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=[
                {"text": prompt},
                {"inline_data": {"mime_type": "image/jpeg", "data": image_data}}
            ]
        )
        return response.text.strip()
        
    except Exception as e:
        print(f"    Warning: Caption generation failed: {e}")
        return f"Event documentation: {event_name}"


def compile_enhanced_report(
    excel_path: str,
    criterion: str,
    output_dir: str = ".",
    generate_captions: bool = True
) -> Dict:
    """
    Generate enhanced compiled PDF report with:
    - Clickable Table of Contents
    - AI-generated narratives
    - Image thumbnails with captions
    - PDF bookmarks
    
    Returns dict with output path and statistics.
    """
    print(f"\n{'='*60}")
    print(f"NAAC Enhanced Report Compiler - Criterion {criterion}")
    print(f"{'='*60}")
    
    result = {
        "success": False,
        "output_path": None,
        "events_processed": 0,
        "images_added": 0,
        "pages": 0
    }
    
    # Clean up temp folder
    temp_dir = "temp_downloads"
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
    os.makedirs(temp_dir, exist_ok=True)
    
    # 1. Parse Excel
    print("\n[1/5] Parsing Excel data...")
    events = parse_criterion_sheet(excel_path, criterion)
    print(f"    Found {len(events)} events")
    
    if not events:
        result["error"] = "No events found in Excel"
        return result
    
    # 2. Initialize Drive fetcher
    print("\n[2/5] Connecting to Google Drive...")
    drive = GoogleDriveFetcher()
    if not drive.authenticate():
        result["error"] = "Drive authentication failed"
        return result
    
    # 3. Download and process content from Drive
    print("\n[3/5] Downloading and processing event content...")
    event_data = []  # List of {event, narrative, images, pdf_paths}
    
    for i, event in enumerate(events):
        url = event.get('doc_link', '')
        event_info = {
            "event": event,
            "narrative": "",
            "images": [],
            "pdf_paths": [],
            "doc_text": ""
        }
        
        print(f"\n    [{i+1}/{len(events)}] {event['name'][:50]}...")
        
        if url and 'drive.google.com' in url:
            event_dir = os.path.join(temp_dir, f"event_{i}")
            os.makedirs(event_dir, exist_ok=True)
            
            # Fetch content
            content = drive.fetch_folder_content(url, output_dir=event_dir)
            
            if content['success']:
                event_info["doc_text"] = content.get('text_content', '')
                
                # Process files
                for file_info in content.get('files', []):
                    if file_info.get('type') == 'pdf':
                        event_info["pdf_paths"].append(file_info.get('path'))
                        print(f"        ✓ PDF: {file_info['name'][:40]}")
                    elif file_info.get('type') == 'image':
                        img_path = file_info.get('path')
                        if img_path and os.path.exists(img_path):
                            # Generate caption
                            if generate_captions:
                                caption = generate_image_caption(img_path, event['name'])
                            else:
                                caption = file_info.get('name', 'Event image')
                            
                            event_info["images"].append({
                                "path": img_path,
                                "name": file_info.get('name'),
                                "caption": caption
                            })
                            result["images_added"] += 1
                            print(f"        ✓ Image: {file_info['name'][:40]}")
        
        # Generate AI narrative
        print(f"        Generating AI narrative...")
        event_info["narrative"] = generate_ai_narrative(event, event_info["doc_text"])
        
        event_data.append(event_info)
        result["events_processed"] += 1
    
    # 4. Create the enhanced PDF
    print("\n[4/5] Building enhanced PDF report...")
    
    # Get criterion title
    criterion_titles = {
        "5.1.3": "Capacity Building and Skills Enhancement Initiatives",
        "5.2.2": "Students Availing Government/Institutional Scholarships",
        "5.3.1": "Number of Awards/Medals for Outstanding Performance",
        "5.3.3": "Sports and Cultural Events"
    }
    title = criterion_titles.get(criterion, criterion)
    
    # Create PDF with cover and content
    pdf = EnhancedReportPDF()
    
    # Cover page
    pdf.add_cover_page(criterion, title)
    cover_pages = 1
    
    # Calculate page numbers for each event (estimate)
    page_map = {}
    current_page = cover_pages + 2  # Cover + Index (approx 1 page)
    
    for ed in event_data:
        page_map[ed['event']['name']] = current_page
        # Estimate pages per event: 1 base + 1 per 3 images + 1 per PDF
        img_pages = (len(ed['images']) + 2) // 3
        current_page += 1 + img_pages + len(ed['pdf_paths'])
    
    # Index page with page numbers
    pdf.add_index_page(events, page_map)
    
    # Event sections
    for ed in event_data:
        pdf.add_event_section(ed['event'], ed['narrative'], ed['images'])
    
    # Save intermediate PDF
    intermediate_path = os.path.join(temp_dir, "content.pdf")
    pdf.output(intermediate_path)
    print(f"    Created content PDF")
    
    # 5. Merge with source PDFs
    print("\n[5/5] Merging with source PDFs and adding bookmarks...")
    
    writer = PdfWriter()
    
    # Add content PDF
    content_reader = PdfReader(intermediate_path)
    for page in content_reader.pages:
        writer.add_page(page)
    
    # Add source PDFs for each event with bookmarks
    for ed in event_data:
        if ed['pdf_paths']:
            # Add bookmark for this event's PDFs
            bookmark_page = len(writer.pages)
            writer.add_outline_item(
                sanitize_text(f"{ed['event']['name'][:50]} - Source Documents"),
                bookmark_page
            )
            
            for pdf_path in ed['pdf_paths']:
                if os.path.exists(pdf_path):
                    try:
                        reader = PdfReader(pdf_path)
                        for page in reader.pages:
                            writer.add_page(page)
                    except Exception as e:
                        print(f"    Warning: Could not add {pdf_path}: {e}")
    
    # Save final output
    safe_criterion = criterion.replace(".", "_")
    output_path = os.path.join(output_dir, f"NAAC_Enhanced_{safe_criterion}.pdf")
    
    with open(output_path, 'wb') as f:
        writer.write(f)
    
    result["pages"] = len(writer.pages)
    result["output_path"] = output_path
    result["success"] = True
    
    print(f"\n{'='*60}")
    print(f"✅ Enhanced report saved: {output_path}")
    print(f"   Total pages: {result['pages']}")
    print(f"   Events processed: {result['events_processed']}")
    print(f"   Images added: {result['images_added']}")
    print(f"{'='*60}")
    
    return result


if __name__ == "__main__":
    excel_path = "data/Criteria 5.1.3 CMPN Data 2024-25.xlsx"
    compile_enhanced_report(excel_path, "5.1.3")
