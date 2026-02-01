import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import Layout from './components/Layout/Layout.jsx';
import SourcesPage from './pages/SourcesPage.jsx';
import ProcessingPage from './pages/ProcessingPage.jsx';
import CriteriaPage from './pages/CriteriaPage.jsx';
import EvidenceViewPage from './pages/EvidenceViewPage.jsx';
import NarrativeEditorPage from './pages/NarrativeEditorPage.jsx';
import ExportPage from './pages/ExportPage.jsx';

/**
 * Main Application Component
 * 
 * Sets up routing and layout for the NAAC Automation System.
 * All pages are wrapped in a consistent Layout component that includes
 * the sidebar navigation and header.
 */
function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Layout />}>
          {/* Default redirect to Sources page */}
          <Route index element={<Navigate to="/sources" replace />} />
          
          {/* Main application routes */}
          <Route path="sources" element={<SourcesPage />} />
          <Route path="processing" element={<ProcessingPage />} />
          <Route path="criteria" element={<CriteriaPage />} />
          <Route path="evidence" element={<EvidenceViewPage />} />
          <Route path="narrative" element={<NarrativeEditorPage />} />
          <Route path="export" element={<ExportPage />} />
          
          {/* Fallback for unknown routes */}
          <Route path="*" element={<Navigate to="/sources" replace />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;
