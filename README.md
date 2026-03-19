# NAAC Automation System

A comprehensive AI-powered system to automate the generation of NAAC (National Assessment and Accreditation Council) accreditation reports for educational institutions. This system integrates a React frontend, a FastAPI backend, and LangChain-based AI agents to process data, generate narratives, and compile professional PDF reports.

## Team
Project developed by a team of 5 members during a Internship.

## 🚀 Features

- **Automated Report Generation**: Uses LLMs (Google Gemma 2 via OpenRouter/Groq) to write professional academic narratives for NAAC criteria.
- **Evidence Management**: Upload and organize evidence files (images, docs) linked to specific events.
- **Excel Integration**: Parses standard NAAC data templates from Excel files.
- **PDF & Word Export**: Generates formatted reports with Table of Contents, images, and proper academic styling.
- **Dual Mode**:
  - **Full Web App**: Modern React UI with real-time processing feedback.
  - **Standalone Scripts**: Python scripts for quick, headless report generation.

## 📂 Project Structure

- **`frontend/`**: React 18 application with Vite. Handles UI for uploading files and viewing reports.
- **`backend/`**: FastAPI server exposing LangGraph agents and report compilation logic.
- **`data/`**: Directory for input Excel files.
- **`uploads/`**: Directory where uploaded evidence and generated reports are stored.
- **`naac_pdf_generator.py`**: Standalone script for generating reports from Excel + Google Drive links.
- **`demo_report_generator.py`**: Offline demo script that generates a report without API keys (for testing/demo).

## 🛠️ Prerequisites

- **Python**: 3.10+
- **Node.js**: 18+ (for frontend)
- **API Keys**:
  - `OPENROUTER_API_KEY` (for LLM access)
  - Google Drive API credentials (optional, for Drive integration)

## 📦 Installation

### 1. Backend Setup

```bash
# Install Python dependencies
pip install -r backend/requirements.txt
```

### 2. Frontend Setup

```bash
cd frontend
# Install Node dependencies
npm install
```

### 3. Environment Configuration

Create a `.env` file in the root directory (or use the one in `backend/` if running server):

```ini
OPENROUTER_API_KEY=your_key_here
# Add other keys as needed
```

## 🏃 Usage

### Option A: specific Standalone Scripts (Quickest)

To generate a report from a specific Excel file:

```bash
# Run the PDF generator
python naac_pdf_generator.py
```

To run a demo without API keys (uses templates):

```bash
# Run the demo generator
python demo_report_generator.py
```

### Option B: Full Web Application

1. **Start the Backend Server**:
   ```bash
   python backend/server.py
   ```
   Server runs at `http://localhost:8000`.

2. **Start the Frontend Development Server**:
   ```bash
   cd frontend
   npm run dev
   ```
   App runs at `http://localhost:5173`.

3. **Navigate to the App**: Open your browser to the frontend URL to upload files and generate reports.

## 📄 Documentation

- [Frontend Documentation](frontend/README.md): Detailed guide on the React application structure and components.

## 🤝 Contribution

This project is developed for institutional internal use.

## 📝 License

All rights reserved.
