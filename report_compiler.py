"""
Enhanced Report Compiler for NAAC Criteria
Generates formatted PDF reports with per-event sections
"""
import os
from typing import List, Dict
from fpdf import FPDF
from google import genai
from dotenv import load_dotenv

from excel_parser import parse_criterion_sheet, get_available_criteria
from google_docs_fetcher import fetch_google_doc_content

load_dotenv()

# Initialize Gemini
client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
MODEL_NAME = "gemini-2.5-flash-lite"

class NAACReportPDF(FPDF):
    """Custom PDF class for NAAC reports."""
    
    def __init__(self):
        super().__init__()
        self.set_auto_page_break(auto=True, margin=20)
        self.set_left_margin(20)
        self.set_right_margin(20)
    
    def safe_text(self, text: str, max_len: int = 200) -> str:
        """Sanitize text for PDF output."""
        if not text:
            return ""
        # Truncate and encode safely
        text = str(text)[:max_len]
        # Remove problematic characters
        text = ''.join(c if ord(c) < 256 else '?' for c in text)
        return text
    
    def header(self):
        self.set_font("Helvetica", "B", 12)
        self.cell(0, 10, "NAAC Self-Study Report", new_x="LMARGIN", new_y="NEXT", align="C")
        self.ln(5)
    
    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.cell(0, 10, f"Page {self.page_no()}", align="C")
    
    def add_criterion_title(self, criterion: str, title: str):
        self.add_page()
        self.set_font("Helvetica", "B", 16)
        self.cell(0, 12, self.safe_text(f"Criterion {criterion}", 50), new_x="LMARGIN", new_y="NEXT", align="C")
        self.set_font("Helvetica", "B", 12)
        self.multi_cell(0, 8, self.safe_text(title, 100), align="C")
        self.ln(10)
    
    def add_event_section(self, event: dict, evidence: str = None):
        # Event title
        self.set_font("Helvetica", "B", 11)
        name = self.safe_text(event.get('name', 'Event'), 80)
        self.multi_cell(0, 7, name)
        
        # Event details on separate lines
        self.set_font("Helvetica", "", 10)
        
        if event.get('date'):
            self.cell(0, 6, f"Date: {self.safe_text(str(event['date']), 30)}", new_x="LMARGIN", new_y="NEXT")
        if event.get('students'):
            self.cell(0, 6, f"Participants: {self.safe_text(str(event['students']), 20)}", new_x="LMARGIN", new_y="NEXT")
        if event.get('agencies'):
            self.cell(0, 6, f"Facilitators: {self.safe_text(str(event['agencies']), 50)}", new_x="LMARGIN", new_y="NEXT")
        
        # Evidence from Google Doc
        if evidence:
            self.set_font("Helvetica", "I", 9)
            self.set_text_color(80, 80, 80)
            self.multi_cell(0, 5, f"Evidence: {self.safe_text(evidence, 300)}...")
            self.set_text_color(0, 0, 0)
        
        self.ln(5)
    
    def add_summary(self, summary: str):
        self.set_font("Helvetica", "B", 12)
        self.cell(0, 10, "Summary", new_x="LMARGIN", new_y="NEXT")
        self.set_font("Helvetica", "", 10)
        self.multi_cell(0, 6, self.safe_text(summary, 1500))

def generate_ai_summary(criterion: str, events: List[Dict]) -> str:
    """Generate AI summary for the criterion using Gemini."""
    event_list = "\n".join([f"- {e['name']} ({e.get('date', 'N/A')}): {e.get('students', 'N/A')} students" 
                           for e in events[:15]])
    
    prompt = f"""Write a professional 150-word summary for NAAC Criterion {criterion}.
    
Events conducted:
{event_list}

The summary should:
1. Highlight the institution's commitment to capacity building
2. Mention specific types of programs (soft skills, ICT, life skills)
3. Note the participation numbers
4. Be formal and suitable for NAAC accreditation report
"""
    
    try:
        response = client.models.generate_content(model=MODEL_NAME, contents=prompt)
        return response.text
    except Exception as e:
        return f"Summary generation failed: {e}"

def generate_enhanced_report(excel_path: str, criterion: str, output_dir: str = "."):
    """
    Generate an enhanced PDF report for a specific criterion.
    """
    print(f"\n{'='*60}")
    print(f"Generating Enhanced Report for Criterion {criterion}")
    print(f"{'='*60}")
    
    # 1. Parse Excel
    print("\n[1/4] Parsing Excel data...")
    events = parse_criterion_sheet(excel_path, criterion)
    print(f"    Found {len(events)} events")
    
    if not events:
        print("    ERROR: No events found!")
        return None
    
    # 2. Fetch Google Docs content
    print("\n[2/4] Fetching Google Docs evidence...")
    for event in events:
        doc_link = event.get('doc_link', '')
        if doc_link and 'google' in doc_link.lower():
            result = fetch_google_doc_content(doc_link)
            if result['success']:
                event['evidence'] = result['content'][:500]
                print(f"    ✓ Fetched: {event['name'][:30]}...")
            else:
                event['evidence'] = None
                print(f"    ✗ Skipped: {event['name'][:30]}... ({result['error']})")
        else:
            event['evidence'] = None
    
    # 3. Generate AI summary
    print("\n[3/4] Generating AI summary...")
    summary = generate_ai_summary(criterion, events)
    print(f"    Summary generated ({len(summary)} chars)")
    
    # 4. Create PDF
    print("\n[4/4] Creating PDF report...")
    pdf = NAACReportPDF()
    
    # Criterion title
    criterion_titles = {
        "5.1.3": "Capacity building and skills enhancement initiatives",
        "5.2.2": "Students availing government/institutional scholarships",
        "5.3.1": "Number of awards/medals for outstanding performance"
    }
    title = criterion_titles.get(criterion, "")
    pdf.add_criterion_title(criterion, title)
    
    # Add each event section
    for event in events:
        pdf.add_event_section(event, event.get('evidence'))
    
    # Add summary
    pdf.add_page()
    pdf.add_summary(summary)
    
    # Save PDF
    safe_criterion = criterion.replace(".", "_")
    output_path = os.path.join(output_dir, f"NAAC_Report_{safe_criterion}.pdf")
    pdf.output(output_path)
    
    print(f"\n{'='*60}")
    print(f"✅ Report saved to: {output_path}")
    print(f"{'='*60}")
    
    return output_path

if __name__ == "__main__":
    excel_path = "data/Criteria 5.1.3 CMPN Data 2024-25.xlsx"
    generate_enhanced_report(excel_path, "5.1.3")
