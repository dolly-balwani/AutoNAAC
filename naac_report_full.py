"""
NAAC Enhanced Report Generator
Uses OpenRouter AI (FREE, no quota limits) + Google Drive Images

Features:
- AI-generated structured reports (Title, Objective, Planning, etc.)
- Images extracted from Google Drive
- Your college's PDF format
- No quota limits using OpenRouter's free models
"""

import os
import sys
import time
import re
import pandas as pd
from typing import List, Dict, Optional
from dotenv import load_dotenv

load_dotenv()

# Check dependencies
try:
    from reportlab.lib.pagesizes import A4
    from reportlab.platypus import SimpleDocTemplate, Image, Spacer, PageBreak, Paragraph, Table, TableStyle
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.lib import colors
    from pydrive2.auth import GoogleAuth
    from pydrive2.drive import GoogleDrive
    from langchain_openai import ChatOpenAI
    from langchain_core.prompts import PromptTemplate
    from langchain_core.output_parsers import JsonOutputParser
    from pydantic import BaseModel
    from openpyxl import load_workbook
except ImportError as e:
    print(f"Missing dependency: {e}")
    print("Run: pip install reportlab pydrive2 langchain-openai langchain-core pydantic openpyxl pandas python-dotenv")
    sys.exit(1)


# ============================================================================
# CONFIGURATION
# ============================================================================
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
EXCEL_FILE = "data/Criteria 5.1.3 CMPN Data 2024-25.xlsx"
SHEET_NAME = "5.1.3"
PDF_OUTPUT = "NAAC_Report_5.1.3_Enhanced.pdf"
LOGO_FILE = "vesit.png"
MAX_IMAGES_PER_EVENT = 5

# College branding colors
VESIT_BLUE = colors.HexColor('#1f4788')
VESIT_GOLD = colors.HexColor('#c9a227')


# ============================================================================
# PYDANTIC MODEL FOR AI OUTPUT
# ============================================================================
class EventReport(BaseModel):
    Title: str
    Objective: str
    Planning: str
    Participation: str
    Evidence: str
    Examples: str
    Conclusion: str


# ============================================================================
# TEXT SANITIZATION
# ============================================================================
def sanitize_text(text: str, max_len: int = 2000) -> str:
    """Sanitize text for PDF - replaces Unicode special characters."""
    if not text:
        return ""
    text = str(text)[:max_len]
    replacements = {
        '–': '-', '—': '-', ''': "'", ''': "'", '"': '"', '"': '"',
        '…': '...', '•': '*', '°': 'deg', '©': '(c)', '®': '(R)',
        '™': '(TM)', '\u200b': '', '\xa0': ' ', '\n': ' ', '\r': '',
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    return ''.join(c if ord(c) < 256 else '' for c in text)


# ============================================================================
# GOOGLE DRIVE FUNCTIONS
# ============================================================================
def init_google_drive():
    """Initialize Google Drive connection."""
    print("\n🔐 Authenticating with Google Drive...")
    try:
        gauth = GoogleAuth()
        gauth.LocalWebserverAuth()
        drive = GoogleDrive(gauth)
        print("✅ Google Drive authenticated!")
        return drive
    except Exception as e:
        print(f"⚠️ Google Drive auth failed: {e}")
        print("   Continuing without image extraction...")
        return None


def extract_drive_id(url: str) -> Optional[tuple]:
    """Extract file/folder ID from Google Drive URL."""
    if not url:
        return None, None
    
    folder_match = re.search(r'/folders/([a-zA-Z0-9_-]+)', url)
    if folder_match:
        return folder_match.group(1), 'folder'
    
    file_match = re.search(r'/file/d/([a-zA-Z0-9_-]+)', url)
    if file_match:
        return file_match.group(1), 'file'
    
    id_match = re.search(r'id=([a-zA-Z0-9_-]+)', url)
    if id_match:
        return id_match.group(1), 'unknown'
    
    return None, None


def extract_links_from_excel_row(excel_file: str, sheet_name: str, row_idx: int) -> List[str]:
    """Extract hyperlinks from Excel row."""
    links = []
    try:
        wb = load_workbook(excel_file, data_only=False)
        if sheet_name in wb.sheetnames:
            ws = wb[sheet_name]
            actual_row = row_idx + 3  # Account for header
            for cell in ws[actual_row]:
                if cell.hyperlink and cell.hyperlink.target:
                    links.append(cell.hyperlink.target)
    except Exception as e:
        pass
    return links


def download_images_from_folder(drive, folder_id: str, max_images: int = 5, depth: int = 0) -> List[str]:
    """Download images from Drive folder recursively."""
    images = []
    if depth > 2 or not drive:
        return images
    
    try:
        # Get images
        image_files = drive.ListFile({
            'q': f"'{folder_id}' in parents and trashed=false and mimeType contains 'image/'"
        }).GetList()
        
        for file in image_files[:max_images]:
            try:
                filename = f"temp_img_{folder_id[:8]}_{file['title']}"
                file.GetContentFile(filename)
                images.append(filename)
                print(f"      ✓ Downloaded: {file['title'][:30]}")
            except:
                continue
        
        # Check subfolders
        if len(images) < max_images:
            subfolders = drive.ListFile({
                'q': f"'{folder_id}' in parents and trashed=false and mimeType='application/vnd.google-apps.folder'"
            }).GetList()
            
            for subfolder in subfolders[:2]:
                remaining = max_images - len(images)
                if remaining > 0:
                    sub_images = download_images_from_folder(drive, subfolder['id'], remaining, depth + 1)
                    images.extend(sub_images)
    except Exception as e:
        print(f"      ⚠️ Folder access error: {e}")
    
    return images


# ============================================================================
# AI REPORT GENERATION
# ============================================================================
def init_llm():
    """Initialize OpenRouter LLM."""
    print("\n🤖 Initializing OpenRouter AI...")
    
    if not OPENROUTER_API_KEY:
        print("❌ OPENROUTER_API_KEY not found in .env!")
        return None
    
    try:
        llm = ChatOpenAI(
            model="google/gemma-3-27b-it:free",  # Free model, no limits
            base_url="https://openrouter.ai/api/v1",
            api_key=OPENROUTER_API_KEY,
            temperature=0.3,
        )
        print("✅ OpenRouter AI ready (using Gemma 3 - FREE)")
        return llm
    except Exception as e:
        print(f"❌ LLM init failed: {e}")
        return None


def generate_ai_report(llm, event_data: str) -> Optional[Dict]:
    """Generate structured report using AI."""
    if not llm:
        return None
    
    parser = JsonOutputParser(pydantic_object=EventReport)
    
    prompt = PromptTemplate(
        input_variables=["event"],
        partial_variables={"format_instructions": parser.get_format_instructions()},
        template="""You are an expert academic writer for NAAC Accreditation reports.
Write a professional, detailed report for this event/initiative.

Event Data:
{event}

Provide comprehensive content for each section:

1. **Title**: Create a clear, professional title (3-7 words). Do NOT include "Criterion" prefix.

2. **Objective**: What were the goals and intended outcomes? (3-5 detailed sentences)

3. **Planning**: How was this organized, timeline, resources used? (4-6 sentences)

4. **Participation**: Who participated - numbers, categories, engagement levels? (4-6 sentences)

5. **Evidence**: What evidence shows successful conduct and impact? (3-5 sentences)

6. **Examples**: Specific examples of implementation and outcomes? (4-6 sentences)

7. **Conclusion**: Overall impact, achievements, and future recommendations? (5-7 sentences)

Write in formal academic English. Be specific and detailed.

{format_instructions}"""
    )
    
    try:
        chain = prompt | llm | parser
        result = chain.invoke({"event": event_data})
        return result
    except Exception as e:
        print(f"      ⚠️ AI generation failed: {e}")
        return None


# ============================================================================
# PDF GENERATION - COLLEGE FORMAT
# ============================================================================
def create_pdf_report(events_data: List[Dict], output_path: str):
    """Create PDF in college format."""
    print(f"\n📄 Creating PDF: {output_path}")
    
    doc = SimpleDocTemplate(output_path, pagesize=A4, 
                           leftMargin=0.75*inch, rightMargin=0.75*inch,
                           topMargin=0.75*inch, bottomMargin=0.75*inch)
    width, height = A4
    story = []
    styles = getSampleStyleSheet()
    
    # Custom styles matching college format
    title_style = ParagraphStyle(
        "CollegeTitle",
        parent=styles['Heading1'],
        fontSize=22,
        textColor=VESIT_BLUE,
        spaceAfter=12,
        alignment=1,
        fontName='Helvetica-Bold'
    )
    
    heading_style = ParagraphStyle(
        "EventHeading",
        parent=styles['Heading2'],
        fontSize=16,
        textColor=VESIT_BLUE,
        spaceBefore=12,
        spaceAfter=8,
        fontName='Helvetica-Bold'
    )
    
    section_label = ParagraphStyle(
        "SectionLabel",
        parent=styles['Normal'],
        fontSize=11,
        textColor=VESIT_BLUE,
        fontName='Helvetica-Bold',
        spaceBefore=8,
        spaceAfter=4
    )
    
    body_style = ParagraphStyle(
        "BodyText",
        parent=styles['Normal'],
        fontSize=11,
        spaceAfter=6,
        alignment=4,  # Justify
        leading=14
    )
    
    # Cover Page
    story.append(Spacer(1, 0.5*inch))
    
    # Logo
    if os.path.exists(LOGO_FILE):
        try:
            logo = Image(LOGO_FILE, width=5*inch, height=1.2*inch, hAlign="CENTER")
            story.append(logo)
        except:
            pass
    
    story.append(Spacer(1, 0.3*inch))
    story.append(Paragraph("Vivekanand Education Society's", title_style))
    story.append(Paragraph("INSTITUTE OF TECHNOLOGY", title_style))
    story.append(Spacer(1, 0.1*inch))
    story.append(Paragraph("(Affiliated to University of Mumbai, Approved by AICTE)", styles['Normal']))
    story.append(Spacer(1, 1*inch))
    
    story.append(Paragraph("<b>NAAC CRITERION 5.1.3</b>", title_style))
    story.append(Spacer(1, 0.2*inch))
    story.append(Paragraph("Capacity Building and Skills Enhancement Initiatives", heading_style))
    story.append(Spacer(1, 0.5*inch))
    story.append(Paragraph("Academic Year 2024-25", body_style))
    story.append(Paragraph("Department of Computer Engineering", body_style))
    story.append(PageBreak())
    
    # Table of Contents
    story.append(Paragraph("<b>TABLE OF CONTENTS</b>", title_style))
    story.append(Spacer(1, 0.3*inch))
    
    toc_data = [["Sr. No.", "Event Name", "Date"]]
    for i, event in enumerate(events_data):
        toc_data.append([
            str(i + 1),
            sanitize_text(event.get('name', '')[:50], 50),
            sanitize_text(str(event.get('date', ''))[:15], 15)
        ])
    
    toc_table = Table(toc_data, colWidths=[0.6*inch, 4.5*inch, 1.2*inch])
    toc_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), VESIT_BLUE),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('TOPPADDING', (0, 0), (-1, 0), 8),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(toc_table)
    story.append(PageBreak())
    
    # Event Reports
    for i, event in enumerate(events_data):
        print(f"    [{i+1}/{len(events_data)}] Adding: {event.get('name', '')[:40]}...")
        
        report = event.get('ai_report', {})
        
        # Event Title
        title = sanitize_text(report.get('Title', event.get('name', 'Event Report')), 100)
        story.append(Paragraph(f"<b>{i+1}. {title}</b>", heading_style))
        story.append(Spacer(1, 0.1*inch))
        
        # Metadata
        if event.get('date'):
            story.append(Paragraph(f"<b>Date:</b> {sanitize_text(str(event['date']), 30)}", body_style))
        if event.get('students'):
            story.append(Paragraph(f"<b>Participants:</b> {sanitize_text(str(event['students']), 100)}", body_style))
        
        story.append(Spacer(1, 0.15*inch))
        
        # Report Sections
        sections = [
            ("Objective", report.get('Objective', '')),
            ("Planning & Organization", report.get('Planning', '')),
            ("Participation Details", report.get('Participation', '')),
            ("Evidence & Documentation", report.get('Evidence', '')),
            ("Key Examples", report.get('Examples', '')),
            ("Conclusion & Impact", report.get('Conclusion', '')),
        ]
        
        for label, content in sections:
            if content:
                story.append(Paragraph(f"<b>{label}:</b>", section_label))
                story.append(Paragraph(sanitize_text(content, 1500), body_style))
        
        # Images
        images = event.get('images', [])
        if images:
            story.append(Spacer(1, 0.2*inch))
            story.append(Paragraph("<b>Supporting Images:</b>", section_label))
            story.append(Spacer(1, 0.1*inch))
            
            for img_path in images[:3]:  # Max 3 images per event
                if os.path.exists(img_path):
                    try:
                        img = Image(img_path, width=4.5*inch, height=3*inch, hAlign="CENTER")
                        story.append(img)
                        story.append(Spacer(1, 0.1*inch))
                    except:
                        pass
        
        # Page break between events
        if i < len(events_data) - 1:
            story.append(PageBreak())
    
    # Build PDF
    doc.build(story)
    print(f"✅ PDF created: {output_path}")


# ============================================================================
# MAIN EXECUTION
# ============================================================================
def main():
    print("=" * 70)
    print("NAAC ENHANCED REPORT GENERATOR")
    print("With OpenRouter AI (FREE) + Google Drive Images")
    print("=" * 70)
    
    # Initialize services
    drive = init_google_drive()
    llm = init_llm()
    
    # Read Excel
    print(f"\n📁 Reading Excel: {EXCEL_FILE}")
    try:
        df = pd.read_excel(EXCEL_FILE, sheet_name=SHEET_NAME, header=1)
        print(f"✅ Found {len(df)} rows")
    except Exception as e:
        print(f"❌ Excel error: {e}")
        return
    
    events_data = []
    downloaded_images = []
    
    print("\n" + "=" * 70)
    print("PROCESSING EVENTS")
    print("=" * 70)
    
    for idx, row in df.iterrows():
        event_name = str(row.iloc[0]) if pd.notna(row.iloc[0]) else ""
        
        # Skip empty/header rows
        if not event_name or event_name.lower() in ['nan', 'name of the activity', 'sr. no.']:
            continue
        
        print(f"\n[{len(events_data)+1}] {event_name[:50]}...")
        
        event = {
            'name': event_name,
            'date': str(row.iloc[1]) if len(row) > 1 and pd.notna(row.iloc[1]) else '',
            'students': str(row.iloc[2]) if len(row) > 2 and pd.notna(row.iloc[2]) else '',
            'agencies': str(row.iloc[3]) if len(row) > 3 and pd.notna(row.iloc[3]) else '',
            'images': [],
            'ai_report': {}
        }
        
        # Extract images from Drive
        if drive:
            links = extract_links_from_excel_row(EXCEL_FILE, SHEET_NAME, idx)
            # Also check text content for links
            row_text = str(row)
            url_pattern = r'https?://(?:drive|docs)\.google\.com[^\s\)\"\']+' 
            text_links = re.findall(url_pattern, row_text)
            links.extend(text_links)
            
            for link in links[:2]:  # Max 2 folders per event
                drive_id, link_type = extract_drive_id(link)
                if drive_id and link_type == 'folder':
                    print(f"    📁 Downloading images from folder...")
                    images = download_images_from_folder(drive, drive_id, MAX_IMAGES_PER_EVENT)
                    event['images'].extend(images)
                    downloaded_images.extend(images)
        
        # Generate AI report
        if llm:
            print(f"    🤖 Generating AI report...")
            # Rate limit
            if len(events_data) > 0:
                time.sleep(2)
            
            ai_report = generate_ai_report(llm, row.to_string())
            if ai_report:
                event['ai_report'] = ai_report
                print(f"    ✅ AI report generated")
            else:
                print(f"    ⚠️ Using template")
        
        events_data.append(event)
    
    print(f"\n✅ Processed {len(events_data)} events")
    print(f"📷 Downloaded {len(downloaded_images)} images")
    
    # Create PDF
    print("\n" + "=" * 70)
    print("CREATING PDF REPORT")
    print("=" * 70)
    
    create_pdf_report(events_data, PDF_OUTPUT)
    
    # Cleanup temp images
    print("\n🧹 Cleaning up temp images...")
    for img in downloaded_images:
        try:
            if os.path.exists(img):
                os.remove(img)
        except:
            pass
    
    print("\n" + "=" * 70)
    print("✅ COMPLETE!")
    print(f"📄 Report: {os.path.abspath(PDF_OUTPUT)}")
    print("=" * 70)


if __name__ == "__main__":
    main()
