import { useNavigate } from 'react-router-dom';
import { Card, Button, Badge } from '../components/UI';
import { ExportCard } from '../components/Export';
import { useExport } from '../hooks';

/**
 * Export Page
 * 
 * Download the final NAAC report in various formats.
 */
function ExportPage() {
  const navigate = useNavigate();
  const { docxStatus, pdfStatus, exportDocx, exportPdf, isExporting } = useExport();

  /**
   * Navigate back
   */
  const handleBack = () => {
    navigate('/narrative');
  };

  /**
   * Start new process
   */
  const handleNewProcess = () => {
    navigate('/sources');
  };

  return (
    <div>
      {/* Page Header */}
      <div className="page-header">
        <h1 className="page-header__title">Export Report</h1>
        <p className="page-header__description">
          Download your completed NAAC accreditation report in your preferred format.
        </p>
      </div>

      {/* Report Summary */}
      <Card title="Report Summary" style={{ marginBottom: '24px' }}>
        <div className="stats-grid">
          <div className="stat-card">
            <div className="stat-card__label">Criteria Included</div>
            <div className="stat-card__value">7</div>
          </div>
          <div className="stat-card">
            <div className="stat-card__label">Sub-criteria</div>
            <div className="stat-card__value">42</div>
          </div>
          <div className="stat-card">
            <div className="stat-card__label">Evidence Items</div>
            <div className="stat-card__value">11</div>
          </div>
          <div className="stat-card">
            <div className="stat-card__label">Word Count</div>
            <div className="stat-card__value">~2,500</div>
          </div>
        </div>
      </Card>

      {/* Export Options */}
      <Card title="Download Options" subtitle="Select your preferred format">
        <div className="export-options">
          <ExportCard
            icon="📄"
            title="Word Document"
            description="Download as Microsoft Word (.docx) format for further editing and formatting."
            onExport={exportDocx}
            status={docxStatus}
            disabled={isExporting}
          />
          <ExportCard
            icon="📕"
            title="PDF Document"
            description="Download as PDF format for sharing and printing. Layout is fixed and professional."
            onExport={exportPdf}
            status={pdfStatus}
            disabled={isExporting}
          />
        </div>
      </Card>

      {/* Export Status */}
      {isExporting && (
        <Card style={{ marginTop: '24px', backgroundColor: 'var(--color-info-light)', border: '1px solid var(--color-info)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <span style={{ fontSize: '24px' }}>⏳</span>
            <div>
              <p className="font-semibold" style={{ color: 'var(--color-info)', marginBottom: '4px' }}>
                Generating Report
              </p>
              <p className="text-sm" style={{ color: 'var(--color-gray-700)' }}>
                Your report is being generated. This may take a few moments...
              </p>
            </div>
          </div>
        </Card>
      )}

      {/* Completion Notice */}
      {(docxStatus === 'completed' || pdfStatus === 'completed') && (
        <Card style={{ marginTop: '24px', backgroundColor: 'var(--color-success-light)', border: '1px solid var(--color-success)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <span style={{ fontSize: '24px' }}>✅</span>
            <div>
              <p className="font-semibold" style={{ color: 'var(--color-success)', marginBottom: '4px' }}>
                Export Complete
              </p>
              <p className="text-sm" style={{ color: 'var(--color-gray-700)' }}>
                Your report has been generated successfully. Check your downloads folder.
              </p>
            </div>
          </div>
        </Card>
      )}

      {/* Navigation Buttons */}
      <Card style={{ marginTop: '24px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between' }}>
          <Button variant="secondary" onClick={handleBack}>
            ← Back to Narrative Editor
          </Button>
          <Button variant="primary" onClick={handleNewProcess}>
            Start New Process
          </Button>
        </div>
      </Card>

      {/* Additional Information */}
      <Card title="Export Information" style={{ marginTop: '24px' }}>
        <div className="text-sm" style={{ color: 'var(--color-gray-600)' }}>
          <h4 style={{ marginBottom: '8px', color: 'var(--color-gray-800)' }}>Word Document (.docx)</h4>
          <ul style={{ paddingLeft: '20px', lineHeight: '1.8', marginBottom: '16px' }}>
            <li>Fully editable format compatible with Microsoft Word and Google Docs</li>
            <li>Includes all text, tables, and embedded images</li>
            <li>Recommended for making additional edits before final submission</li>
          </ul>
          
          <h4 style={{ marginBottom: '8px', color: 'var(--color-gray-800)' }}>PDF Document</h4>
          <ul style={{ paddingLeft: '20px', lineHeight: '1.8' }}>
            <li>Fixed layout that preserves formatting across all devices</li>
            <li>Ideal for official submission and printing</li>
            <li>Includes bookmarks for easy navigation</li>
          </ul>
        </div>
      </Card>
    </div>
  );
}

export default ExportPage;
