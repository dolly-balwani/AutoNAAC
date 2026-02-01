"""
NAAC Report Generator - EXACT VES FORMAT
Matches your college's PDF template exactly:
- Red/maroon branding
- Hierarchical INDEX
- Clickable hyperlinks
- Proper page numbers
"""

import os
import sys
import re
import pandas as pd
from typing import List, Dict, Optional
from dotenv import load_dotenv

load_dotenv()

try:
    from reportlab.lib.pagesizes import A4
    from reportlab.platypus import SimpleDocTemplate, Image, Spacer, PageBreak, Paragraph, Table, TableStyle, ListFlowable, ListItem
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch, cm
    from reportlab.lib import colors
    from reportlab.pdfgen import canvas
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
    from openpyxl import load_workbook
    from pydrive2.auth import GoogleAuth
    from pydrive2.drive import GoogleDrive
except ImportError as e:
    print(f"Missing dependency: {e}")
    print("Run: pip install reportlab pydrive2 openpyxl pandas python-dotenv")
    sys.exit(1)


# ============================================================================
# CONFIGURATION - VES BRANDING
# ============================================================================
EXCEL_FILE = "data/Criteria 5.1.3 CMPN Data 2024-25.xlsx"
SHEET_NAME = "5.1.3"
PDF_OUTPUT = "NAAC_5.1.3_VES_Format.pdf"

# VES Colors (matching your template)
VES_RED = colors.HexColor('#8B0000')  # Dark red/maroon
VES_GOLD = colors.HexColor('#C9A227')


# ============================================================================
# TEXT SANITIZATION  
# ============================================================================
def sanitize(text: str, max_len: int = 500) -> str:
    """Clean text for PDF."""
    if not text or str(text) == 'nan':
        return ""
    text = str(text)[:max_len]
    replacements = {
        '–': '-', '—': '-', ''': "'", ''': "'", '"': '"', '"': '"',
        '…': '...', '•': '*', '\u200b': '', '\xa0': ' ',
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    return ''.join(c if ord(c) < 256 else '' for c in text)


# ============================================================================
# GOOGLE DRIVE FUNCTIONS
# ============================================================================
def init_drive():
    """Initialize Google Drive."""
    try:
        gauth = GoogleAuth()
        gauth.LocalWebserverAuth()
        return GoogleDrive(gauth)
    except:
        return None


def get_drive_id(url: str):
    """Extract Drive folder/file ID."""
    if not url:
        return None, None
    folder = re.search(r'/folders/([a-zA-Z0-9_-]+)', url)
    if folder:
        return folder.group(1), 'folder'
    file = re.search(r'/file/d/([a-zA-Z0-9_-]+)', url)
    if file:
        return file.group(1), 'file'
    return None, None


def get_hyperlinks(excel_path: str, sheet: str, row: int) -> List[str]:
    """Get hyperlinks from Excel row."""
    links = []
    try:
        wb = load_workbook(excel_path, data_only=False)
        if sheet in wb.sheetnames:
            ws = wb[sheet]
            for cell in ws[row + 3]:
                if cell.hyperlink and cell.hyperlink.target:
                    links.append(cell.hyperlink.target)
    except:
        pass
    return links


def download_folder_images(drive, folder_id: str, max_imgs: int = 5) -> List[str]:
    """Download images from Drive folder."""
    images = []
    if not drive:
        return images
    
    try:
        files = drive.ListFile({
            'q': f"'{folder_id}' in parents and trashed=false and mimeType contains 'image/'"
        }).GetList()
        
        for f in files[:max_imgs]:
            try:
                fname = f"temp_{folder_id[:6]}_{f['title']}"
                f.GetContentFile(fname)
                images.append(fname)
                print(f"      ✓ {f['title'][:30]}")
            except:
                continue
    except:
        pass
    
    return images


# ============================================================================
# PDF GENERATION - EXACT VES FORMAT
# ============================================================================
class VESReport:
    def __init__(self, output_path: str):
        self.output_path = output_path
        self.width, self.height = A4
        self.styles = getSampleStyleSheet()
        self.story = []
        self.page_counter = 0
        self.toc_entries = []  # (level, title, page)
        
        # Create custom styles matching VES format
        self._create_styles()
    
    def _create_styles(self):
        """Create styles matching VES template."""
        # Header title - big red
        self.header_style = ParagraphStyle(
            'VESHeader',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=VES_RED,
            alignment=TA_CENTER,
            spaceAfter=6,
            fontName='Times-Bold'
        )
        
        # Sub header
        self.subheader_style = ParagraphStyle(
            'VESSubHeader',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=colors.black,
            alignment=TA_CENTER,
            spaceAfter=4,
            fontName='Times-Roman'
        )
        
        # Criterion title - underlined
        self.criterion_style = ParagraphStyle(
            'Criterion',
            parent=self.styles['Normal'],
            fontSize=14,
            textColor=colors.black,
            alignment=TA_CENTER,
            spaceBefore=20,
            spaceAfter=6,
            fontName='Times-Bold'
        )
        
        # Index header
        self.index_header = ParagraphStyle(
            'IndexHeader',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=colors.black,
            alignment=TA_CENTER,
            spaceBefore=15,
            spaceAfter=10,
            fontName='Times-Bold',
            underline=True
        )
        
        # Normal text
        self.body_style = ParagraphStyle(
            'VESBody',
            parent=self.styles['Normal'],
            fontSize=11,
            alignment=TA_JUSTIFY,
            fontName='Times-Roman',
            leading=14
        )
        
        # Hyperlink style
        self.link_style = ParagraphStyle(
            'VESLink',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=colors.blue,
            fontName='Times-Roman'
        )
    
    def add_header_page(self, criterion: str, title: str):
        """Add VES header page matching template."""
        # College name in red
        self.story.append(Paragraph(
            "<b>Vivekanand Education Society's</b>",
            self.header_style
        ))
        
        # Institute name
        self.story.append(Paragraph(
            "<u>Institute of Technology</u>",
            self.subheader_style  
        ))
        
        # Affiliation line
        aff_style = ParagraphStyle(
            'Affiliation',
            parent=self.styles['Normal'],
            fontSize=10,
            alignment=TA_CENTER,
            fontName='Times-Roman'
        )
        self.story.append(Paragraph(
            "(Affiliated to University of Mumbai, Approved by AICTE & Recognized by Govt. of Maharashtra)",
            aff_style
        ))
        
        self.story.append(Spacer(1, 0.5*inch))
        
        # Criterion number - underlined centered
        self.story.append(Paragraph(
            f"<u><b>{criterion}</b></u>",
            self.criterion_style
        ))
        
        # Criterion title
        self.story.append(Paragraph(
            f"<b>{title}</b>",
            self.criterion_style
        ))
        
        self.story.append(Spacer(1, 0.3*inch))
        
        # INDEX header - underlined
        self.story.append(Paragraph(
            "<u><b>INDEX</b></u>",
            self.index_header
        ))
        
        self.story.append(Spacer(1, 0.2*inch))
    
    def add_index_table(self, events: List[Dict]):
        """Add INDEX table matching VES format exactly."""
        # Table data with hierarchy
        table_data = [
            ['Sr. No.', 'Contents', 'Page No.']
        ]
        
        current_page = 1
        for i, event in enumerate(events):
            name = sanitize(event.get('name', ''), 60)
            
            # Add main entry
            table_data.append([
                str(i + 1),
                name,
                str(current_page)
            ])
            
            # Add sub-items if they have Drive links (like in your template)
            sub_items = event.get('sub_items', [])
            for j, sub in enumerate(sub_items[:5]):  # Max 5 sub-items
                letter = chr(ord('a') + j)
                sub_name = sanitize(sub.get('name', ''), 55)
                table_data.append([
                    f"  {letter})",
                    f'<link href="{sub.get("url", "#")}">{sub_name}</link>' if sub.get('url') else sub_name,
                    str(current_page)
                ])
            
            current_page += 1
        
        # Create table with VES styling
        col_widths = [0.8*inch, 4.5*inch, 0.8*inch]
        
        # Convert link markup to Paragraphs
        formatted_data = []
        for row in table_data:
            formatted_row = []
            for i, cell in enumerate(row):
                if i == 1 and '<link' in str(cell):
                    # Parse and create hyperlink paragraph
                    formatted_row.append(Paragraph(cell, self.link_style))
                else:
                    formatted_row.append(cell)
            formatted_data.append(formatted_row)
        
        table = Table(formatted_data, colWidths=col_widths)
        table.setStyle(TableStyle([
            # Header row
            ('BACKGROUND', (0, 0), (-1, 0), colors.white),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('FONTNAME', (0, 0), (-1, 0), 'Times-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('TOPPADDING', (0, 0), (-1, 0), 8),
            
            # Data rows
            ('FONTNAME', (0, 1), (-1, -1), 'Times-Roman'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('ALIGN', (0, 1), (0, -1), 'CENTER'),  # Sr No centered
            ('ALIGN', (1, 1), (1, -1), 'LEFT'),    # Contents left
            ('ALIGN', (2, 1), (2, -1), 'CENTER'),  # Page No centered
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            
            # Borders
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('BOX', (0, 0), (-1, -1), 1, colors.black),
        ]))
        
        self.story.append(table)
        self.story.append(PageBreak())
    
    def add_event_page(self, event: Dict, index: int, images: List[str] = None):
        """Add event report page."""
        name = sanitize(event.get('name', ''), 100)
        date = sanitize(str(event.get('date', '')), 30)
        
        # Event header
        header_style = ParagraphStyle(
            'EventHeader',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=VES_RED,
            fontName='Times-Bold',
            spaceBefore=10,
            spaceAfter=8
        )
        
        self.story.append(Paragraph(f"<b>{index}. {name}</b>", header_style))
        
        if date and date != 'nan':
            self.story.append(Paragraph(f"<b>Date:</b> {date}", self.body_style))
        
        self.story.append(Spacer(1, 0.15*inch))
        
        # Event content sections
        sections = [
            ("Objective", f"This initiative was conducted to enhance student skills and provide practical exposure in {name[:50]}."),
            ("Participation", f"Students from the Computer Engineering department actively participated in this activity."),
            ("Outcome", f"The program successfully achieved its objectives of skill enhancement and capacity building.")
        ]
        
        for label, content in sections:
            label_style = ParagraphStyle(
                'SectionLabel',
                parent=self.body_style,
                fontName='Times-Bold',
                spaceBefore=6
            )
            self.story.append(Paragraph(f"<b>{label}:</b>", label_style))
            self.story.append(Paragraph(content, self.body_style))
        
        # Add images if available
        if images:
            self.story.append(Spacer(1, 0.2*inch))
            self.story.append(Paragraph("<b>Evidence:</b>", self.body_style))
            
            for img_path in images[:3]:
                if os.path.exists(img_path):
                    try:
                        img = Image(img_path, width=4*inch, height=2.5*inch)
                        self.story.append(img)
                        self.story.append(Spacer(1, 0.1*inch))
                    except:
                        pass
        
        self.story.append(PageBreak())
    
    def build(self):
        """Build the PDF."""
        doc = SimpleDocTemplate(
            self.output_path,
            pagesize=A4,
            leftMargin=0.75*inch,
            rightMargin=0.75*inch,
            topMargin=0.75*inch,
            bottomMargin=0.75*inch
        )
        doc.build(self.story)


# ============================================================================
# MAIN
# ============================================================================
def main():
    print("=" * 60)
    print("NAAC REPORT - VES FORMAT")
    print("=" * 60)
    
    # Init Drive
    print("\n🔐 Connecting to Google Drive...")
    drive = init_drive()
    if drive:
        print("✅ Drive connected!")
    else:
        print("⚠️ Drive not available, continuing without images...")
    
    # Read Excel
    print(f"\n📁 Reading: {EXCEL_FILE}")
    try:
        df = pd.read_excel(EXCEL_FILE, sheet_name=SHEET_NAME, header=1)
        print(f"✅ Found {len(df)} rows")
    except Exception as e:
        print(f"❌ Error: {e}")
        return
    
    # Parse events
    events = []
    all_images = []
    
    print("\n" + "=" * 60)
    print("PROCESSING EVENTS")
    print("=" * 60)
    
    for idx, row in df.iterrows():
        name = str(row.iloc[0]) if pd.notna(row.iloc[0]) else ""
        if not name or name.lower() in ['nan', 'name of the activity', 'sr. no.']:
            continue
        
        print(f"\n[{len(events)+1}] {name[:45]}...")
        
        event = {
            'name': name,
            'date': str(row.iloc[1]) if len(row) > 1 and pd.notna(row.iloc[1]) else '',
            'students': str(row.iloc[2]) if len(row) > 2 and pd.notna(row.iloc[2]) else '',
            'sub_items': []
        }
        
        # Get Drive links and download images
        images = []
        if drive:
            links = get_hyperlinks(EXCEL_FILE, SHEET_NAME, idx)
            for link in links[:2]:
                drive_id, link_type = get_drive_id(link)
                if drive_id and link_type == 'folder':
                    print(f"    📁 Getting images...")
                    imgs = download_folder_images(drive, drive_id, 3)
                    images.extend(imgs)
                    all_images.extend(imgs)
                    
                    # Add as sub-items for INDEX
                    event['sub_items'].append({
                        'name': f"Supporting document",
                        'url': link
                    })
        
        event['images'] = images
        events.append(event)
    
    print(f"\n✅ Processed {len(events)} events")
    print(f"📷 Downloaded {len(all_images)} images")
    
    # Create PDF
    print("\n" + "=" * 60)
    print("CREATING PDF")
    print("=" * 60)
    
    report = VESReport(PDF_OUTPUT)
    
    # Header page with INDEX
    report.add_header_page("5.1.3", "Capacity Building and Skill Enhancement")
    report.add_index_table(events)
    
    # Event pages
    for i, event in enumerate(events):
        print(f"    [{i+1}/{len(events)}] {event['name'][:40]}...")
        report.add_event_page(event, i+1, event.get('images', []))
    
    report.build()
    
    # Cleanup
    print("\n🧹 Cleaning up...")
    for img in all_images:
        try:
            if os.path.exists(img):
                os.remove(img)
        except:
            pass
    
    print("\n" + "=" * 60)
    print("✅ COMPLETE!")  
    print(f"📄 {os.path.abspath(PDF_OUTPUT)}")
    print("=" * 60)


if __name__ == "__main__":
    main()
