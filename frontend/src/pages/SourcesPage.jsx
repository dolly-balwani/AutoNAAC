import { useState } from 'react';
import { Card, Button, Badge } from '../components/UI';
import { ExcelUpload, CriteriaSelector, ApiDataConfig } from '../components/Sources';
import { useExcelUpload } from '../hooks';

/**
 * Sources Page
 * 
 * Select data source for NAAC report generation.
 * Supports Excel file upload or API data connection.
 */
function SourcesPage() {
  // Data source selection: 'excel' or 'api'
  const [dataSource, setDataSource] = useState('excel');
  
  // Excel upload hook
  const {
    excelFile,
    availableCriteria,
    selectedCriterion,
    setSelectedCriterion,
    uploadStatus,
    reportStatus,
    error,
    reportResult,
    isUploading,
    isGenerating,
    canGenerate,
    hasReport,
    handleUpload,
    handleGenerateReport,
    reset,
  } = useExcelUpload();

  return (
    <div>
      {/* Page Header */}
      <div className="page-header">
        <h1 className="page-header__title">Data Source</h1>
        <p className="page-header__description">
          Select how you want to provide data for your NAAC accreditation report.
        </p>
      </div>

      {/* Data Source Selection */}
      <Card title="Select Data Source" subtitle="Choose how to import your NAAC data">
        <div className="source-options">
          <div 
            className={`source-option ${dataSource === 'excel' ? 'source-option--active' : ''}`}
            onClick={() => { setDataSource('excel'); reset(); }}
          >
            <span className="source-option__icon">📊</span>
            <div className="source-option__content">
              <h3 className="source-option__title">Excel Upload</h3>
              <p className="source-option__description">
                Upload an Excel file containing your NAAC criterion data with Google Drive links.
              </p>
            </div>
            {dataSource === 'excel' && <span className="source-option__check">✓</span>}
          </div>
          
          <div 
            className={`source-option ${dataSource === 'api' ? 'source-option--active' : ''}`}
            onClick={() => { setDataSource('api'); reset(); }}
          >
            <span className="source-option__icon">🔌</span>
            <div className="source-option__content">
              <h3 className="source-option__title">API Data</h3>
              <p className="source-option__description">
                Connect to your institution's data systems to fetch NAAC evidence automatically.
              </p>
            </div>
            {dataSource === 'api' && <span className="source-option__check">✓</span>}
          </div>
        </div>
      </Card>

      {/* Excel Upload Flow */}
      {dataSource === 'excel' && (
        <>
          {/* Step 1: Upload Excel */}
          <Card 
            title="Step 1: Upload Excel File" 
            subtitle="Upload your NAAC criterion data file"
            style={{ marginTop: '24px' }}
          >
            <ExcelUpload 
              onFileSelected={handleUpload}
              disabled={isUploading || isGenerating}
              currentFile={excelFile}
            />
            
            {isUploading && (
              <div className="status-message status-message--info" style={{ marginTop: '16px' }}>
                <span className="status-message__icon">⏳</span>
                <span>Uploading and analyzing Excel file...</span>
              </div>
            )}
            
            {uploadStatus === 'success' && (
              <div className="status-message status-message--success" style={{ marginTop: '16px' }}>
                <span className="status-message__icon">✅</span>
                <span>Excel file uploaded successfully!</span>
              </div>
            )}
            
            {uploadStatus === 'error' && (
              <div className="status-message status-message--error" style={{ marginTop: '16px' }}>
                <span className="status-message__icon">❌</span>
                <span>{error || 'Failed to upload file'}</span>
              </div>
            )}
          </Card>

          {/* Step 2: Select Criterion */}
          {uploadStatus === 'success' && (
            <Card 
              title="Step 2: Select Criterion" 
              subtitle="Choose which NAAC criterion to generate a report for"
              style={{ marginTop: '24px' }}
            >
              <CriteriaSelector
                criteria={availableCriteria}
                selected={selectedCriterion}
                onChange={setSelectedCriterion}
                disabled={isGenerating}
              />
            </Card>
          )}

          {/* Step 3: Generate Report */}
          {canGenerate && (
            <Card 
              title="Step 3: Generate Report" 
              subtitle="Create your enhanced NAAC report"
              style={{ marginTop: '24px' }}
            >
              <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                <p className="text-sm" style={{ color: 'var(--color-gray-600)' }}>
                  The report will include:
                </p>
                <ul style={{ paddingLeft: '20px', color: 'var(--color-gray-600)', fontSize: '14px', lineHeight: '1.8' }}>
                  <li>Clickable Table of Contents</li>
                  <li>AI-generated narratives for each event</li>
                  <li>Image thumbnails with captions</li>
                  <li>PDF bookmarks for navigation</li>
                </ul>
                
                <Button 
                  variant="primary" 
                  size="lg"
                  onClick={() => handleGenerateReport(true)}
                  disabled={isGenerating}
                  style={{ alignSelf: 'flex-start' }}
                >
                  {isGenerating ? '⏳ Generating Report...' : '🚀 Generate Report'}
                </Button>
              </div>
              
              {isGenerating && (
                <div className="status-message status-message--info" style={{ marginTop: '16px' }}>
                  <span className="status-message__icon">⏳</span>
                  <div>
                    <p><strong>Generating report...</strong></p>
                    <p className="text-sm">This may take a few minutes as we process images and generate AI narratives.</p>
                  </div>
                </div>
              )}
              
              {reportStatus === 'error' && (
                <div className="status-message status-message--error" style={{ marginTop: '16px' }}>
                  <span className="status-message__icon">❌</span>
                  <span>{error || 'Failed to generate report'}</span>
                </div>
              )}
            </Card>
          )}

          {/* Report Ready - Download */}
          {hasReport && (
            <Card 
              title="Report Ready! 🎉" 
              style={{ marginTop: '24px', backgroundColor: 'var(--color-success-light)', border: '2px solid var(--color-success)' }}
            >
              <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                <div className="stats-grid">
                  <div className="stat-card">
                    <div className="stat-card__label">Events Processed</div>
                    <div className="stat-card__value">{reportResult?.events_processed || 0}</div>
                  </div>
                  <div className="stat-card">
                    <div className="stat-card__label">Images Added</div>
                    <div className="stat-card__value">{reportResult?.images_added || 0}</div>
                  </div>
                  <div className="stat-card">
                    <div className="stat-card__label">Total Pages</div>
                    <div className="stat-card__value">{reportResult?.pages || 0}</div>
                  </div>
                </div>
                
                <a 
                  href={reportResult?.downloadUrl}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="btn btn--primary btn--lg"
                  style={{ alignSelf: 'flex-start', textDecoration: 'none' }}
                >
                  📥 Download PDF Report
                </a>
                
                <Button 
                  variant="secondary" 
                  onClick={reset}
                  style={{ alignSelf: 'flex-start' }}
                >
                  Generate Another Report
                </Button>
              </div>
            </Card>
          )}
        </>
      )}

      {/* API Data Flow (Placeholder) */}
      {dataSource === 'api' && (
        <Card 
          title="API Configuration" 
          subtitle="Configure your data source connection"
          style={{ marginTop: '24px' }}
        >
          <ApiDataConfig />
        </Card>
      )}

      {/* Help Section */}
      <Card title="Instructions" style={{ marginTop: '24px' }}>
        <div className="text-sm" style={{ color: 'var(--color-gray-600)' }}>
          <h4 style={{ marginBottom: '8px', color: 'var(--color-gray-800)' }}>Excel Upload</h4>
          <ol style={{ paddingLeft: '20px', lineHeight: '1.8', marginBottom: '16px' }}>
            <li><strong>Prepare Excel File:</strong> Your Excel file should have sheets named with criterion codes (e.g., "5.1.3", "5.3.3") containing event data.</li>
            <li><strong>Include Google Drive Links:</strong> Add Google Drive links to documents and images for each event in the proof column.</li>
            <li><strong>Upload File:</strong> Drag and drop or click to upload your Excel file.</li>
            <li><strong>Select Criterion:</strong> Choose which criterion sheet to generate a report for.</li>
            <li><strong>Generate Report:</strong> Click the button to create an enhanced PDF with AI-generated narratives.</li>
          </ol>
          
          <h4 style={{ marginBottom: '8px', color: 'var(--color-gray-800)' }}>Supported NAAC Criteria</h4>
          <p>The system supports <strong>any NAAC criterion</strong> as long as your Excel sheet follows the standard format with columns for:</p>
          <ul style={{ paddingLeft: '20px', lineHeight: '1.8' }}>
            <li>Event/Activity Name</li>
            <li>Date</li>
            <li>Number of Students</li>
            <li>Agencies/Collaborators</li>
            <li>Document Proof Link (Google Drive)</li>
          </ul>
        </div>
      </Card>
    </div>
  );
}

export default SourcesPage;
