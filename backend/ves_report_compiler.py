"""
NAAC VES Report Compiler for FastAPI Backend
Uses the same VESPDF engine from naac_groq_report.py with Groq AI + VES branding.
"""

import os
import sys
import time
import re
import io
import json
import pandas as pd
from typing import List, Dict, Optional, Tuple
from dotenv import load_dotenv

# Load .env from current directory
load_dotenv()
PARENT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

try:
    from reportlab.lib.pagesizes import A4
    from reportlab.platypus import SimpleDocTemplate, Image, Spacer, PageBreak, Paragraph, Table, TableStyle
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
    from pydrive2.auth import GoogleAuth
    from pydrive2.drive import GoogleDrive
    from langchain_groq import ChatGroq
    from langchain_core.prompts import PromptTemplate
    from langchain_core.output_parsers import JsonOutputParser
    from pydantic import BaseModel, Field
    from openpyxl import load_workbook
    from pypdf import PdfReader, PdfWriter
except ImportError as e:
    print(f"Missing dependency: {e}")
    sys.exit(1)

VES_RED = colors.HexColor('#8B0000')

class ReportSections(BaseModel):
    Title: str = Field(description="Professional event title")
    Objective: str = Field(description="Aims and intended outcomes")
    Planning: str = Field(description="Organization details")
    Participation: str = Field(description="Participant details")
    Evidence: str = Field(description="Proof of conduct")
    Outcome: str = Field(description="Summary of achievements")

def clean(text: str) -> str:
    if not text or str(text) == 'nan': return ""
    return ''.join(c if ord(c) < 256 else '' for c in str(text))

def get_drive():
    try:
        gauth = GoogleAuth()
        creds_file = "mycreds.txt"  # Now in backend folder
        gauth.LoadCredentialsFile(creds_file)
        if gauth.credentials is None:
            gauth.LocalWebserverAuth()
        elif gauth.access_token_expired:
            try:
                gauth.Refresh()
            except:
                gauth.LocalWebserverAuth()
        else:
            gauth.Authorize()
        gauth.SaveCredentialsFile(creds_file)
        return GoogleDrive(gauth)
    except Exception as e:
        print(f"Drive Auth Error: {e}")
        return None

def download_drive_content(drive, urls, folder_prefix):
    images = []
    pdf_path = None
    if not drive or not urls: return images, None, False
    
    for link_idx, url in enumerate(urls):
        if not url or not isinstance(url, str): continue
        m = re.search(r'([a-zA-Z0-9_-]{25,})', url)
        if not m: continue
        fid = m.group(1)
        
        try:
            f_meta = drive.CreateFile({'id': fid})
            f_meta.FetchMetadata()
            
            if f_meta['mimeType'] == 'application/pdf':
                if not pdf_path:
                    pdf_path = f"{folder_prefix}_doc_{link_idx}.pdf"
                    f_meta.GetContentFile(pdf_path)
                continue

            query = f"'{fid}' in parents and trashed=false"
            children = drive.ListFile({'q': query}).GetList()
            
            for child in children:
                mtype = child['mimeType']
                if 'image/' in mtype and len(images) < 4:
                    fname = f"{folder_prefix}_img_{link_idx}_{len(images)}.jpg"
                    child.GetContentFile(fname)
                    images.append(fname)
                elif mtype == 'application/pdf' and not pdf_path:
                    pdf_path = f"{folder_prefix}_doc_{link_idx}.pdf"
                    child.GetContentFile(pdf_path)
                    
        except Exception as e:
            print(f"Drive Link Error: {e}")
            
    is_pdf = pdf_path is not None
    return images, pdf_path, is_pdf

def generate_narrative(row_data: str):
    try:
        llm = ChatGroq(temperature=0.3, model_name="llama-3.1-8b-instant", groq_api_key=os.getenv("GROQ_API_KEY"))
        parser = JsonOutputParser(pydantic_object=ReportSections)
        prompt = PromptTemplate(
            template="""You are an expert academic writer documenting NAAC Accreditation reports for a premium engineering institute. 
Based on the provided event data, write a HIGHLY DETAILED, COMPREHENSIVE, and PROFESSIONAL report. 
Each section MUST be thorough with multiple sentences (at least 5-8 sentences per section). 
Use formal academic language and avoid placeholders like 'NaN' or 'N/A'. If a value is missing, infer it professionally from the context or describe the typical process.

Event Data:
{data}

Provide detailed responses for:
1. **Title**: A professional, descriptive title.
2. **Objective**: Detailed aims, intended learning outcomes, and alignment with institutional goals.
3. **Planning**: Thorough description of the organization, timeline, resource allocation, and committee involvement.
4. **Participation**: Comprehensive details on student engagement, demographics, and active involvement levels.
5. **Evidence**: Detailed list of documentation maintained (certificates, geo-tagged photos, feedback analysis).
6. **Outcome**: Extensive summary of achievements, impact on student employability/skills, and future recommendations.

{format_instructions}""",
            input_variables=["data"],
            partial_variables={"format_instructions": parser.get_format_instructions()},
        )
        chain = prompt | llm | parser
        return chain.invoke({"data": row_data})
    except Exception as e:
        print(f"AI Exception: {e}")
        return None


class VESPDF:
    def __init__(self, filename):
        self.doc = SimpleDocTemplate(filename, pagesize=A4, 
                                   leftMargin=0.75*inch, rightMargin=0.75*inch, 
                                   topMargin=2.8*inch, bottomMargin=0.75*inch)
        self.styles = getSampleStyleSheet()
        self.story = []
        self._setup_styles()

    def _setup_styles(self):
        self.s_header = ParagraphStyle(
            'H', fontSize=22, textColor=VES_RED, alignment=1, fontName='Times-Bold', leading=26
        )
        self.s_event_title = ParagraphStyle(
            'ET', fontSize=18, textColor=VES_RED, fontName='Times-Bold', spaceBefore=12, spaceAfter=12, leading=22
        )
        self.s_sub = ParagraphStyle('S', fontSize=18, alignment=1, fontName='Times-Roman', underline=True, leading=22)
        self.s_aff = ParagraphStyle('A', fontSize=9, alignment=1, leading=11)
        self.s_body = ParagraphStyle('B', fontSize=11, leading=14, alignment=4, fontName='Times-Roman', spaceAfter=8)
        self.s_label = ParagraphStyle('L', parent=self.s_body, fontName='Times-Bold', spaceBefore=10, textColor=VES_RED)
        self.s_caption = ParagraphStyle('Cap', fontSize=9, alignment=1, fontName='Times-Italic', spaceBefore=4, spaceAfter=8)
        self.s_idx_item = ParagraphStyle('IdxItem', fontSize=10, leading=12, alignment=0, fontName='Times-Roman')

    def footer(self, canvas, doc):
        canvas.saveState()
        canvas.setFont('Times-Roman', 9)
        canvas.drawRightString(A4[0] - 0.75*inch, 0.5*inch, f"Page {doc.page}")
        canvas.restoreState()

    def header(self, canvas, doc):
        canvas.saveState()
        logo_path = "ves_logo.png"  # Now in backend folder
        if os.path.exists(logo_path):
            canvas.drawImage(logo_path, 0.885*inch, A4[1] - 2.6*inch, width=6.5*inch, preserveAspectRatio=True, mask='auto')
        canvas.restoreState()

    def add_cover(self, criterion, events, event_pages=None):
        self.story.append(Spacer(1, 1.3*inch))
        self.story.append(Paragraph(f"<u><b>{criterion}</b></u>", ParagraphStyle('C', fontSize=14, alignment=1, fontName='Times-Bold', leading=18)))
        self.story.append(Paragraph("<b>Capacity Building and Skill Enhancement</b>", ParagraphStyle('CT', fontSize=13, alignment=1, fontName='Times-Bold', leading=16)))
        self.story.append(Spacer(1, 0.3*inch))
        self.story.append(Paragraph("<u><b>INDEX</b></u>", ParagraphStyle('I', fontSize=14, alignment=1, fontName='Times-Bold', leading=18)))
        self.story.append(Spacer(1, 0.2*inch))
        
        data = [['Sr. No.', 'Contents', 'Page No.']]
        for i, ev in enumerate(events):
            pg = event_pages.get(i, "?") if event_pages else "?"
            contents_p = Paragraph(clean(ev['name']), self.s_idx_item)
            data.append([str(i+1), contents_p, str(pg)])
        
        t = Table(data, colWidths=[0.6*inch, 4.8*inch, 0.7*inch])
        t.setStyle(TableStyle([
            ('GRID', (0,0), (-1,-1), 0.5, colors.black),
            ('FONTNAME', (0,0), (-1,0), 'Times-Bold'),
            ('ALIGN', (0,0), (0,-1), 'CENTER'),
            ('ALIGN', (2,0), (2,-1), 'CENTER'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('LEFTPADDING', (1,1), (1,-1), 5),
            ('RIGHTPADDING', (1,1), (1,-1), 5),
        ]))
        self.story.append(t)
        self.story.append(PageBreak())

    def add_event(self, idx, report, images, is_pdf=False):
        title = clean(report.get('Title', 'Activity Report'))
        self.story.append(Paragraph(f"<b>{idx}. {title}</b>", self.s_event_title))
        
        for k in ['Objective', 'Planning', 'Participation', 'Evidence', 'Outcome']:
            content = report.get(k, '')
            if content:
                self.story.append(Paragraph(f"<b>{k}:</b>", self.s_label))
                self.story.append(Paragraph(clean(content), self.s_body))
        
        if images:
            self.story.append(Spacer(1, 0.2*inch))
            for i, img in enumerate(images):
                try: 
                    self.story.append(Image(img, width=5.0*inch, height=3.5*inch))
                    self.story.append(Paragraph(f"<i>Activity Figure {idx}.{i+1}: {title}</i>", self.s_caption))
                    self.story.append(Spacer(1, 0.15*inch))
                except: pass
        
        if is_pdf:
            self.story.append(Spacer(1, 0.2*inch))
            self.story.append(Paragraph("<b>Note: Additional detailed documentation is attached in the following pages.</b>", self.s_body))
        
        self.story.append(PageBreak())

    def build_doc(self):
        self.doc.build(self.story, onFirstPage=self.header, onLaterPages=self.header)


def compile_ves_report(excel_path: str, criterion: str, output_path: str) -> Dict:
    """
    Compiles a VES-branded report using Groq AI and the refined 3-pass system.
    Works for ANY NAAC criterion as long as the Excel follows the standard format.
    """
    print(f"🚀 Running VES Report Compiler for {criterion}...")
    
    result = {
        "success": False,
        "output_path": None,
        "events_processed": 0,
        "images_added": 0,
        "pages": 0,
        "error": None
    }
    
    try:
        drive = get_drive()
        df = pd.read_excel(excel_path, sheet_name=criterion, header=1)
    except Exception as e:
        result["error"] = f"Failed to read Excel or sheet '{criterion}': {e}"
        return result
        
    events = []
    temp_files = []
    
    cache_file = "ai_cache.json"
    cache = {}
    if os.path.exists(cache_file):
        try:
            with open(cache_file, "r") as f: cache = json.load(f)
        except: pass

    # Pass 1: Gather data
    total_rows = len(df)
    
    # Simple column detection: use column 0 unless it's "Year"
    name_col_idx = 0
    first_col = str(df.columns[0]).strip().lower()
    if first_col == 'year':
        name_col_idx = 1  # Use second column if first is Year
    
    print(f"   📋 Using column {name_col_idx} for event names: '{df.columns[name_col_idx]}'")
    
    # Common invalid values to skip (headers, etc.)
    skip_values = ['nan', 'sr. no.', 'sr no', 'name of the activity', 'activity']
    
    for i, row in df.iterrows():
        name = str(row.iloc[name_col_idx]).strip()
        # Skip invalid rows
        if not name or name.lower() in skip_values:
            continue
        # Skip very short names (likely headers or codes)
        if len(name) < 3:
            continue
        
        print(f"[{len(events)+1}/{total_rows}] Processing: {name[:50]}...")
        
        # Check cache
        cache_key = f"{criterion}_{name}"
        if cache_key in cache:
            print("      ✓ Using cached narrative")
            report = cache[cache_key]
        else:
            relevant_info = []
            for col, val in row.items():
                if pd.notna(val) and str(val).strip() != "" and "Unnamed" not in str(col):
                    relevant_info.append(f"{col}: {val}")
            row_summary = "\n".join(relevant_info)
            
            report = None
            for attempt in range(3):
                report = generate_narrative(row_summary)
                if report and len(str(report.get('Objective', ''))) > 100:
                    # FORCE the title to be the actual event name from Excel
                    report['Title'] = name
                    print(f"      ✓ AI narrative generated")
                    break
                print(f"      ⚠️ AI attempt {attempt+1} insufficient, retrying...")
                time.sleep(2)
            
            if not report or len(str(report.get('Objective', ''))) < 50: 
                print("      ⚠️ Using fallback narrative")
                report = {"Title": name, "Objective": "Details pending...", "Planning": "Standard planning...", "Participation": "Students participated...", "Evidence": "Records maintained...", "Outcome": "Positive impact..."}
            else:
                # Ensure title is always the actual event name
                report['Title'] = name

            cache[cache_key] = report
            with open(cache_file, "w") as f: json.dump(cache, f)
        
        # Extract hyperlinks
        links = []
        try:
            wb = load_workbook(excel_path, data_only=False)
            ws = wb[criterion]
            for cell in ws[i+3]: 
                if cell.hyperlink: links.append(cell.hyperlink.target)
        except: pass
        
        if links:
            print(f"      🔍 Checking {len(links)} Drive link(s)...")
        imgs, pdf_path, is_pdf = download_drive_content(drive, links, f"doc_{len(events)}")
        if imgs:
            print(f"      📸 Downloaded {len(imgs)} image(s)")
        if pdf_path:
            print(f"      📥 Downloaded PDF")
        temp_files.extend(imgs)
        if pdf_path: temp_files.append(pdf_path)
        result["images_added"] += len(imgs)
        
        events.append({'name': name, 'report': report, 'images': imgs, 'pdf_path': pdf_path, 'is_pdf': is_pdf})
        result["events_processed"] += 1
        
        if len(events) >= 35: break  # Full report with all events

    if not events:
        result["error"] = "No events found in the Excel sheet."
        return result

    # Pass 2: Calculate page numbers
    buff_idx = io.BytesIO()
    doc_idx = SimpleDocTemplate(buff_idx, pagesize=A4, leftMargin=0.75*inch, rightMargin=0.75*inch, topMargin=0.75*inch, bottomMargin=0.75*inch)
    dummy_pdf_base = VESPDF("dummy.pdf")
    dummy_pdf_base.add_cover(criterion, events, {}) 
    doc_idx.build(dummy_pdf_base.story)
    idx_reader = PdfReader(buff_idx)
    index_pages_count = len(idx_reader.pages)

    event_pages = {}
    current_page = 1 + index_pages_count
    
    for i, ev in enumerate(events):
        event_pages[i] = current_page
        
        dummy_ev = VESPDF("dummy_ev.pdf")
        dummy_ev.add_event(i+1, ev['report'], ev['images'], ev['is_pdf'])
        
        buff = io.BytesIO()
        doc = SimpleDocTemplate(buff, pagesize=A4, leftMargin=0.75*inch, rightMargin=0.75*inch, topMargin=0.75*inch, bottomMargin=0.75*inch)
        doc.build(dummy_ev.story)
        ev_summary_pages = len(PdfReader(buff).pages)
        
        pages_in_this_event = ev_summary_pages
        if ev['is_pdf'] and ev['pdf_path']:
            try: pages_in_this_event += len(PdfReader(ev['pdf_path']).pages)
            except: pass
            
        current_page += pages_in_this_event

    # Pass 3: Final build
    base_output = "base_report.pdf"
    final_pdf_obj = VESPDF(base_output)
    final_pdf_obj.add_cover(criterion, events, event_pages)
    for i, ev in enumerate(events):
        final_pdf_obj.add_event(i+1, ev['report'], ev['images'], ev['is_pdf'])
    final_pdf_obj.build_doc()
    
    # Merge PDFs
    writer = PdfWriter()
    base_reader = PdfReader(base_output)
    for p in range(index_pages_count):
        writer.add_page(base_reader.pages[p])
    
    base_current_idx = index_pages_count
    for i, ev in enumerate(events):
        dummy_ev = VESPDF("temp.pdf")
        dummy_ev.add_event(i+1, ev['report'], ev['images'], ev['is_pdf'])
        buff = io.BytesIO()
        doc = SimpleDocTemplate(buff, pagesize=A4, leftMargin=0.75*inch, rightMargin=0.75*inch, topMargin=0.75*inch, bottomMargin=0.75*inch)
        doc.build(dummy_ev.story)
        ev_summary_pages = len(PdfReader(buff).pages)
        
        for p in range(ev_summary_pages):
            writer.add_page(base_reader.pages[base_current_idx])
            base_current_idx += 1
            
        if ev['is_pdf'] and ev['pdf_path']:
            try:
                merge_reader = PdfReader(ev['pdf_path'])
                for p in merge_reader.pages:
                    writer.add_page(p)
            except: pass

    with open(output_path, "wb") as f:
        writer.write(f)
    
    result["pages"] = len(writer.pages)
    result["output_path"] = output_path
    result["success"] = True
    
    # Cleanup
    for f_path in temp_files: 
        try: os.remove(f_path)
        except: pass
    for f_path in ["dummy.pdf", "dummy_ev.pdf", "temp.pdf", "base_report.pdf"]:
        if os.path.exists(f_path): os.remove(f_path)
    
    print(f"✅ Report generated: {output_path} ({result['pages']} pages)")
    return result
