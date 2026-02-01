import { useNavigate } from 'react-router-dom';
import { Card, Button, Select } from '../components/UI';
import { FileUpload, FileList } from '../components/Sources';
import { useFileUpload, useProcessing } from '../hooks';

/**
 * Sources Page
 * 
 * Upload documents for NAAC processing.
 * Supports PDF, DOCX, PPTX, and image files.
 */
function SourcesPage() {
  const navigate = useNavigate();
  const { 
    files, 
    processingMode, 
    setProcessingMode, 
    addFiles, 
    removeFile,
    getAcceptedTypes,
    canProcess 
  } = useFileUpload();
  
  const { startProcessing } = useProcessing();

  // Processing mode options
  const modeOptions = [
    { value: 'pdf', label: 'PDF Documents' },
    { value: 'docx', label: 'Word Documents (DOCX)' },
    { value: 'pptx', label: 'PowerPoint Presentations (PPTX)' },
    { value: 'images', label: 'Images (PNG, JPG, etc.)' }
  ];

  /**
   * Handle start processing button click
   */
  const handleStartProcessing = () => {
    startProcessing(files);
    navigate('/processing');
  };

  return (
    <div>
      {/* Page Header */}
      <div className="page-header">
        <h1 className="page-header__title">Upload Source Documents</h1>
        <p className="page-header__description">
          Select the document type and upload files to extract evidence for NAAC accreditation.
        </p>
      </div>

      {/* Processing Mode Selection */}
      <Card 
        title="Processing Mode" 
        subtitle="Select the type of documents you want to process"
      >
        <Select
          label="Document Type"
          value={processingMode}
          onChange={setProcessingMode}
          options={modeOptions}
          placeholder="Select document type..."
          required
        />
        
        {processingMode && (
          <p className="text-sm text-muted" style={{ marginTop: '8px' }}>
            Selected mode: <strong>{modeOptions.find(o => o.value === processingMode)?.label}</strong>
          </p>
        )}
      </Card>

      {/* File Upload Area */}
      <Card 
        title="Upload Files" 
        subtitle="Drag and drop files or click to browse"
        style={{ marginTop: '24px' }}
      >
        <FileUpload
          onFilesSelected={addFiles}
          acceptedTypes={getAcceptedTypes()}
          multiple={true}
          disabled={!processingMode}
        />
        
        {!processingMode && (
          <p className="text-sm text-muted text-center" style={{ marginTop: '16px' }}>
            Please select a processing mode first
          </p>
        )}
      </Card>

      {/* Uploaded Files List */}
      {files.length > 0 && (
        <Card 
          title={`Uploaded Files (${files.length})`}
          subtitle="Review your files before processing"
          style={{ marginTop: '24px' }}
          footer={
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span className="text-sm text-muted">
                {files.length} file(s) ready for processing
              </span>
              <Button 
                variant="primary" 
                size="lg"
                onClick={handleStartProcessing}
                disabled={!canProcess}
              >
                Start Processing
              </Button>
            </div>
          }
        >
          <FileList files={files} onRemove={removeFile} />
        </Card>
      )}

      {/* Help Section */}
      <Card 
        title="Instructions" 
        style={{ marginTop: '24px' }}
      >
        <div className="text-sm" style={{ color: 'var(--color-gray-600)' }}>
          <ol style={{ paddingLeft: '20px', lineHeight: '1.8' }}>
            <li><strong>Select Processing Mode:</strong> Choose the type of documents you want to upload (PDF, Word, PowerPoint, or Images).</li>
            <li><strong>Upload Files:</strong> Drag and drop files into the upload area or click to browse. Only files matching the selected mode will be accepted.</li>
            <li><strong>Review Files:</strong> Check the uploaded files list and remove any unwanted files.</li>
            <li><strong>Start Processing:</strong> Click the "Start Processing" button to begin extracting evidence from your documents.</li>
          </ol>
        </div>
      </Card>
    </div>
  );
}

export default SourcesPage;
