"""
NAAC PDF MERGER - Downloads and Merges ALL Source PDFs
Creates one big PDF like your college's format (252+ pages)

Flow:
1. Create INDEX page (VES header + table of contents)
2. For each event in Excel:
   - Download all PDFs from the Drive links
   - Merge them into the final PDF
3. Output: One complete merged PDF with INDEX + all source docs
"""

import os
import sys
import re
import io
import pandas as pd
from typing import List, Dict, Tuple, Optional
from dotenv import load_dotenv

load_dotenv()

try:
    from reportlab.lib.pagesizes import A4
    from reportlab.platypus import SimpleDocTemplate, Spacer, PageBreak, Paragraph, Table, TableStyle
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER
    from pypdf import PdfReader, PdfWriter
    from openpyxl import load_workbook
    from pydrive2.auth import GoogleAuth
    from pydrive2.drive import GoogleDrive
except ImportError as e:
    print(f"Missing: {e}")
    print("Run: pip install reportlab pypdf pydrive2 openpyxl pandas python-dotenv")
    sys.exit(1)


# ============================================================================
# CONFIG
# ============================================================================
EXCEL_FILE = "data/Criteria 5.1.3 CMPN Data 2024-25.xlsx"
SHEET_NAME = "5.1.3"
OUTPUT_PDF = "NAAC_5.1.3_MERGED_FULL.pdf"
TEMP_DIR = "temp_pdfs"

VES_RED = colors.HexColor('#8B0000')


def sanitize(text: str, max_len: int = 500) -> str:
    if not text or str(text) == 'nan':
        return ""
    text = str(text)[:max_len]
    for old, new in {'–': '-', '—': '-', ''': "'", ''': "'", '"': '"', '"': '"'}.items():
        text = text.replace(old, new)
    return ''.join(c if ord(c) < 256 else '' for c in text)


# ============================================================================
# GOOGLE DRIVE
# ============================================================================
def init_drive():
    try:
        gauth = GoogleAuth()
        gauth.LocalWebserverAuth()
        return GoogleDrive(gauth)
    except Exception as e:
        print(f"⚠️ Drive auth failed: {e}")
        return None


def get_drive_id(url: str) -> Tuple[Optional[str], Optional[str]]:
    if not url:
        return None, None
    
    # Folder
    m = re.search(r'/folders/([a-zA-Z0-9_-]+)', url)
    if m:
        return m.group(1), 'folder'
    
    # File
    m = re.search(r'/file/d/([a-zA-Z0-9_-]+)', url)
    if m:
        return m.group(1), 'file'
    
    # Doc/Sheet/etc
    m = re.search(r'/d/([a-zA-Z0-9_-]+)', url)
    if m:
        return m.group(1), 'file'
    
    return None, None


def get_excel_hyperlinks(path: str, sheet: str, row_idx: int) -> List[str]:
    """Get hyperlinks from Excel row."""
    links = []
    try:
        wb = load_workbook(path, data_only=False)
        if sheet in wb.sheetnames:
            ws = wb[sheet]
            for cell in ws[row_idx + 3]:
                if cell.hyperlink and cell.hyperlink.target:
                    links.append(cell.hyperlink.target)
    except:
        pass
    return links


def download_pdfs_from_folder(drive, folder_id: str, temp_dir: str, prefix: str = "") -> List[str]:
    """Download all PDFs from a Drive folder."""
    pdfs = []
    if not drive:
        return pdfs
    
    try:
        # Get PDFs
        files = drive.ListFile({
            'q': f"'{folder_id}' in parents and trashed=false and mimeType='application/pdf'"
        }).GetList()
        
        for f in files:
            try:
                fname = os.path.join(temp_dir, f"{prefix}_{f['title']}")
                fname = fname.replace(" ", "_")[:150] + ".pdf"
                f.GetContentFile(fname)
                pdfs.append(fname)
                print(f"        ✓ PDF: {f['title'][:40]}")
            except Exception as e:
                print(f"        ✗ {f['title'][:30]}: {e}")
        
        # Check subfolders
        subfolders = drive.ListFile({
            'q': f"'{folder_id}' in parents and trashed=false and mimeType='application/vnd.google-apps.folder'"
        }).GetList()
        
        for sf in subfolders[:3]:  # Max 3 subfolders
            sub_pdfs = download_pdfs_from_folder(drive, sf['id'], temp_dir, f"{prefix}_{sf['title'][:20]}")
            pdfs.extend(sub_pdfs)
        
        # Also get Google Docs as PDFs
        docs = drive.ListFile({
            'q': f"'{folder_id}' in parents and trashed=false and mimeType='application/vnd.google-apps.document'"
        }).GetList()
        
        for doc in docs[:5]:
            try:
                fname = os.path.join(temp_dir, f"{prefix}_{doc['title']}.pdf")
                fname = fname.replace(" ", "_")[:150]
                doc.GetContentFile(fname, mimetype='application/pdf')
                pdfs.append(fname)
                print(f"        ✓ Doc→PDF: {doc['title'][:35]}")
            except:
                pass
                
    except Exception as e:
        print(f"        ⚠️ Folder error: {e}")
    
    return pdfs


def download_file_as_pdf(drive, file_id: str, temp_dir: str, name: str) -> Optional[str]:
    """Download a Drive file as PDF."""
    if not drive:
        return None
    
    try:
        f = drive.CreateFile({'id': file_id})
        f.FetchMetadata()
        
        mime = f.get('mimeType', '')
        fname = os.path.join(temp_dir, f"{name}".replace(" ", "_")[:100] + ".pdf")
        
        if 'pdf' in mime:
            f.GetContentFile(fname)
        elif 'document' in mime:
            f.GetContentFile(fname, mimetype='application/pdf')
        else:
            return None
        
        print(f"        ✓ File: {name[:40]}")
        return fname
    except:
        return None


# ============================================================================
# PDF GENERATION
# ============================================================================
def create_index_pdf(events: List[Dict], output_path: str) -> str:
    """Create the INDEX cover page as a PDF."""
    from reportlab.platypus import SimpleDocTemplate
    
    doc = SimpleDocTemplate(output_path, pagesize=A4,
                           leftMargin=0.75*inch, rightMargin=0.75*inch,
                           topMargin=0.75*inch, bottomMargin=0.75*inch)
    
    styles = getSampleStyleSheet()
    story = []
    
    # Header
    header_style = ParagraphStyle(
        'Header', parent=styles['Heading1'],
        fontSize=22, textColor=VES_RED, alignment=TA_CENTER,
        fontName='Times-Bold', spaceAfter=4
    )
    
    story.append(Paragraph("<b>Vivekanand Education Society's</b>", header_style))
    story.append(Paragraph("<u>Institute of Technology</u>", ParagraphStyle(
        'Sub', parent=styles['Normal'], fontSize=16, alignment=TA_CENTER,
        fontName='Times-Roman'
    )))
    story.append(Paragraph(
        "(Affiliated to University of Mumbai, Approved by AICTE & Recognized by Govt. of Maharashtra)",
        ParagraphStyle('Aff', parent=styles['Normal'], fontSize=9, alignment=TA_CENTER)
    ))
    
    story.append(Spacer(1, 0.4*inch))
    
    # Criterion
    story.append(Paragraph("<u><b>5.1.3</b></u>", ParagraphStyle(
        'Crit', parent=styles['Normal'], fontSize=14, alignment=TA_CENTER, fontName='Times-Bold'
    )))
    story.append(Paragraph("<b>Capacity Building and Skill Enhancement</b>", ParagraphStyle(
        'CritTitle', parent=styles['Normal'], fontSize=13, alignment=TA_CENTER, fontName='Times-Bold'
    )))
    
    story.append(Spacer(1, 0.3*inch))
    story.append(Paragraph("<u><b>INDEX</b></u>", ParagraphStyle(
        'Index', parent=styles['Normal'], fontSize=14, alignment=TA_CENTER, fontName='Times-Bold'
    )))
    story.append(Spacer(1, 0.2*inch))
    
    # Index table
    table_data = [['Sr. No.', 'Contents', 'Page No.']]
    page_num = 2  # Start after index page
    
    for i, event in enumerate(events):
        name = sanitize(event.get('name', ''), 55)
        num_pdfs = event.get('num_pdfs', 0)
        
        table_data.append([str(i + 1), name, str(page_num)])
        page_num += max(1, num_pdfs * 2)  # Estimate pages
    
    table = Table(table_data, colWidths=[0.6*inch, 4.8*inch, 0.7*inch])
    table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, 0), 'Times-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('FONTNAME', (0, 1), (-1, -1), 'Times-Roman'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('ALIGN', (0, 0), (0, -1), 'CENTER'),
        ('ALIGN', (2, 0), (2, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    
    story.append(table)
    
    doc.build(story)
    return output_path


def merge_pdfs(index_pdf: str, event_pdfs: List[List[str]], output_path: str):
    """Merge INDEX + all event PDFs into one."""
    writer = PdfWriter()
    
    # Add index
    print("    Adding INDEX page...")
    reader = PdfReader(index_pdf)
    for page in reader.pages:
        writer.add_page(page)
    
    # Add each event's PDFs
    total_pdfs = sum(len(pdfs) for pdfs in event_pdfs)
    added = 0
    
    for i, pdfs in enumerate(event_pdfs):
        for pdf_path in pdfs:
            if os.path.exists(pdf_path):
                try:
                    reader = PdfReader(pdf_path)
                    for page in reader.pages:
                        writer.add_page(page)
                    added += 1
                    print(f"    [{added}/{total_pdfs}] Merged: {os.path.basename(pdf_path)[:40]}")
                except Exception as e:
                    print(f"    ✗ Failed: {os.path.basename(pdf_path)[:30]} - {e}")
    
    # Save
    with open(output_path, 'wb') as f:
        writer.write(f)
    
    print(f"\n✅ Merged {added} PDFs → {output_path}")
    return added


# ============================================================================
# MAIN
# ============================================================================
def main():
    print("=" * 65)
    print("NAAC PDF MERGER - Full Document Compilation")
    print("Downloads all PDFs from Drive and merges into one report")
    print("=" * 65)
    
    # Create temp dir
    os.makedirs(TEMP_DIR, exist_ok=True)
    
    # Init Drive
    print("\n🔐 Authenticating Google Drive...")
    drive = init_drive()
    if drive:
        print("✅ Drive connected!")
    else:
        print("❌ Drive required for PDF download!")
        return
    
    # Read Excel
    print(f"\n📁 Reading: {EXCEL_FILE}")
    try:
        df = pd.read_excel(EXCEL_FILE, sheet_name=SHEET_NAME, header=1)
        print(f"✅ Found {len(df)} rows")
    except Exception as e:
        print(f"❌ Error: {e}")
        return
    
    # Process events
    events = []
    all_event_pdfs = []
    
    print("\n" + "=" * 65)
    print("DOWNLOADING PDFs FROM DRIVE")
    print("=" * 65)
    
    for idx, row in df.iterrows():
        name = str(row.iloc[0]) if pd.notna(row.iloc[0]) else ""
        if not name or name.lower() in ['nan', 'name of the activity']:
            continue
        
        event_num = len(events) + 1
        print(f"\n[{event_num}] {name[:50]}...")
        
        event = {'name': name, 'num_pdfs': 0}
        event_pdfs = []
        
        # Get hyperlinks from Excel
        links = get_excel_hyperlinks(EXCEL_FILE, SHEET_NAME, idx)
        
        # Also check text for links
        row_text = str(row)
        url_pattern = r'https?://(?:drive|docs)\.google\.com[^\s\)\"\'<>]+'
        text_links = re.findall(url_pattern, row_text)
        links.extend(text_links)
        
        # Download PDFs from each link
        for link in list(set(links))[:5]:  # Max 5 links per event
            drive_id, link_type = get_drive_id(link)
            
            if drive_id:
                if link_type == 'folder':
                    print(f"    📁 Folder: {drive_id[:15]}...")
                    pdfs = download_pdfs_from_folder(drive, drive_id, TEMP_DIR, f"e{event_num}")
                    event_pdfs.extend(pdfs)
                else:
                    pdf = download_file_as_pdf(drive, drive_id, TEMP_DIR, f"e{event_num}_{name[:20]}")
                    if pdf:
                        event_pdfs.append(pdf)
        
        event['num_pdfs'] = len(event_pdfs)
        events.append(event)
        all_event_pdfs.append(event_pdfs)
        
        if event_pdfs:
            print(f"    → {len(event_pdfs)} PDF(s) downloaded")
    
    print(f"\n✅ Processed {len(events)} events")
    total_pdfs = sum(len(p) for p in all_event_pdfs)
    print(f"📄 Total PDFs downloaded: {total_pdfs}")
    
    if total_pdfs == 0:
        print("⚠️ No PDFs found! Check Drive permissions or links.")
        return
    
    # Create INDEX page
    print("\n" + "=" * 65)
    print("CREATING MERGED PDF")
    print("=" * 65)
    
    index_path = os.path.join(TEMP_DIR, "index.pdf")
    print("\n📝 Creating INDEX page...")
    create_index_pdf(events, index_path)
    
    # Merge all
    print("\n📎 Merging all PDFs...")
    merged = merge_pdfs(index_path, all_event_pdfs, OUTPUT_PDF)
    
    # Cleanup
    print("\n🧹 Cleaning up temp files...")
    import shutil
    try:
        shutil.rmtree(TEMP_DIR)
    except:
        pass
    
    # Final stats
    if os.path.exists(OUTPUT_PDF):
        reader = PdfReader(OUTPUT_PDF)
        print("\n" + "=" * 65)
        print("✅ COMPLETE!")
        print(f"📄 Output: {os.path.abspath(OUTPUT_PDF)}")
        print(f"📊 Total pages: {len(reader.pages)}")
        print(f"📑 Events: {len(events)}")
        print(f"📎 PDFs merged: {merged}")
        print("=" * 65)


if __name__ == "__main__":
    main()
