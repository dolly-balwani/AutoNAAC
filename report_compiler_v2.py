"""
Enhanced Report Compiler with Google Drive Integration
Generates formatted PDF reports with images and content from Drive folders
"""
import os
import shutil
from typing import List, Dict
from fpdf import FPDF
from google import genai
from dotenv import load_dotenv
from pypdf import PdfReader

from excel_parser import parse_criterion_sheet
from drive_fetcher import GoogleDriveFetcher

load_dotenv()

# Initialize Gemini
client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
MODEL_NAME = "gemini-2.5-flash-lite"


def extract_pdf_text(pdf_path: str) -> str:
    """Extract text content from a PDF file."""
    try:
        reader = PdfReader(pdf_path)
        text = ""
        for page in reader.pages[:3]:  # First 3 pages only
            text += page.extract_text() or ""
        return text.strip()
    except Exception as e:
        return ""

class EnhancedNAACReport(FPDF):
    """Enhanced PDF class for NAAC reports with image support."""
    
    def __init__(self):
        super().__init__()
        self.set_auto_page_break(auto=True, margin=20)
        self.set_left_margin(15)
        self.set_right_margin(15)
    
    def safe_text(self, text: str, max_len: int = 500) -> str:
        """Sanitize text for PDF output."""
        if not text:
            return ""
        text = str(text)[:max_len]
        text = ''.join(c if ord(c) < 256 else '?' for c in text)
        return text
    
    def header(self):
        self.set_font("Helvetica", "B", 14)
        self.cell(0, 10, "NAAC Self-Study Report 2024-25", new_x="LMARGIN", new_y="NEXT", align="C")
        self.set_font("Helvetica", "", 10)
        self.cell(0, 6, "Vivekanand Education Society's Institute of Technology", new_x="LMARGIN", new_y="NEXT", align="C")
        self.ln(5)
        self.set_draw_color(0, 0, 0)
        self.line(15, self.get_y(), 195, self.get_y())
        self.ln(5)
    
    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.cell(0, 10, f"Page {self.page_no()}", align="C")
    
    def add_criterion_title(self, criterion: str, title: str):
        self.add_page()
        self.set_font("Helvetica", "B", 18)
        self.set_text_color(0, 51, 102)
        self.cell(0, 12, self.safe_text(f"Criterion {criterion}"), new_x="LMARGIN", new_y="NEXT", align="C")
        self.set_font("Helvetica", "B", 12)
        self.multi_cell(0, 8, self.safe_text(title, 150), align="C")
        self.set_text_color(0, 0, 0)
        self.ln(10)
    
    def add_event_section(self, event: dict, images: List[str] = None, text_content: str = None):
        """Add an event section with optional images and text content."""
        # Check if we need a new page
        if self.get_y() > 220:
            self.add_page()
        
        # Event title with background
        self.set_fill_color(240, 240, 240)
        self.set_font("Helvetica", "B", 11)
        name = self.safe_text(event.get('name', 'Event'), 100)
        self.cell(0, 8, name, new_x="LMARGIN", new_y="NEXT", fill=True)
        
        # Event details in a structured format
        self.set_font("Helvetica", "", 10)
        
        # Date
        if event.get('date'):
            date_str = str(event['date'])
            if '00:00:00' in date_str:
                date_str = date_str.split(' ')[0]
            self.cell(30, 6, "Date:", new_x="RIGHT")
            self.cell(0, 6, self.safe_text(date_str, 30), new_x="LMARGIN", new_y="NEXT")
        
        # Participants
        if event.get('students'):
            self.cell(30, 6, "Participants:", new_x="RIGHT")
            self.cell(0, 6, self.safe_text(str(event['students']), 20), new_x="LMARGIN", new_y="NEXT")
        
        # Facilitators
        if event.get('agencies'):
            self.cell(30, 6, "Facilitators:", new_x="RIGHT")
            self.multi_cell(0, 6, self.safe_text(str(event['agencies']), 80))
        
        # Add text content from Drive if available
        if text_content:
            self.ln(3)
            self.set_font("Helvetica", "B", 9)
            self.cell(0, 5, "Evidence/Report Content:", new_x="LMARGIN", new_y="NEXT")
            self.set_font("Helvetica", "", 9)
            self.set_text_color(50, 50, 50)
            # Show first 600 chars of content
            self.multi_cell(0, 5, self.safe_text(text_content, 600))
            self.set_text_color(0, 0, 0)
        
        # Add images if available
        if images:
            self.ln(3)
            for img_path in images[:2]:  # Limit to 2 images per event
                if os.path.exists(img_path):
                    try:
                        # Calculate image size (max width 80mm, max height 60mm)
                        self.image(img_path, x=None, y=None, w=80)
                        self.ln(3)
                    except Exception as e:
                        self.set_font("Helvetica", "I", 8)
                        self.cell(0, 5, f"[Image: {os.path.basename(img_path)}]", new_x="LMARGIN", new_y="NEXT")
        
        self.ln(5)
    
    def add_summary(self, summary: str):
        self.add_page()
        self.set_font("Helvetica", "B", 14)
        self.set_text_color(0, 51, 102)
        self.cell(0, 10, "Executive Summary", new_x="LMARGIN", new_y="NEXT", align="C")
        self.set_text_color(0, 0, 0)
        self.ln(5)
        self.set_font("Helvetica", "", 11)
        self.multi_cell(0, 7, self.safe_text(summary, 2000))


def generate_ai_summary(criterion: str, events: List[Dict]) -> str:
    """Generate AI summary for the criterion using Gemini."""
    event_list = "\n".join([
        f"- {e['name']} ({e.get('date', 'N/A')}): {e.get('students', 'N/A')} participants" 
        for e in events[:15]
    ])
    
    prompt = f"""Write a professional 200-word executive summary for NAAC Criterion {criterion}.

Events conducted during 2024-25:
{event_list}

The summary should:
1. Highlight the institution's commitment to student development
2. Mention the variety of programs (soft skills, ICT, career guidance)
3. Note the strong participation numbers
4. Be formal and suitable for NAAC accreditation report
5. Start with "The institution..."
"""
    
    try:
        response = client.models.generate_content(model=MODEL_NAME, contents=prompt)
        return response.text
    except Exception as e:
        return f"Summary generation failed: {e}"


def generate_full_report(excel_path: str, criterion: str, output_dir: str = "."):
    """
    Generate a full enhanced PDF report with images from Google Drive.
    """
    print(f"\n{'='*60}")
    print(f"Enhanced Report Generator for Criterion {criterion}")
    print(f"{'='*60}")
    
    # Clean up temp folder
    temp_dir = "temp_downloads"
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
    os.makedirs(temp_dir, exist_ok=True)
    
    # 1. Parse Excel
    print("\n[1/4] Parsing Excel data...")
    events = parse_criterion_sheet(excel_path, criterion)
    print(f"    Found {len(events)} events")
    
    if not events:
        print("    ERROR: No events found!")
        return None
    
    # 2. Initialize Drive fetcher
    print("\n[2/4] Connecting to Google Drive...")
    drive = GoogleDriveFetcher()
    if not drive.authenticate():
        print("    ERROR: Drive authentication failed!")
        return None
    
    # 3. Fetch content from each Drive folder
    print("\n[3/4] Fetching evidence from Drive folders...")
    for i, event in enumerate(events):
        url = event.get('doc_link', '')
        event['images'] = []
        event['text_content'] = ''
        
        if url and 'drive.google.com' in url:
            event_dir = os.path.join(temp_dir, f"event_{i}")
            os.makedirs(event_dir, exist_ok=True)
            
            print(f"    [{i+1}/{len(events)}] {event['name'][:40]}...")
            result = drive.fetch_folder_content(url, output_dir=event_dir)
            
            if result['success']:
                event['images'] = result.get('images', [])
                # Get text from Google Docs
                event['text_content'] = result.get('text_content', '')
                
                # Also extract text from downloaded PDFs
                for file_info in result.get('files', []):
                    if file_info.get('type') == 'pdf' and file_info.get('path'):
                        pdf_text = extract_pdf_text(file_info['path'])
                        if pdf_text:
                            event['text_content'] += "\n" + pdf_text
                
                print(f"        ✓ Found {len(event['images'])} images, {len(event['text_content'])} chars text")
            else:
                print(f"        ✗ {result.get('error', 'Unknown error')}")
    
    # 4. Generate AI summary
    print("\n[4/4] Generating executive summary...")
    summary = generate_ai_summary(criterion, events)
    print(f"    Summary generated ({len(summary)} chars)")
    
    # 5. Create PDF
    print("\nCreating PDF report...")
    pdf = EnhancedNAACReport()
    
    # Criterion titles
    criterion_titles = {
        "5.1.3": "Capacity Building and Skills Enhancement Initiatives",
        "5.2.2": "Students Availing Government/Institutional Scholarships",
        "5.3.1": "Number of Awards/Medals for Outstanding Performance"
    }
    title = criterion_titles.get(criterion, criterion)
    pdf.add_criterion_title(criterion, title)
    
    # Add each event section with images and text content
    for event in events:
        pdf.add_event_section(event, event.get('images', []), event.get('text_content', ''))
    
    # Add summary
    pdf.add_summary(summary)
    
    # Save PDF
    safe_criterion = criterion.replace(".", "_")
    output_path = os.path.join(output_dir, f"NAAC_Report_{safe_criterion}_Full.pdf")
    pdf.output(output_path)
    
    print(f"\n{'='*60}")
    print(f"✅ Report saved to: {output_path}")
    print(f"{'='*60}")
    
    return output_path


if __name__ == "__main__":
    excel_path = "data/Criteria 5.1.3 CMPN Data 2024-25.xlsx"
    generate_full_report(excel_path, "5.1.3")
