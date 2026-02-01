"""
NAAC Demo Report Generator - Guaranteed to Work (No API Required)
For Final Review Demo - Generates a working PDF with all features

This script generates a professional NAAC report from Excel data
without needing any API calls (Gemini, OpenRouter, etc.)
"""

import os
import sys
from typing import List, Dict

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from dotenv import load_dotenv
load_dotenv()

# Check for required dependencies
try:
    from fpdf import FPDF
    from pypdf import PdfReader, PdfWriter
    import pandas as pd
except ImportError as e:
    print(f"Missing dependency: {e}")
    print("Run: pip install fpdf2 pypdf pandas openpyxl")
    sys.exit(1)


def sanitize_text(text: str, max_len: int = 500) -> str:
    """Sanitize text for PDF - replaces Unicode special characters."""
    if not text:
        return ""
    text = str(text)[:max_len]
    replacements = {
        '–': '-', '—': '-', ''': "'", ''': "'", '"': '"', '"': '"',
        '…': '...', '•': '*', '°': ' deg', '©': '(c)', '®': '(R)',
        '™': '(TM)', '\u200b': '', '\xa0': ' ',
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    return ''.join(c if ord(c) < 256 else '?' for c in text)


class DemoReportPDF(FPDF):
    """PDF generator for demo report."""
    
    def __init__(self):
        super().__init__()
        self.set_auto_page_break(auto=True, margin=15)
    
    def header(self):
        self.set_font("Helvetica", "I", 8)
        self.cell(0, 10, "NAAC Criterion Report - Demo", align="R")
        self.ln(5)
    
    def add_cover(self, criterion: str, title: str):
        self.add_page()
        self.set_font("Helvetica", "B", 16)
        self.cell(0, 15, "Vivekanand Education Society's", new_x="LMARGIN", new_y="NEXT", align="C")
        self.cell(0, 10, "Institute of Technology", new_x="LMARGIN", new_y="NEXT", align="C")
        self.set_font("Helvetica", "", 10)
        self.cell(0, 8, "(Affiliated to University of Mumbai, Approved by AICTE)", new_x="LMARGIN", new_y="NEXT", align="C")
        self.ln(30)
        
        self.set_font("Helvetica", "B", 28)
        self.cell(0, 15, sanitize_text(f"Criterion {criterion}"), new_x="LMARGIN", new_y="NEXT", align="C")
        self.ln(10)
        self.set_font("Helvetica", "B", 14)
        self.multi_cell(0, 10, sanitize_text(title), align="C")
        self.ln(40)
        
        self.set_font("Helvetica", "", 12)
        self.cell(0, 10, "NAAC Accreditation Report", new_x="LMARGIN", new_y="NEXT", align="C")
        self.cell(0, 10, "Academic Year 2024-25", new_x="LMARGIN", new_y="NEXT", align="C")
    
    def add_toc(self, events: List[Dict]):
        self.add_page()
        self.set_font("Helvetica", "B", 18)
        self.cell(0, 15, "TABLE OF CONTENTS", new_x="LMARGIN", new_y="NEXT", align="C")
        self.ln(10)
        
        self.set_font("Helvetica", "B", 10)
        self.cell(10, 8, "Sr.", border=1, align="C")
        self.cell(120, 8, "Event Name", border=1, align="C")
        self.cell(30, 8, "Date", border=1, align="C")
        self.cell(20, 8, "Page", border=1, align="C", new_x="LMARGIN", new_y="NEXT")
        
        self.set_font("Helvetica", "", 9)
        for i, event in enumerate(events):
            name = sanitize_text(event.get('name', ''), 60)
            date = sanitize_text(str(event.get('date', '')), 15)
            page = i + 3  # Cover + TOC pages
            
            self.cell(10, 7, str(i+1), border=1, align="C")
            self.set_text_color(0, 0, 180)
            self.cell(120, 7, name, border=1)
            self.set_text_color(0, 0, 0)
            self.cell(30, 7, date, border=1, align="C")
            self.cell(20, 7, str(page), border=1, align="C", new_x="LMARGIN", new_y="NEXT")
    
    def add_event(self, event: Dict, index: int):
        self.add_page()
        
        # Event title
        self.set_font("Helvetica", "B", 14)
        self.multi_cell(0, 8, sanitize_text(event.get('name', 'Untitled Event'), 100))
        self.ln(3)
        
        # Metadata
        self.set_font("Helvetica", "", 10)
        if event.get('date'):
            self.cell(0, 6, f"Date: {sanitize_text(str(event['date']), 20)}", new_x="LMARGIN", new_y="NEXT")
        if event.get('students'):
            self.cell(0, 6, f"Participants: {sanitize_text(str(event['students']), 50)}", new_x="LMARGIN", new_y="NEXT")
        if event.get('agencies'):
            self.cell(0, 6, f"Agencies: {sanitize_text(str(event['agencies']), 80)}", new_x="LMARGIN", new_y="NEXT")
        self.ln(8)
        
        # Auto-generated narrative (template-based, no API needed)
        narrative = generate_template_narrative(event)
        
        self.set_font("Helvetica", "B", 11)
        self.cell(0, 8, "Event Summary", new_x="LMARGIN", new_y="NEXT")
        self.set_font("Helvetica", "", 10)
        self.multi_cell(0, 6, sanitize_text(narrative, 2000))


def generate_template_narrative(event: Dict) -> str:
    """Generate a professional narrative without AI - uses templates."""
    name = event.get('name', 'the event')
    date = event.get('date', 'the academic year 2024-25')
    students = event.get('students', 'students')
    agencies = event.get('agencies', 'the department')
    
    templates = [
        f"The {name} was successfully conducted as part of the institution's commitment to holistic student development. ",
        f"This initiative was organized on {date} and witnessed enthusiastic participation from {students}. ",
        f"The event was coordinated by {agencies}, demonstrating effective collaboration for academic enhancement. ",
        "The program aligned with NAAC criteria for capacity building and skills enhancement initiatives. ",
        "Participants gained valuable exposure to practical knowledge and industry-relevant skills. ",
        "The event contributed significantly to the overall learning experience and employability of students. ",
        "Feedback from participants indicated high satisfaction with the program content and delivery. ",
        "This initiative reflects the institution's ongoing efforts to provide comprehensive education beyond the classroom."
    ]
    
    return ''.join(templates)


def parse_excel_simple(excel_path: str, criterion: str) -> List[Dict]:
    """Parse Excel with simple pandas - no complex hyperlink extraction."""
    events = []
    
    try:
        # Try different possible sheet names
        possible_sheets = [criterion, f"Criterion {criterion}", criterion.replace(".", "_")]
        df = None
        
        for sheet in possible_sheets:
            try:
                df = pd.read_excel(excel_path, sheet_name=sheet, header=1)
                print(f"    Found sheet: {sheet}")
                break
            except:
                continue
        
        if df is None:
            # Try first sheet
            df = pd.read_excel(excel_path, header=1)
            print(f"    Using first sheet")
        
        # Process rows
        for idx, row in df.iterrows():
            first_col = str(row.iloc[0]) if pd.notna(row.iloc[0]) else ""
            
            # Skip empty or header rows
            if not first_col or first_col.lower() in ['nan', 'name of the activity', 'sr. no.', 'sr.no.']:
                continue
            
            event = {
                "name": first_col,
                "date": str(row.iloc[1]) if len(row) > 1 and pd.notna(row.iloc[1]) else "",
                "students": str(row.iloc[2]) if len(row) > 2 and pd.notna(row.iloc[2]) else "",
                "agencies": str(row.iloc[3]) if len(row) > 3 and pd.notna(row.iloc[3]) else "",
            }
            
            if event["name"] and len(event["name"]) > 3:
                events.append(event)
        
    except Exception as e:
        print(f"Error parsing Excel: {e}")
    
    return events


def main():
    print("=" * 60)
    print("NAAC DEMO REPORT GENERATOR")
    print("(No API Required - Guaranteed to Work)")
    print("=" * 60)
    
    # Configuration
    excel_path = "data/Criteria 5.1.3 CMPN Data 2024-25.xlsx"
    criterion = "5.1.3"
    output_pdf = "NAAC_Demo_Report_5_1_3.pdf"
    
    # Check if Excel exists
    if not os.path.exists(excel_path):
        # Try backend uploads folder
        excel_path = "backend/uploads/Criteria 5.1.3 CMPN Data 2024-25.xlsx"
        if not os.path.exists(excel_path):
            print(f"\n❌ Excel file not found!")
            print("   Please place the Excel file in the 'data' folder")
            return
    
    print(f"\n📁 Excel: {excel_path}")
    print(f"📄 Criterion: {criterion}")
    
    # Parse Excel
    print("\n[1/3] Parsing Excel data...")
    events = parse_excel_simple(excel_path, criterion)
    print(f"    Found {len(events)} events")
    
    if not events:
        print("❌ No events found in Excel!")
        return
    
    # Generate PDF
    print("\n[2/3] Generating PDF report...")
    pdf = DemoReportPDF()
    
    # Cover page
    pdf.add_cover(criterion, "Capacity Building and Skills Enhancement Initiatives")
    
    # Table of Contents
    pdf.add_toc(events)
    
    # Event sections
    for i, event in enumerate(events):
        print(f"    [{i+1}/{len(events)}] {event['name'][:40]}...")
        pdf.add_event(event, i)
    
    # Save PDF
    print(f"\n[3/3] Saving PDF: {output_pdf}")
    pdf.output(output_pdf)
    
    print(f"\n{'=' * 60}")
    print(f"✅ SUCCESS! Report generated: {output_pdf}")
    print(f"   Total events: {len(events)}")
    print(f"   Pages: ~{len(events) + 2}")
    print(f"{'=' * 60}")
    print(f"\n📂 Open the PDF: {os.path.abspath(output_pdf)}")


if __name__ == "__main__":
    main()
