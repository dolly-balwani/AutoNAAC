import { useNavigate } from 'react-router-dom';
import { Card, Button, Tabs } from '../components/UI';
import { EvidenceViewer } from '../components/Evidence';
import { useEvidence } from '../hooks';

/**
 * Evidence View Page
 * 
 * Review extracted evidence from processed documents.
 * Displays text, images, and tables in tabbed views.
 */
function EvidenceViewPage() {
  const navigate = useNavigate();
  const { activeTab, setActiveTab, evidence, tabs } = useEvidence();

  /**
   * Navigate to next page
   */
  const handleContinue = () => {
    navigate('/narrative');
  };

  /**
   * Navigate back
   */
  const handleBack = () => {
    navigate('/criteria');
  };

  return (
    <div>
      {/* Page Header */}
      <div className="page-header">
        <h1 className="page-header__title">Evidence View</h1>
        <p className="page-header__description">
          Review the extracted evidence from your documents. Evidence is categorized by type.
        </p>
      </div>

      {/* Evidence Statistics */}
      <Card style={{ marginBottom: '24px' }}>
        <div className="stats-grid">
          <div className="stat-card">
            <div className="stat-card__label">Text Extracts</div>
            <div className="stat-card__value">5</div>
          </div>
          <div className="stat-card">
            <div className="stat-card__label">Images</div>
            <div className="stat-card__value">3</div>
          </div>
          <div className="stat-card">
            <div className="stat-card__label">Tables</div>
            <div className="stat-card__value">3</div>
          </div>
          <div className="stat-card">
            <div className="stat-card__label">Source Files</div>
            <div className="stat-card__value">8</div>
          </div>
        </div>
      </Card>

      {/* Evidence Viewer with Tabs */}
      <Card title="Extracted Evidence">
        <Tabs 
          tabs={tabs} 
          activeTab={activeTab} 
          onTabChange={setActiveTab} 
        />
        <div className="tabs__content">
          <EvidenceViewer items={evidence} type={activeTab} />
        </div>
      </Card>

      {/* Navigation Buttons */}
      <Card style={{ marginTop: '24px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between' }}>
          <Button variant="secondary" onClick={handleBack}>
            ← Back to Criteria
          </Button>
          <Button variant="primary" onClick={handleContinue}>
            Continue to Narrative Editor →
          </Button>
        </div>
      </Card>

      {/* Help Section */}
      <Card title="About Evidence View" style={{ marginTop: '24px' }}>
        <div className="text-sm" style={{ color: 'var(--color-gray-600)' }}>
          <p style={{ marginBottom: '12px' }}>
            This page displays all evidence extracted from your uploaded documents:
          </p>
          <ul style={{ paddingLeft: '20px', lineHeight: '1.8' }}>
            <li><strong>Text Evidence:</strong> Relevant text passages extracted from documents that support NAAC criteria.</li>
            <li><strong>Images:</strong> Charts, graphs, photographs, and other visual elements that provide supporting evidence.</li>
            <li><strong>Tables:</strong> Data tables containing statistics, metrics, and structured information.</li>
          </ul>
          <p style={{ marginTop: '12px' }}>
            Each evidence item shows the source file name and page number for reference.
          </p>
        </div>
      </Card>
    </div>
  );
}

export default EvidenceViewPage;
