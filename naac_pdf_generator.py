import pandas as pd
import re
import os
import time
import openpyxl
from openpyxl import load_workbook
from urllib.parse import urlparse
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Image, Spacer, PageBreak, Paragraph
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive

# FIXED IMPORTS - Use langchain_core instead of langchain
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_openai import ChatOpenAI
from pydantic import BaseModel
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# ============================================================================
# CONFIGURATION
# ============================================================================
excel_file = r"F:\VESIT\Internship\Criteria 5 CMPN Data 2024-25 .xlsx"
sheet_name = "5.1.3"
pdf_output = "NAAC Criteria 5.1.3.pdf"
logo_file = "vesit.png"  # Make sure this file exists


# ============================================================================
# PYDANTIC MODEL FOR STRUCTURED OUTPUT
# ============================================================================
class Reportout(BaseModel):
    Title: str
    Objective: str
    Planning: str
    Participation: str
    Evidence: str
    Examples: str
    Conclusion: str


# ============================================================================
# HELPER FUNCTIONS - LINK EXTRACTION
# ============================================================================
def extract_links_from_text(text):
    """Extract all URLs and links from text"""
    if pd.isna(text) or text == "":
        return []

    text_str = str(text)
    links = []

    # Pattern to match various URL formats
    url_patterns = [
        r'https?://[^\s\)]+',  # HTTP/HTTPS URLs
        r'www\.[^\s\)]+',      # www URLs
        r'drive\.google\.com[^\s\)]+',  # Google Drive links
        r'docs\.google\.com[^\s\)]+',   # Google Docs links
    ]

    for pattern in url_patterns:
        matches = re.findall(pattern, text_str, re.IGNORECASE)
        for match in matches:
            # Add http:// if missing
            if not match.startswith(('http://', 'https://')):
                if match.startswith('www.'):
                    match = 'https://' + match
                elif 'drive.google.com' in match or 'docs.google.com' in match:
                    match = 'https://' + match
            links.append(match)

    return links


def check_excel_hyperlinks(file_path, sheet_name, row_number):
    """Check for Excel hyperlinks in a specific row"""
    hyperlinks = []
    try:
        wb = load_workbook(file_path, data_only=False)

        if sheet_name not in wb.sheetnames:
            return hyperlinks

        ws = wb[sheet_name]

        # Check specific row (add 2 because header is at row 1, data starts at row 2)
        actual_row = row_number + 2

        for cell in ws[actual_row]:
            if cell.hyperlink and cell.hyperlink.target:
                hyperlinks.append(cell.hyperlink.target)

    except Exception as e:
        print(f"  ⚠️  Error reading hyperlinks from row {row_number}: {e}")

    return hyperlinks


# ============================================================================
# HELPER FUNCTIONS - GOOGLE DRIVE
# ============================================================================
def extract_drive_links_from_row(row_data, excel_file, sheet_name, row_index):
    """Extract Google Drive folder/file links from row data (both text and hyperlinks)"""
    all_links = []

    # 1. Extract from text content
    row_str = str(row_data)
    text_links = extract_links_from_text(row_str)
    all_links.extend(text_links)

    # 2. Extract from Excel hyperlinks
    hyperlinks = check_excel_hyperlinks(excel_file, sheet_name, row_index)
    all_links.extend(hyperlinks)

    # 3. Filter only Google Drive links
    drive_pattern = r'https?://(?:drive\.google\.com|docs\.google\.com)'
    drive_links = [link for link in all_links if re.search(drive_pattern, link, re.IGNORECASE)]

    return drive_links


def extract_file_id_from_url(url):
    """Extract file or folder ID from Google Drive URL"""
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


def download_images_from_drive(drive, folder_id, max_images=15, current_depth=0, max_depth=3):
    """Recursively download images from a Google Drive folder and all its subfolders"""
    images = []

    if current_depth > max_depth:
        return images

    try:
        # Get all image files in current folder
        image_files = drive.ListFile({
            'q': f"'{folder_id}' in parents and trashed=false and mimeType contains 'image/'"
        }).GetList()

        for file in image_files:
            if len(images) >= max_images:
                break
            try:
                # Download the file
                file.GetContentFile(file['title'])
                images.append({
                    'path': file['title'],
                    'title': file['title'],
                    'folder_depth': current_depth
                })
                print(f"  {'  ' * current_depth}✓ Downloaded image: {file['title']}")
            except Exception as e:
                print(f"  {'  ' * current_depth}✗ Error downloading {file['title']}: {e}")
                continue

        # Get all subfolders in current folder
        subfolders = drive.ListFile({
            'q': f"'{folder_id}' in parents and trashed=false and mimeType='application/vnd.google-apps.folder'"
        }).GetList()

        # Recursively process each subfolder
        for subfolder in subfolders:
            if len(images) >= max_images:
                break
            print(f"  {'  ' * current_depth}📁 Processing subfolder: {subfolder['title']}")
            subfolder_images = download_images_from_drive(
                drive,
                subfolder['id'], 
                max_images=max_images - len(images),
                current_depth=current_depth + 1,
                max_depth=max_depth
            )
            images.extend(subfolder_images)

    except Exception as e:
        print(f"  {'  ' * current_depth}✗ Error accessing folder {folder_id}: {e}")

    return images


# ============================================================================
# MAIN EXECUTION
# ============================================================================
def main():
    print("=" * 80)
    print("NAAC CRITERIA PDF GENERATOR WITH AI SUMMARIES")
    print("=" * 80)

    # -------------------------------------------------------------------------
    # 1. Initialize Google Drive
    # -------------------------------------------------------------------------
    print("\n🔐 Initializing Google Drive authentication...")
    try:
        gauth = GoogleAuth()
        gauth.LocalWebserverAuth()
        drive = GoogleDrive(gauth)
        print("✅ Google Drive authenticated successfully")
    except Exception as e:
        print(f"❌ Error initializing Google Drive: {e}")
        print("   Continuing without Google Drive access...")
        drive = None

    # -------------------------------------------------------------------------
    # 2. Initialize LLM (Claude via OpenRouter)
    # -------------------------------------------------------------------------
    # -------------------------------------------------------------------------
# 2. Initialize LLM (Claude via OpenRouter)
# -------------------------------------------------------------------------
    print("\n🤖 Initializing Google Gemma LLM...")
    try:
        llm = ChatOpenAI(
            model="google/gemma-3-27b-it:free",
            base_url="https://openrouter.ai/api/v1",
            api_key=os.environ.get("OPENROUTER_API_KEY"),
            temperature=0.2,
        )
        print("✅ LLM initialized successfully")
    except Exception as e:
        print(f"❌ Error initializing LLM: {e}")
        return

    # -------------------------------------------------------------------------
    # 3. Setup LangChain Parser and Prompt
    # -------------------------------------------------------------------------
    parser = JsonOutputParser(pydantic_object=Reportout)

    prompt = PromptTemplate(
        input_variables=["row"],
        partial_variables={"format_instructions": parser.get_format_instructions()},
        template="""You are an expert academic writer documenting NAAC Accreditation Criteria. 
Based on the provided data about an event/initiative, write a comprehensive and detailed report covering all the following fields.
Provide thorough, well-structured responses for each field with sufficient detail and context.

Data provided:
{row}

For each of the following fields, provide detailed, comprehensive responses:

1. **Title**: Extract or create a concise, descriptive title (2-5 words). Do NOT include "Criterion" prefix.

2. **Objective**: Explain the primary goals, aims, and intended outcomes. (3-5 sentences)

3. **Planning**: Describe how this was planned and organized, including timeline and resources. (4-6 sentences)

4. **Participation**: Detail who participated, numbers, categories, and engagement levels. (4-6 sentences)

5. **Evidence**: List and describe evidence demonstrating successful conduct and impact. (3-5 sentences)

6. **Examples**: Provide specific examples illustrating implementation and outcomes. (4-6 sentences)

7. **Conclusion**: Summarize overall impact, achievements, and recommendations. (5-7 sentences)

{format_instructions}""",
    )

    chain = prompt | llm | parser

    # -------------------------------------------------------------------------
    # 4. Read Excel Data
    # -------------------------------------------------------------------------
    print(f"\n📁 Reading Excel file: {excel_file}")
    print(f"📄 Sheet: {sheet_name}")

    try:
        df = pd.read_excel(excel_file, sheet_name=sheet_name, header=1)
        print(f"✅ Loaded {len(df)} rows from Excel")
    except Exception as e:
        print(f"❌ Error reading Excel file: {e}")
        return

    # -------------------------------------------------------------------------
    # 5. Initialize PDF Document
    # -------------------------------------------------------------------------
    print(f"\n📄 Initializing PDF: {pdf_output}")

    doc = SimpleDocTemplate(pdf_output, pagesize=A4)
    width, height = A4
    story = []
    styles = getSampleStyleSheet()

    # Define custom styles
    title_style = ParagraphStyle(
        "Title",
        parent=styles['Heading1'],
        fontSize=20,
        textColor=colors.HexColor('#1f4788'),
        spaceAfter=12,
        alignment=1  # Center
    )

    heading_style = ParagraphStyle(
        "Heading",
        parent=styles['Heading2'],
        fontSize=18,
        textColor=colors.HexColor('#1f4788'),
        spaceBefore=12,
        spaceAfter=6,
        alignment=0
    )

    content_style = ParagraphStyle(
        "Content",
        parent=styles['Normal'],
        fontSize=11,
        spaceAfter=8,
        alignment=4  # Justify
    )

    field_label_style = ParagraphStyle(
        "FieldLabel",
        parent=styles['Normal'],
        fontSize=11,
        textColor=colors.HexColor('#1f4788'),
        fontName='Helvetica-Bold',
        spaceAfter=4,
        alignment=0
    )

    # Add logo if available
    if os.path.exists(logo_file):
        try:
            img = Image(logo_file, width=width-2*inch, height=1.5*inch, hAlign="CENTER")
            story.append(img)
            story.append(Spacer(1, 0.3*inch))
        except Exception as e:
            print(f"⚠️  Could not add logo: {e}")

    # Add main title
    story.append(Paragraph("NAAC Criteria 5 - Student Support and Progression", title_style))
    story.append(Spacer(1, 0.5*inch))

    # -------------------------------------------------------------------------
    # 6. Process Each Row
    # -------------------------------------------------------------------------
    print("\n" + "=" * 80)
    print("PROCESSING ROWS")
    print("=" * 80)

    processed_count = 0
    failed_count = 0
    downloaded_images = []  # Track all downloaded images for cleanup

    for index, row in df.iterrows():
        try:
            print(f"\n[{index + 1}/{len(df)}] Processing row {index + 1}...")

            # Rate limiting delay
            if index > 0:
                time.sleep(2)

            # Generate AI summary
            result = chain.invoke({"row": row.to_string()})
            processed_count += 1

            # Add title
            if "Title" in result and result["Title"]:
                title_text = f"Criterion 5 Enhancement Initiative: {result['Title']}"
                story.append(Paragraph(f"<b>{title_text}</b>", heading_style))
                story.append(Spacer(1, 0.2*inch))

            # Collect images from Google Drive links
            all_images = []
            if drive:
                # FIXED: Extract links from both text AND hyperlinks
                drive_links = extract_drive_links_from_row(row.to_string(), excel_file, sheet_name, index)

                if drive_links:
                    print(f"  📎 Found {len(drive_links)} Google Drive link(s)")
                    for link in drive_links:
                        file_id, link_type = extract_file_id_from_url(link)

                        if file_id and link_type == 'folder':
                            print(f"  📁 Processing folder: {file_id}")
                            images = download_images_from_drive(drive, file_id, max_images=15, max_depth=3)
                            all_images.extend(images)
                            downloaded_images.extend(images)
                        elif file_id and link_type == 'file':
                            try:
                                file = drive.CreateFile({'id': file_id})
                                file_title = file['title']
                                if any(file_title.lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']):
                                    file.GetContentFile(file_title)
                                    img_info = {'path': file_title, 'title': file_title}
                                    all_images.append(img_info)
                                    downloaded_images.append(img_info)
                                    print(f"  ✓ Downloaded image: {file_title}")
                            except Exception as e:
                                print(f"  ✗ Error processing file {file_id}: {e}")
                else:
                    print(f"  ℹ️  No Google Drive links found in this row")

            # Add text fields
            field_mapping = {
                "Objective": "Objective",
                "Planning": "Planning",
                "Participation": "Participation",
                "Evidence": "Evidence",
                "Examples": "Examples",
                "Conclusion": "Conclusion"
            }

            for field_key, field_label in field_mapping.items():
                if field_key in result and result[field_key]:
                    story.append(Paragraph(f"<b>{field_label}:</b>", field_label_style))
                    story.append(Paragraph(result[field_key], content_style))
                    story.append(Spacer(1, 0.1*inch))

            # Add images after text content
            if all_images:
                story.append(Spacer(1, 0.2*inch))
                story.append(Paragraph("<b>Supporting Images:</b>", field_label_style))
                story.append(Spacer(1, 0.1*inch))

                for img_info in all_images:
                    try:
                        img = Image(img_info['path'], width=5*inch, height=3*inch, hAlign="CENTER")
                        story.append(img)
                        story.append(Paragraph(f"<i>{img_info['title']}</i>", styles['Normal']))
                        story.append(Spacer(1, 0.1*inch))
                    except Exception as e:
                        print(f"  ✗ Error adding image {img_info['path']}: {e}")

            # Add page break between entries
            if index < len(df) - 1:
                story.append(PageBreak())

        except Exception as e:
            failed_count += 1
            error_type = type(e).__name__
            error_msg = str(e)

            print(f"❌ Error processing row {index + 1}: {error_type}")
            print(f"   Message: {error_msg}")

            if "RateLimitError" in error_type or "429" in error_msg or "rate limit" in error_msg.lower():
                print(f"\n⚠️  Rate limit exceeded! Processed {processed_count} rows.")
                break
            else:
                print(f"   Continuing with next row...")
                continue

    # -------------------------------------------------------------------------
    # 7. Build PDF
    # -------------------------------------------------------------------------
    print(f"\n{'=' * 80}")
    print("BUILDING PDF")
    print("=" * 80)
    print(f"📊 Processed: {processed_count} rows")
    print(f"❌ Failed: {failed_count} rows")
    print(f"📷 Images collected: {len(downloaded_images)}")
    print(f"📄 Building PDF: {pdf_output}...")

    try:
        doc.build(story)
        print(f"✅ PDF created successfully: {pdf_output}")
    except Exception as e:
        print(f"❌ Error building PDF: {e}")

    # -------------------------------------------------------------------------
    # 8. Cleanup Downloaded Images
    # -------------------------------------------------------------------------
    print(f"\n🧹 Cleaning up {len(downloaded_images)} downloaded images...")
    cleaned = 0
    for img_info in downloaded_images:
        if os.path.exists(img_info['path']):
            try:
                os.remove(img_info['path'])
                cleaned += 1
            except Exception as e:
                print(f"  ⚠️  Could not delete {img_info['path']}: {e}")

    print(f"✅ Cleaned up {cleaned} image files")
    print("\n" + "=" * 80)
    print("✅ PROCESS COMPLETE!")
    print("=" * 80)


if __name__ == "__main__":
    main()
