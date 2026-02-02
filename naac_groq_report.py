"""
NAAC FINAL REPORT GENERATOR - GROQ + VES FORMAT (AUTOMATED)
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

load_dotenv()

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

EXCEL_FILE = "data/Criteria 5.1.3 CMPN Data 2024-25.xlsx"
SHEET_NAME = "5.1.3"
PDF_OUTPUT = "NAAC_VES_FINAL_REPORT.pdf"
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
        # TRY TO USE LOCAL AUTH WITHOUT BROWSER IF POSSIBLE
        gauth.LoadCredentialsFile("mycreds.txt")
        if gauth.credentials is None:
            # First time auth
            gauth.LocalWebserverAuth()
        elif gauth.access_token_expired:
            try:
                gauth.Refresh()
            except:
                # If refresh fails, redo auth
                gauth.LocalWebserverAuth()
        else:
            gauth.Authorize()
        gauth.SaveCredentialsFile("mycreds.txt")
        return GoogleDrive(gauth)
    except Exception as e:
        print(f"Drive Auth Error: {e}")
        return None

def download_drive_content(drive, urls, folder_prefix):
    """
    Tries to find images and PDFs from a list of URLs.
    """
    images = []
    pdf_path = None
    if not drive or not urls: return images, None, False
    
    # Process each link found in the row
    for link_idx, url in enumerate(urls):
        if not url or not isinstance(url, str): continue
        m = re.search(r'([a-zA-Z0-9_-]{25,})', url)
        if not m: continue
        fid = m.group(1)
        
        print(f"      🔍 Checking Drive Link {link_idx+1}: {fid[:10]}...")
        try:
            f_meta = drive.CreateFile({'id': fid})
            f_meta.FetchMetadata()
            
            # If it's a direct PDF
            if f_meta['mimeType'] == 'application/pdf':
                if not pdf_path:
                    pdf_path = f"{folder_prefix}_doc_{link_idx}.pdf"
                    print(f"      📥 Downloading PDF: {f_meta['title']}")
                    f_meta.GetContentFile(pdf_path)
                continue

            # If it's a folder, list its contents
            query = f"'{fid}' in parents and trashed=false"
            children = drive.ListFile({'q': query}).GetList()
            
            for child in children:
                mtype = child['mimeType']
                if 'image/' in mtype and len(images) < 4:
                    fname = f"{folder_prefix}_img_{link_idx}_{len(images)}.jpg"
                    print(f"      📸 Downloading Image: {child['title']}")
                    child.GetContentFile(fname)
                    images.append(fname)
                elif mtype == 'application/pdf' and not pdf_path:
                    pdf_path = f"{folder_prefix}_doc_{link_idx}.pdf"
                    print(f"      📥 Downloading PDF (from folder): {child['title']}")
                    child.GetContentFile(pdf_path)
                    
        except Exception as e:
            print(f"      ⚠️ Drive Link Error: {e}")
            
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
        print(f"      AI Exception: {e}")
        return None

class VESPDF:
    def __init__(self, filename):
        # Increased topMargin to accommodate the logo header comfortably
        self.doc = SimpleDocTemplate(filename, pagesize=A4, 
                                   leftMargin=0.75*inch, rightMargin=0.75*inch, 
                                   topMargin=2.8*inch, bottomMargin=0.75*inch)
        self.styles = getSampleStyleSheet()
        self.story = []
        self._setup_styles()

    def _setup_styles(self):
        # Header - Big Red
        self.s_header = ParagraphStyle(
            'H', 
            fontSize=22, 
            textColor=VES_RED, 
            alignment=1, 
            fontName='Times-Bold',
            leading=26
        )
        # Event Title
        self.s_event_title = ParagraphStyle(
            'ET', 
            fontSize=18, 
            textColor=VES_RED, 
            fontName='Times-Bold', 
            spaceBefore=12,
            spaceAfter=12,
            leading=22
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
        if os.path.exists("ves_logo.png"):
            # Centering 6.5in banner: x = (8.27 - 6.5)/2 = 0.885
            # Lowering Y significantly to A4[1] - 2.6 to avoid any top cut-off
            canvas.drawImage("ves_logo.png", 0.885*inch, A4[1] - 2.6*inch, width=6.5*inch, preserveAspectRatio=True, mask='auto')
        canvas.restoreState()

    def add_cover(self, events, event_pages=None):
        # The cover doesn't get the header, so we just add spacer for where header would be
        self.story.append(Spacer(1, 1.3*inch))
        
        # We don't use the logo again since it's in the header (on this page too)
        # But for the cover, we want the title centered.
        self.story.append(Paragraph("<u><b>5.1.3</b></u>", ParagraphStyle('C', fontSize=14, alignment=1, fontName='Times-Bold', leading=18)))
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
        
        # Add summary/narrative first
        for k in ['Objective', 'Planning', 'Participation', 'Evidence', 'Outcome']:
            content = report.get(k, '')
            if content:
                self.story.append(Paragraph(f"<b>{k}:</b>", self.s_label))
                self.story.append(Paragraph(clean(content), self.s_body))
        
        # Add images if found (Common for folder-based events)
        if images:
            self.story.append(Spacer(1, 0.2*inch))
            for i, img in enumerate(images):
                try: 
                    # Scale image to fit, max width 6 inches
                    img_obj = Image(img, width=6.0*inch, height=None)
                    # Maintain aspect ratio if height is not specified, but ReportLab needs something. 
                    # Better to use a simpler call:
                    # i = Image(img, width=4.5*inch, height=3*inch) 
                    # Let's stick to a safe fixed size for now or better scaling
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

def main():
    print("🚀 Running NAAC Final Report Generator...")
    drive = get_drive()
    df = pd.read_excel(EXCEL_FILE, sheet_name=SHEET_NAME, header=1)
    events = []
    temp_files = [] 
    
    # Load cache
    cache_file = "ai_cache.json"
    cache = {}
    if os.path.exists(cache_file):
        try:
            with open(cache_file, "r") as f: cache = json.load(f)
        except: pass

    # Pass 1: Gather data and images/PDFs
    for i, row in df.iterrows():
        name = str(row.iloc[0])
        if not name or name.lower() in ['nan', 'sr. no.']: continue
        
        print(f"[{len(events)+1}/{len(df)}] Processing: {name[:40]}...")
        
        # Check cache
        if name in cache:
            print("      ✓ Using cached narrative")
            report = cache[name]
        else:
            # Better data summary for AI
            relevant_info = []
            for col, val in row.items():
                if pd.notna(val) and str(val).strip() != "" and "Unnamed" not in str(col):
                    relevant_info.append(f"{col}: {val}")
            row_summary = "\n".join(relevant_info)
            
            # Retry logic for Groq
            report = None
            for attempt in range(3):
                report = generate_narrative(row_summary)
                if report and len(str(report.get('Objective', ''))) > 100:
                    break
                print(f"      ⚠️ AI attempt {attempt+1} insufficient, retrying...")
                time.sleep(3)
            
            if not report or len(str(report.get('Objective', ''))) < 50: 
                report = {"Title": name, "Objective": "Detailed narrative being drafted for this activity...", "Planning": "Standard planning procedures were followed...", "Participation": "Students and faculty actively participated...", "Evidence": "Institutional records are maintained...", "Outcome": "Positive impact on student technical skills..."}

            cache[name] = report
            with open(cache_file, "w") as f: json.dump(cache, f)
        
        links = []
        try:
            wb = load_workbook(EXCEL_FILE, data_only=False)
            ws = wb[SHEET_NAME]
            # Find hyperlinks in the current row
            for cell in ws[i+3]: 
                if cell.hyperlink: links.append(cell.hyperlink.target)
        except: pass
        
        imgs, pdf_path, is_pdf = download_drive_content(drive, links, f"doc_{len(events)}")
        temp_files.extend(imgs)
        if pdf_path: temp_files.append(pdf_path)
        
        events.append({'name': name, 'report': report, 'images': imgs, 'pdf_path': pdf_path, 'is_pdf': is_pdf})
        
        if len(events) >= 35: break 

    # Pass 2: Calculate REAL page numbers
    print("📏 Calculating EXACT page numbers (Pass 2/3)...")
    
    # Measure INDEX pages first
    buff_idx = io.BytesIO()
    doc_idx = SimpleDocTemplate(buff_idx, pagesize=A4, leftMargin=0.75*inch, rightMargin=0.75*inch, topMargin=0.75*inch, bottomMargin=0.75*inch)
    dummy_pdf_base = VESPDF("dummy.pdf")
    dummy_pdf_base.add_cover(events, {}) 
    doc_idx.build(dummy_pdf_base.story)
    idx_reader = PdfReader(buff_idx)
    index_pages_count = len(idx_reader.pages)

    event_pages = {}
    current_page = 1 + index_pages_count
    
    for i, ev in enumerate(events):
        event_pages[i] = current_page
        
        # Build individual event piece to measure
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

    # Pass 3: FINAL BUILD
    print(f"📄 Finalizing {PDF_OUTPUT} (Pass 3/3)...")
    base_output = "base_report.pdf"
    final_pdf_obj = VESPDF(base_output)
    final_pdf_obj.add_cover(events, event_pages)
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

    with open(PDF_OUTPUT, "wb") as f:
        writer.write(f)
    
    # Cleanup
    for f in temp_files: 
        try: os.remove(f)
        except: pass
    for f in ["dummy.pdf", "dummy_ev.pdf", "temp.pdf", "base_report.pdf", "dummy_idx.pdf"]:
        if os.path.exists(f): os.remove(f)
    
    print(f"✅ COMPLETE! See {PDF_OUTPUT}")

if __name__ == "__main__": main()
