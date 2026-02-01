import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, Button, ProgressBar } from '../components/UI';
import { LogPanel, StatCard } from '../components/Processing';
import { useProcessing } from '../hooks';

/**
 * Processing Page
 * 
 * Displays document processing progress with live logs and statistics.
 */
function ProcessingPage() {
  const navigate = useNavigate();
  const { 
    isProcessing, 
    progress, 
    currentFile, 
    logs, 
    stats,
    stopProcessing 
  } = useProcessing();

  /**
   * Handle navigation after processing completes
   */
  const handleContinue = () => {
    navigate('/criteria');
  };

  /**
   * Handle stop button click
   */
  const handleStop = () => {
    stopProcessing();
  };

  /**
   * Handle back to sources
   */
  const handleBack = () => {
    navigate('/sources');
  };

  return (
    <div>
      {/* Page Header */}
      <div className="page-header">
        <h1 className="page-header__title">Processing Documents</h1>
        <p className="page-header__description">
          {isProcessing 
            ? 'Documents are being processed. Please do not close this page.'
            : 'Processing complete. Review the results below.'
          }
        </p>
      </div>

      {/* Progress Section */}
      <Card title="Processing Progress">
        <ProgressBar 
          value={progress} 
          variant={progress === 100 ? 'success' : 'default'}
          size="lg"
          showLabel={true}
        />
        
        {currentFile && (
          <p className="text-sm" style={{ marginTop: '16px' }}>
            <strong>Current file:</strong> {currentFile}
          </p>
        )}
        
        {isProcessing && (
          <div style={{ marginTop: '16px', textAlign: 'center' }}>
            <Button variant="danger" onClick={handleStop}>
              Stop Processing
            </Button>
          </div>
        )}
      </Card>

      {/* Statistics Section */}
      <div style={{ marginTop: '24px' }}>
        <div className="stats-grid">
          <StatCard label="Total Files" value={stats.total} />
          <StatCard label="Processed" value={stats.processed} />
          <StatCard 
            label="Successful" 
            value={stats.success} 
            variant="success" 
          />
          <StatCard 
            label="Failed" 
            value={stats.failed} 
            variant={stats.failed > 0 ? 'error' : 'default'} 
          />
        </div>
      </div>

      {/* Logs Section */}
      <Card 
        title="Processing Logs" 
        subtitle="Real-time processing updates"
        style={{ marginTop: '24px' }}
      >
        <LogPanel logs={logs} />
      </Card>

      {/* Navigation Buttons */}
      <Card style={{ marginTop: '24px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between' }}>
          <Button 
            variant="secondary" 
            onClick={handleBack}
            disabled={isProcessing}
          >
            ← Back to Sources
          </Button>
          <Button 
            variant="primary" 
            onClick={handleContinue}
            disabled={isProcessing || stats.success === 0}
          >
            Continue to Criteria →
          </Button>
        </div>
      </Card>

      {/* Processing Notice */}
      {isProcessing && (
        <Card style={{ marginTop: '24px', backgroundColor: 'var(--color-warning-light)', border: '1px solid var(--color-warning)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <span style={{ fontSize: '24px' }}>⚠️</span>
            <div>
              <p className="font-semibold" style={{ color: 'var(--color-warning)', marginBottom: '4px' }}>
                Processing in Progress
              </p>
              <p className="text-sm" style={{ color: 'var(--color-gray-700)' }}>
                Navigation is disabled while documents are being processed. Please wait for processing to complete.
              </p>
            </div>
          </div>
        </Card>
      )}
    </div>
  );
}

export default ProcessingPage;
