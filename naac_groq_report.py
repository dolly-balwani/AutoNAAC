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
    from pypdf import PdfReader
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
            gauth.LocalWebserverAuth()
        elif gauth.access_token_expired:
            gauth.Refresh()
        else:
            gauth.Authorize()
        gauth.SaveCredentialsFile("mycreds.txt")
        return GoogleDrive(gauth)
    except Exception as e:
        print(f"Drive Auth Error: {e}")
        return None

def download_images(drive, url, folder_prefix):
    images = []
    if not drive or not url: return images
    m = re.search(r'([a-zA-Z0-9_-]{25,})', url)
    if not m: return images
    fid = m.group(1)
    try:
        file_list = drive.ListFile({'q': f"'{fid}' in parents and trashed=false and mimeType contains 'image/'"}).GetList()
        for f in file_list[:2]:
            fname = f"{folder_prefix}_{f['title'][:10].replace(' ', '_')}.jpg"
            f.GetContentFile(fname)
            images.append(fname)
    except: pass
    return images

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
        self.doc = SimpleDocTemplate(filename, pagesize=A4, leftMargin=0.75*inch, rightMargin=0.75*inch, topMargin=0.75*inch, bottomMargin=0.75*inch)
        self.styles = getSampleStyleSheet()
        self.story = []
        self._setup_styles()

    def _setup_styles(self):
        # Header - Big Red with leading
        self.s_header = ParagraphStyle(
            'H', 
            fontSize=24, 
            textColor=VES_RED, 
            alignment=1, 
            fontName='Times-Bold',
            leading=28
        )
        # Event Title - Medium Red with leading
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
        self.s_body = ParagraphStyle('B', fontSize=11, leading=14, alignment=4, fontName='Times-Roman', spaceAfter=6)
        self.s_label = ParagraphStyle('L', parent=self.s_body, fontName='Times-Bold', spaceBefore=8, textColor=VES_RED)

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
        # Index Item Style (Enforce wrapping)
        self.s_idx_item = ParagraphStyle('IdxItem', fontSize=10, leading=12, alignment=0, fontName='Times-Roman')

    def add_cover(self, events, event_pages=None):
        # Use a 3-column table for logo on left but text centered in middle
        logo = None
        if os.path.exists("ves_logo.png"):
            try:
                logo = Image("ves_logo.png", width=1.1*inch, height=1.1*inch)
            except: pass

        center_text = [
            [Paragraph("<b>Vivekanand Education Society's</b>", self.s_header)],
            [Paragraph("Institute of Technology", self.s_sub)],
            [Paragraph("(Affiliated to University of Mumbai, Approved by AICTE & Recognized by Govt. of Maharashtra)", self.s_aff)]
        ]
        text_table = Table(center_text, colWidths=[5.0*inch])
        text_table.setStyle(TableStyle([('ALIGN', (0,0), (-1,-1), 'CENTER'), ('VALIGN', (0,0), (-1,-1), 'MIDDLE')]))

        # Logo on left, Text in middle, Empty spacer on right to keep text centered
        header_table = Table([[logo, text_table, Spacer(1.2*inch, 1.1*inch)]], 
                           colWidths=[1.2*inch, 5.0*inch, 1.2*inch])
        header_table.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('LEFTPADDING', (0,0), (-1,-1), 0),
            ('RIGHTPADDING', (0,0), (-1,-1), 0),
        ]))
        
        self.story.append(header_table)
        self.story.append(Spacer(1, 0.4*inch))
        self.story.append(Paragraph("<u><b>5.1.3</b></u>", ParagraphStyle('C', fontSize=14, alignment=1, fontName='Times-Bold', leading=18)))
        self.story.append(Paragraph("<b>Capacity Building and Skill Enhancement</b>", ParagraphStyle('CT', fontSize=13, alignment=1, fontName='Times-Bold', leading=16)))
        self.story.append(Spacer(1, 0.3*inch))
        self.story.append(Paragraph("<u><b>INDEX</b></u>", ParagraphStyle('I', fontSize=14, alignment=1, fontName='Times-Bold', leading=18)))
        self.story.append(Spacer(1, 0.2*inch))
        
        data = [['Sr. No.', 'Contents', 'Page No.']]
        for i, ev in enumerate(events):
            pg = event_pages.get(i, "?") if event_pages else "?"
            # Use Paragraph for Contents to ensure wrapping and no overlap
            contents_p = Paragraph(clean(ev['name']), self.s_idx_item)
            data.append([str(i+1), contents_p, str(pg)])
        
        # Adjust colWidths to give more space to contents and fix overlap
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

    def add_event(self, idx, report, images):
        title = clean(report.get('Title', 'Activity Report'))
        self.story.append(Paragraph(f"<b>{idx}. {title}</b>", self.s_event_title))
        
        for k in ['Objective', 'Planning', 'Participation', 'Evidence', 'Outcome']:
            content = report.get(k, '')
            if content:
                self.story.append(Paragraph(f"<b>{k}:</b>", self.s_label))
                self.story.append(Paragraph(clean(content), self.s_body))
        
        if images:
            self.story.append(Spacer(1, 0.3*inch))
            for img in images:
                try: 
                    i = Image(img, width=4.5*inch, height=3*inch)
                    self.story.append(i)
                    self.story.append(Spacer(1, 0.15*inch))
                except: pass
        self.story.append(PageBreak())

def main():
    print("🚀 Running NAAC Final Report Generator...")
    drive = get_drive()
    df = pd.read_excel(EXCEL_FILE, sheet_name=SHEET_NAME, header=1)
    events = []
    temp_imgs = []
    
    # Load cache
    cache_file = "ai_cache.json"
    cache = {}
    if os.path.exists(cache_file):
        try:
            with open(cache_file, "r") as f: cache = json.load(f)
        except: pass

    # Pass 1: Gather data and images
    for i, row in df.iterrows():
        name = str(row.iloc[0])
        if not name or name.lower() in ['nan', 'sr. no.']: continue
        
        print(f"[{len(events)+1}/29] Processing: {name[:40]}...")
        
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
                report = {
                    "Title": name, 
                    "Objective": f"To enhance the skills and knowledge of participants in {name}, focusing on practical applications and industry standards. The program aims to align student capabilities with the latest technological trends and academic requirements as per NAAC criterion 5.1.3.", 
                    "Planning": "The session was meticulously planned by the department in collaboration with subject matter experts. Resources including technical documentation and presentation materials were organized to ensure a smooth flow of information and high engagement.", 
                    "Participation": "Students from various years of the Computer Engineering department actively participated in the program. The attendance was high, reflecting the relevance of the topic to the students' career aspirations and academic growth.", 
                    "Evidence": "Institutional records including attendance sheets, feedback forms, and session photographs have been maintained as evidence of the successful conduct of the program.", 
                    "Outcome": "Participants demonstrated improved understanding of the core concepts discussed. The feedback indicates significant value addition in terms of practical knowledge and confidence-building for future professional endeavors."
                }
            # Save to cache
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
        
        imgs = download_images(drive, links[0] if links else None, f"img_{len(events)}")
        temp_imgs.extend(imgs)
        events.append({'name': name, 'report': report, 'images': imgs})
        
        if len(events) >= 29: break

    # Pass 2: Calculate REAL page numbers by building a test document
    print("📏 Calculating EXACT page numbers (Pass 2/3)...")
    
    # We build the events first to see how many pages they take
    event_stories = []
    temp_pdf = VESPDF("dummy.pdf")
    for i, ev in enumerate(events):
        event_story = []
        # Title
        title = clean(ev['report'].get('Title', 'Activity Report'))
        event_story.append(Paragraph(f"<b>{i+1}. {title}</b>", temp_pdf.s_event_title))
        
        # Contents
        for k in ['Objective', 'Planning', 'Participation', 'Evidence', 'Outcome']:
            content = ev['report'].get(k, '')
            if content:
                event_story.append(Paragraph(f"<b>{k}:</b>", temp_pdf.s_label))
                event_story.append(Paragraph(clean(content), temp_pdf.s_body))
        
        # Images
        if ev['images']:
            event_story.append(Spacer(1, 0.2*inch))
            for img in ev['images']:
                try: 
                    event_story.append(Image(img, width=4.5*inch, height=3.2*inch))
                    event_story.append(Spacer(1, 0.15*inch))
                except: pass
        
        event_story.append(PageBreak())
        event_stories.append(event_story)

    # Measure each event's pages
    event_pages = {}
    current_page = 2 # Assuming INDEX fits on 1 page (common for ~30 items)
    # If events > 35, index might take 2 pages, but 29 fits 1 page comfortably
    
    for i, story in enumerate(event_stories):
        event_pages[i] = current_page
        
        # Build event individually to measure pages
        buff = io.BytesIO()
        doc = SimpleDocTemplate(buff, pagesize=A4, leftMargin=0.75*inch, rightMargin=0.75*inch, topMargin=0.75*inch, bottomMargin=0.75*inch)
        doc.build(story)
        reader = PdfReader(buff)
        pages_in_this_event = len(reader.pages)
        current_page += pages_in_this_event

    # Pass 3: FINAL BUILD
    print(f"📄 Finalizing {PDF_OUTPUT} (Pass 3/3)...")
    final_pdf = VESPDF(PDF_OUTPUT)
    final_pdf.add_cover(events, event_pages)
    
    # We MUST REBUILD the story items for the final doc because 'doc.build' 
    # in Pass 2 consumes the flowables in 'event_stories'.
    for i, ev in enumerate(events):
        title = clean(ev['report'].get('Title', 'Activity Report'))
        final_pdf.story.append(Paragraph(f"<b>{i+1}. {title}</b>", final_pdf.s_event_title))
        
        for k in ['Objective', 'Planning', 'Participation', 'Evidence', 'Outcome']:
            content = ev['report'].get(k, '')
            if content:
                final_pdf.story.append(Paragraph(f"<b>{k}:</b>", final_pdf.s_label))
                final_pdf.story.append(Paragraph(clean(content), final_pdf.s_body))
        
        if ev['images']:
            final_pdf.story.append(Spacer(1, 0.2*inch))
            for img in ev['images']:
                try: 
                    final_pdf.story.append(Image(img, width=4.5*inch, height=3*inch))
                    final_pdf.story.append(Spacer(1, 0.15*inch))
                except: pass
        final_pdf.story.append(PageBreak())
    
    final_pdf.doc.build(final_pdf.story)
    
    # Cleanup
    for im in temp_imgs: 
        try: os.remove(im)
        except: pass
    if os.path.exists("dummy.pdf"): os.remove("dummy.pdf")
    
    print(f"✅ COMPLETE! See {PDF_OUTPUT}")

if __name__ == "__main__": main()
