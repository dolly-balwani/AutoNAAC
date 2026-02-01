import { useNavigate } from 'react-router-dom';
import { Card, Button, Badge } from '../components/UI';
import { TextEditor } from '../components/Narrative';
import { useNarrative } from '../hooks';

/**
 * Narrative Editor Page
 * 
 * Edit and refine AI-generated narrative content for the NAAC report.
 */
function NarrativeEditorPage() {
  const navigate = useNavigate();
  const {
    content,
    isLoading,
    isSaved,
    lastSaved,
    updateContent,
    regenerate,
    improve,
    save
  } = useNarrative();

  /**
   * Navigate to next page
   */
  const handleContinue = () => {
    navigate('/export');
  };

  /**
   * Navigate back
   */
  const handleBack = () => {
    navigate('/evidence');
  };

  return (
    <div>
      {/* Page Header */}
      <div className="page-header">
        <h1 className="page-header__title">Narrative Editor</h1>
        <p className="page-header__description">
          Review and edit the AI-generated narrative content for your NAAC report.
        </p>
      </div>

      {/* Status Bar */}
      <Card style={{ marginBottom: '24px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
            <Badge variant={isSaved ? 'success' : 'warning'}>
              {isSaved ? 'Saved' : 'Unsaved Changes'}
            </Badge>
            {lastSaved && (
              <span className="text-sm text-muted">
                Last saved: {lastSaved}
              </span>
            )}
          </div>
          {isLoading && (
            <span className="text-sm text-muted">
              Processing...
            </span>
          )}
        </div>
      </Card>

      {/* Text Editor */}
      <Card 
        title="Report Narrative" 
        subtitle="Edit the content below or use the action buttons to regenerate/improve"
      >
        <TextEditor
          content={content}
          onChange={updateContent}
          onRegenerate={regenerate}
          onImprove={improve}
          onSave={save}
          isLoading={isLoading}
        />
      </Card>

      {/* Navigation Buttons */}
      <Card style={{ marginTop: '24px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between' }}>
          <Button variant="secondary" onClick={handleBack}>
            ← Back to Evidence
          </Button>
          <Button 
            variant="primary" 
            onClick={handleContinue}
            disabled={!isSaved}
          >
            Continue to Export →
          </Button>
        </div>
        {!isSaved && (
          <p className="text-sm text-warning" style={{ marginTop: '12px', textAlign: 'right' }}>
            Please save your changes before continuing.
          </p>
        )}
      </Card>

      {/* Help Section */}
      <Card title="Editor Instructions" style={{ marginTop: '24px' }}>
        <div className="text-sm" style={{ color: 'var(--color-gray-600)' }}>
          <ul style={{ paddingLeft: '20px', lineHeight: '1.8' }}>
            <li><strong>Edit:</strong> Directly modify the text in the editor area.</li>
            <li><strong>Regenerate:</strong> Generate a completely new narrative based on the extracted evidence.</li>
            <li><strong>Improve:</strong> Enhance the current content with additional details and better phrasing.</li>
            <li><strong>Save:</strong> Save your current edits before proceeding to export.</li>
          </ul>
          <p style={{ marginTop: '12px' }}>
            The word and character count are displayed below the editor for reference.
          </p>
        </div>
      </Card>
    </div>
  );
}

export default NarrativeEditorPage;
