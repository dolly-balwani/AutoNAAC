import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, Button, Checkbox, Badge } from '../components/UI';
import { CriteriaList, SubCriteriaDrawer } from '../components/Criteria';
import { useCriteria } from '../hooks';

/**
 * Criteria Page
 * 
 * Select NAAC criteria and sub-criteria for report generation.
 */
function CriteriaPage() {
  const navigate = useNavigate();
  const {
    criteria,
    selectAll,
    toggleSelectAll,
    updateCriteriaSelection,
    getSelectedSubCriteria,
    getTotalSelected,
    hasSelection
  } = useCriteria();

  // Drawer state
  const [isDrawerOpen, setIsDrawerOpen] = useState(false);
  const [selectedCriterion, setSelectedCriterion] = useState(null);

  /**
   * Handle criterion click to open drawer
   */
  const handleCriteriaClick = (criterion) => {
    if (selectAll) return; // Disabled when all selected
    setSelectedCriterion(criterion);
    setIsDrawerOpen(true);
  };

  /**
   * Handle drawer close
   */
  const handleDrawerClose = () => {
    setIsDrawerOpen(false);
    setSelectedCriterion(null);
  };

  /**
   * Handle sub-criteria selection change
   */
  const handleSelectionChange = (criterionId, subCriteriaIds) => {
    updateCriteriaSelection(criterionId, subCriteriaIds);
  };

  /**
   * Navigate to next page
   */
  const handleContinue = () => {
    navigate('/evidence');
  };

  /**
   * Navigate back
   */
  const handleBack = () => {
    navigate('/processing');
  };

  return (
    <div>
      {/* Page Header */}
      <div className="page-header">
        <h1 className="page-header__title">Select NAAC Criteria</h1>
        <p className="page-header__description">
          Choose the criteria and sub-criteria to include in your accreditation report.
        </p>
      </div>

      {/* Selection Summary */}
      <Card style={{ marginBottom: '24px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div>
            <Checkbox
              id="select-all"
              label="Select All Criteria (include everything)"
              checked={selectAll}
              onChange={toggleSelectAll}
            />
            {selectAll && (
              <p className="text-sm text-muted" style={{ marginTop: '8px', marginLeft: '26px' }}>
                All criteria and sub-criteria will be included in the report.
              </p>
            )}
          </div>
          <div style={{ textAlign: 'right' }}>
            <Badge variant={hasSelection ? 'success' : 'neutral'}>
              {getTotalSelected()} sub-criteria selected
            </Badge>
          </div>
        </div>
      </Card>

      {/* Criteria List */}
      <Card 
        title="NAAC Criteria" 
        subtitle={selectAll ? 'All criteria selected' : 'Click on a criterion to select sub-criteria'}
      >
        <CriteriaList
          criteria={criteria}
          onCriteriaClick={handleCriteriaClick}
          disabled={selectAll}
        />
      </Card>

      {/* Selection Details */}
      {!selectAll && hasSelection && (
        <Card 
          title="Selected Criteria Summary" 
          style={{ marginTop: '24px' }}
        >
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
            {criteria.map((criterion) => {
              const selected = getSelectedSubCriteria(criterion.id);
              if (selected.length === 0) return null;
              return (
                <div 
                  key={criterion.id}
                  style={{ 
                    padding: '8px 12px', 
                    backgroundColor: 'var(--color-gray-100)',
                    borderRadius: '8px',
                    fontSize: '14px'
                  }}
                >
                  <strong>Criterion {criterion.id}:</strong> {selected.length} sub-criteria
                </div>
              );
            })}
          </div>
        </Card>
      )}

      {/* Navigation Buttons */}
      <Card style={{ marginTop: '24px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between' }}>
          <Button variant="secondary" onClick={handleBack}>
            ← Back to Processing
          </Button>
          <Button 
            variant="primary" 
            onClick={handleContinue}
            disabled={!hasSelection}
          >
            Continue to Evidence →
          </Button>
        </div>
      </Card>

      {/* Help Section */}
      <Card title="Instructions" style={{ marginTop: '24px' }}>
        <div className="text-sm" style={{ color: 'var(--color-gray-600)' }}>
          <ul style={{ paddingLeft: '20px', lineHeight: '1.8' }}>
            <li><strong>Select All:</strong> Check "Select All Criteria" to include all criteria and sub-criteria in your report.</li>
            <li><strong>Individual Selection:</strong> Click on a criterion to open the sub-criteria drawer and select specific items.</li>
            <li><strong>Sub-criteria:</strong> Each criterion contains multiple sub-criteria (e.g., 5.1.1, 5.1.2). Select only what you need.</li>
            <li><strong>Review:</strong> Your selections are summarized at the bottom before proceeding.</li>
          </ul>
        </div>
      </Card>

      {/* Sub-criteria Drawer */}
      <SubCriteriaDrawer
        isOpen={isDrawerOpen}
        onClose={handleDrawerClose}
        criterion={selectedCriterion}
        selectedSubCriteria={selectedCriterion ? getSelectedSubCriteria(selectedCriterion.id) : []}
        onSelectionChange={handleSelectionChange}
      />
    </div>
  );
}

export default CriteriaPage;
