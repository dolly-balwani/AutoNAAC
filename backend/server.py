"""
FastAPI Server for NAAC Report Generation
Exposes the LangGraph-based multi-agent system as REST API endpoints.
"""

import os
import shutil
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional, List

from agents import app as langgraph_app
from fpdf import FPDF
from excel_parser import get_available_criteria
from report_compiler_v4 import compile_enhanced_report

# Initialize FastAPI
app = FastAPI(
    title="NAAC Report Generator API",
    description="Multi-agent LLM system for generating NAAC accreditation reports",
    version="1.0.0"
)

# Enable CORS for frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- Request/Response Models ---

class ReportRequest(BaseModel):
    criterion: str


class ReportResponse(BaseModel):
    criterion: str
    report: str
    revision_count: int
    pdf_filename: Optional[str] = None
    txt_filename: Optional[str] = None


class HealthResponse(BaseModel):
    status: str
    message: str


# --- Helper Functions ---

def generate_pdf(criterion: str, content: str, filename: str) -> str:
    """Generates a PDF report from the text content."""
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # Title
    pdf.set_font("Helvetica", "B", 16)
    safe_title = criterion.encode('latin-1', errors='replace').decode('latin-1')
    pdf.cell(0, 10, f"NAAC Criterion: {safe_title}", ln=True, align="C")
    pdf.ln(10)
    
    # Body
    pdf.set_font("Helvetica", "", 11)
    safe_content = content.encode('latin-1', errors='replace').decode('latin-1')
    pdf.multi_cell(0, 7, safe_content)
    
    pdf_filename = filename.replace(".txt", ".pdf")
    pdf.output(pdf_filename)
    return pdf_filename


# --- API Endpoints ---

@app.get("/api/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        message="NAAC Report Generator API is running"
    )


@app.post("/api/generate-report", response_model=ReportResponse)
async def generate_report(request: ReportRequest):
    """
    Generate a NAAC report for the specified criterion.
    Uses the multi-agent LangGraph workflow with Gemini.
    """
    try:
        print(f"\n🚀 API: Starting report generation for: {request.criterion}\n")
        
        initial_state = {
            "criterion": request.criterion,
            "evidence": "",
            "draft": "",
            "critique": "",
            "revision_count": 0,
            "final_report": ""
        }
        
        # Run the LangGraph workflow
        final_state = langgraph_app.invoke(initial_state)
        
        # Save to TXT file
        txt_filename = f"report_{request.criterion.replace(' ', '_')}.txt"
        with open(txt_filename, "w", encoding="utf-8") as f:
            f.write(f"NAAC CRITERION: {request.criterion}\n\n")
            f.write(final_state["draft"])
        
        # Save to PDF file
        pdf_filename = generate_pdf(request.criterion, final_state["draft"], txt_filename)
        
        print(f"✅ API: Report generated successfully")
        
        return ReportResponse(
            criterion=request.criterion,
            report=final_state["draft"],
            revision_count=final_state.get("revision_count", 0),
            pdf_filename=pdf_filename,
            txt_filename=txt_filename
        )
        
    except Exception as e:
        print(f"❌ API Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/criteria")
async def list_criteria():
    """List available NAAC criteria."""
    # This can be expanded to read from a database or config file
    return {
        "criteria": [
            "1.3.1 Integration of Cross-cutting issues",
            "5.1.3 Capacity building and skills enhancement initiatives",
            "5.3.3 Sports and Cultural Events"
        ]
    }


# --- Enhanced Report Compilation Endpoints ---

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


class CompileRequest(BaseModel):
    excel_filename: str
    criterion: str
    generate_captions: bool = True


class CompileResponse(BaseModel):
    success: bool
    output_path: Optional[str] = None
    download_url: Optional[str] = None
    events_processed: int = 0
    images_added: int = 0
    pages: int = 0
    error: Optional[str] = None


@app.post("/api/upload-excel")
async def upload_excel(file: UploadFile = File(...)):
    """
    Upload an Excel file containing NAAC criterion data.
    Returns the filename and available criteria sheets.
    """
    try:
        # Save uploaded file
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_path, "wb") as f:
            shutil.copyfileobj(file.file, f)
        
        # Get available criteria from the Excel
        criteria = get_available_criteria(file_path)
        
        return {
            "success": True,
            "filename": file.filename,
            "filepath": file_path,
            "available_criteria": criteria
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/compile-report", response_model=CompileResponse)
async def compile_report(request: CompileRequest):
    """
    Compile an enhanced NAAC report with:
    - Clickable Table of Contents
    - AI-generated narratives per event
    - Image thumbnails with detailed captions
    - PDF bookmarks for navigation
    """
    try:
        excel_path = os.path.join(UPLOAD_DIR, request.excel_filename)
        
        if not os.path.exists(excel_path):
            return CompileResponse(
                success=False,
                error=f"Excel file not found: {request.excel_filename}"
            )
        
        print(f"\n🚀 API: Starting enhanced report compilation")
        print(f"   Excel: {request.excel_filename}")
        print(f"   Criterion: {request.criterion}")
        
        # Run the enhanced compiler
        result = compile_enhanced_report(
            excel_path=excel_path,
            criterion=request.criterion,
            output_dir=".",
            generate_captions=request.generate_captions
        )
        
        if result["success"]:
            return CompileResponse(
                success=True,
                output_path=result["output_path"],
                download_url=f"/api/download/{os.path.basename(result['output_path'])}",
                events_processed=result["events_processed"],
                images_added=result["images_added"],
                pages=result["pages"]
            )
        else:
            return CompileResponse(
                success=False,
                error=result.get("error", "Unknown error")
            )
            
    except Exception as e:
        print(f"❌ Compile Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/download/{filename}")
async def download_report(filename: str):
    """Download a generated report PDF."""
    file_path = filename
    if not os.path.exists(file_path):
        file_path = os.path.join(".", filename)
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileResponse(
        file_path,
        media_type="application/pdf",
        filename=filename
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
