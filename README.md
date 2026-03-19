# NAAC Report Generation System

An AI-powered system to automate NAAC accreditation report generation using multi-agent LLMs and Google Drive integration.

## Team
Project developed by a team of 5 members during a Internship.

## 🚀 Features

- **VES-Branded Reports**: Professional PDF reports with VES logo header on every page
- **Groq AI Narratives**: Uses Llama 3.1 via Groq for fast, detailed academic writing
- **Google Drive Integration**: Automatically fetches images and PDFs from Drive links in Excel
- **PDF Merging**: Attaches supporting documents inline within the report
- **Multi-Criterion Support**: Works with any NAAC criterion (5.1.3, 5.2.2, 5.3.3, etc.)
- **Modern Web UI**: React frontend with guided report generation workflow

## 📂 Project Structure

```
├── frontend/                   # React 18 + Vite application
├── backend/                    # FastAPI server
│   ├── server.py              # Main API endpoints
│   ├── ves_report_compiler.py # VES-branded PDF generation engine
│   ├── excel_parser.py        # Excel data extraction
│   └── agents.py              # LangChain agents (optional)
├── data/                       # Input Excel files
├── naac_groq_report.py        # Standalone CLI report generator
└── demo_report_generator.py   # Offline demo (no API keys needed)
```

## 🛠️ Prerequisites

- **Python**: 3.10+
- **Node.js**: 18+
- **API Keys**:
  - `GROQ_API_KEY` - For AI narrative generation
  - `GOOGLE_API_KEY` - For Gemini (optional)
  - Google Drive credentials (`client_secrets.json`, `mycreds.txt`)

## 📦 Installation

### 1. Clone & Install Dependencies

```bash
# Backend
pip install -r backend/requirements.txt

# Frontend
cd frontend && npm install
```

### 2. Environment Setup

Create `.env` in both root and `backend/` folders:

```ini
GROQ_API_KEY=gsk_your_key_here
GOOGLE_API_KEY=your_gemini_key_here
```

### 3. Google Drive Setup

Place these files in the root directory:
- `client_secrets.json` - Google OAuth credentials
- `mycreds.txt` - Generated after first auth (auto-created)
- `ves_logo.png` - VES logo banner

## 🏃 Usage

### Option A: Standalone Script (Recommended for Quick Use)

```bash
# Generate full report from Excel
python naac_groq_report.py
```

This generates `NAAC_VES_FINAL_REPORT.pdf` with all events, AI narratives, and merged PDFs.

### Option B: Web Application

```bash
# Terminal 1: Start Backend
cd backend
python -m uvicorn server:app --host 0.0.0.0 --port 8000 --reload

# Terminal 2: Start Frontend
cd frontend
npm run dev
```

Open http://localhost:5173 → Upload Excel → Select Criterion → Generate Report

## 📋 Excel Format Requirements

Your Excel file should have sheets named with criterion codes (e.g., `5.1.3`) with columns:

| Column | Content |
|--------|---------|
| A | Event Name |
| B | Date |
| C | Number of Students |
| D | Agencies Involved |
| E | Proof Link (Google Drive hyperlink) |

## 🔧 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/health` | GET | Health check |
| `/api/upload-excel` | POST | Upload Excel, get available criteria |
| `/api/compile-report` | POST | Generate VES-branded PDF report |
| `/api/download/{filename}` | GET | Download generated report |

## 📄 Output

Generated reports include:
- VES logo header on every page
- Clickable Table of Contents with page numbers
- AI-generated narratives for each event (Objective, Planning, Participation, Evidence, Outcome)
- Images from Google Drive with captions
- Merged supporting PDFs inline

## 🤝 Contributors

Developed by VES Institute of Technology, Mumbai.

## 📝 License

All rights reserved.
