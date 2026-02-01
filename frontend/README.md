# NAAC Automation System - Frontend

A production-ready React frontend for institutional NAAC (National Assessment and Accreditation Council) automation system.

## Overview

This application helps educational institutions automate the NAAC accreditation process by:
- Uploading and processing source documents (PDF, DOCX, PPTX, Images)
- Extracting relevant evidence from documents
- Selecting NAAC criteria and sub-criteria
- Generating narrative reports with AI assistance
- Exporting final reports in Word and PDF formats

## Tech Stack

- **React 18** - UI Library
- **Vite 5** - Build Tool & Dev Server
- **React Router 6** - Client-side Routing
- **Pure CSS** - Styling (no external UI frameworks)

## Project Structure

```
src/
├── components/           # Reusable UI components
│   ├── Layout/          # Layout components (Header, Sidebar)
│   ├── UI/              # Generic UI components (Button, Card, etc.)
│   ├── Sources/         # File upload components
│   ├── Processing/      # Processing status components
│   ├── Criteria/        # Criteria selection components
│   ├── Evidence/        # Evidence viewer components
│   ├── Narrative/       # Text editor components
│   └── Export/          # Export option components
├── hooks/               # Custom React hooks with mock data
├── pages/               # Page components
├── styles/              # Global and component styles
├── App.jsx              # Main app with routing
└── main.jsx             # Application entry point
```

## Pages

1. **Sources** (`/sources`) - Upload documents for processing
2. **Processing** (`/processing`) - View processing progress and logs
3. **Criteria** (`/criteria`) - Select NAAC criteria and sub-criteria
4. **Evidence View** (`/evidence`) - Review extracted evidence
5. **Narrative Editor** (`/narrative`) - Edit AI-generated report content
6. **Export** (`/export`) - Download final report in Word/PDF

## Getting Started

### Prerequisites

- Node.js 18+ 
- npm or yarn

### Installation

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

The development server will start at `http://localhost:3000`

## Design Principles

- **Professional & Minimal** - Clean, enterprise-style design
- **Light Color Theme** - Easy on the eyes, suitable for long work sessions
- **High Readability** - Accessible fonts and generous spacing
- **Government/Enterprise Style** - Mature design suitable for faculty/administrators
- **No Animations** - Focus on functionality over flashiness
- **Responsive** - Works on desktop, tablet, and mobile devices

## Color Palette

- Primary: `#1e3a5f` (Dark Blue)
- Background: `#f3f4f6` (Light Gray)
- Cards: `#ffffff` (White)
- Text: `#1f2937` (Dark Gray)
- Borders: `#e5e7eb` (Light Border)

## Features

### File Upload
- Drag and drop support
- File type filtering based on processing mode
- File list with remove functionality

### Processing
- Real-time progress bar
- Live log panel
- Success/failure statistics
- Navigation disabled during processing

### Criteria Selection
- "Select All" option
- Individual criterion selection via drawer
- Multi-select checkboxes for sub-criteria

### Evidence View
- Tabbed interface (Text, Images, Tables)
- Source file and page number display
- Scrollable viewer

### Narrative Editor
- Large editable textarea
- Word and character count
- Regenerate, Improve, and Save buttons

### Export
- Word (.docx) download
- PDF download
- Generation status indicators

## API Integration

This frontend uses placeholder API calls. To integrate with a real backend:

1. Replace mock data in hooks with actual API calls
2. Update the hooks in `src/hooks/` directory
3. Configure API base URL in environment variables

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## License

This project is for institutional use. All rights reserved.
