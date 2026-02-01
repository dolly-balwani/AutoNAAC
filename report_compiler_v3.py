"""
NAAC Report Compiler V3 - PDF Merger Version
Merges individual event PDFs from Drive into one compiled report with index
"""
import os
import shutil
from typing import List, Dict
from pypdf import PdfReader, PdfWriter
from fpdf import FPDF
from dotenv import load_dotenv

from excel_parser import parse_criterion_sheet
from drive_fetcher import GoogleDriveFetcher

load_dotenv()


class IndexPDF(FPDF):
    """Generate index/cover page for the compiled report."""
    
    def __init__(self):
        super().__init__()
        self.set_auto_page_break(auto=True, margin=15)
    
    def safe_text(self, text: str, max_len: int = 200) -> str:
        if not text:
            return ""
        text = str(text)[:max_len]
        return ''.join(c if ord(c) < 256 else '?' for c in text)


def create_index_pdf(criterion: str, title: str, events: List[Dict], output_path: str):
    """Create an index/cover PDF for the compiled report."""
    pdf = IndexPDF()
    
    # Cover page
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 15, "Vivekanand Education Society's", new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.cell(0, 10, "Institute of Technology", new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 8, "(Affiliated to University of Mumbai, Approved by AICTE)", new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.ln(20)
    
    pdf.set_font("Helvetica", "B", 24)
    pdf.cell(0, 15, pdf.safe_text(criterion), new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.set_font("Helvetica", "B", 14)
    pdf.multi_cell(0, 10, pdf.safe_text(title), align="C")
    pdf.ln(20)
    
    # Index
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 10, "INDEX", new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.ln(5)
    
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(15, 8, "Sr.", border=1, align="C")
    pdf.cell(120, 8, "Event Name", border=1, align="C")
    pdf.cell(30, 8, "Date", border=1, align="C")
    pdf.cell(25, 8, "Students", border=1, align="C", new_x="LMARGIN", new_y="NEXT")
    
    pdf.set_font("Helvetica", "", 9)
    for i, event in enumerate(events):
        name = pdf.safe_text(event.get('name', ''), 60)
        date = str(event.get('date', ''))[:10]
        students = str(event.get('students', ''))[:10]
        
        pdf.cell(15, 7, str(i+1), border=1, align="C")
        pdf.cell(120, 7, name, border=1)
        pdf.cell(30, 7, date, border=1, align="C")
        pdf.cell(25, 7, students, border=1, align="C", new_x="LMARGIN", new_y="NEXT")
    
    pdf.output(output_path)
    return output_path


def merge_pdfs(pdf_paths: List[str], output_path: str) -> str:
    """Merge multiple PDFs into one."""
    writer = PdfWriter()
    
    for pdf_path in pdf_paths:
        if os.path.exists(pdf_path):
            try:
                reader = PdfReader(pdf_path)
                for page in reader.pages:
                    writer.add_page(page)
            except Exception as e:
                print(f"    Warning: Could not add {pdf_path}: {e}")
    
    with open(output_path, 'wb') as output_file:
        writer.write(output_file)
    
    return output_path


def generate_compiled_report(excel_path: str, criterion: str, output_dir: str = "."):
    """
    Generate a compiled PDF report by merging individual event PDFs from Drive.
    """
    print(f"\n{'='*60}")
    print(f"NAAC Report Compiler V3 - Criterion {criterion}")
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
    
    # 3. Download PDFs from each Drive folder
    print("\n[3/4] Downloading event reports from Drive...")
    event_pdfs = []
    
    for i, event in enumerate(events):
        url = event.get('doc_link', '')
        
        if url and 'drive.google.com' in url:
            event_dir = os.path.join(temp_dir, f"event_{i}")
            os.makedirs(event_dir, exist_ok=True)
            
            print(f"    [{i+1}/{len(events)}] {event['name'][:40]}...")
            result = drive.fetch_folder_content(url, output_dir=event_dir)
            
            if result['success']:
                # Collect all PDFs from this event
                for file_info in result.get('files', []):
                    if file_info.get('type') == 'pdf' and file_info.get('path'):
                        event_pdfs.append({
                            'event': event['name'],
                            'path': file_info['path']
                        })
                        print(f"        ✓ Added: {file_info['name'][:40]}")
            else:
                print(f"        ✗ {result.get('error', 'Unknown error')}")
    
    print(f"\n    Total PDFs collected: {len(event_pdfs)}")
    
    # 4. Create compiled report
    print("\n[4/4] Compiling final report...")
    
    # Create index PDF
    criterion_titles = {
        "5.1.3": "Capacity Building and Skills Enhancement Initiatives",
        "5.2.2": "Students Availing Government/Institutional Scholarships",
        "5.3.1": "Number of Awards/Medals for Outstanding Performance"
    }
    title = criterion_titles.get(criterion, criterion)
    
    index_path = os.path.join(temp_dir, "00_index.pdf")
    create_index_pdf(criterion, title, events, index_path)
    print(f"    Created index page")
    
    # Merge all PDFs: index + event PDFs
    all_pdfs = [index_path] + [p['path'] for p in event_pdfs]
    
    safe_criterion = criterion.replace(".", "_")
    output_path = os.path.join(output_dir, f"NAAC_Compiled_{safe_criterion}.pdf")
    
    merge_pdfs(all_pdfs, output_path)
    
    # Get page count
    reader = PdfReader(output_path)
    page_count = len(reader.pages)
    
    print(f"\n{'='*60}")
    print(f"✅ Compiled report saved: {output_path}")
    print(f"   Total pages: {page_count}")
    print(f"   Event PDFs merged: {len(event_pdfs)}")
    print(f"{'='*60}")
    
    return output_path


if __name__ == "__main__":
    excel_path = "data/Criteria 5.1.3 CMPN Data 2024-25.xlsx"
    generate_compiled_report(excel_path, "5.1.3")
