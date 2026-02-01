import { useState, useEffect } from 'react';
import { Button, Checkbox } from '../UI';

/**
 * SubCriteriaDrawer Component
 * 
 * Right-side drawer showing sub-criteria for a selected criterion.
 * 
 * @param {Object} props
 * @param {boolean} props.isOpen - Whether drawer is open
 * @param {Function} props.onClose - Close handler
 * @param {Object} props.criterion - Selected criterion object
 * @param {Array} props.selectedSubCriteria - Currently selected sub-criteria IDs
 * @param {Function} props.onSelectionChange - Handler for selection changes
 */
function SubCriteriaDrawer({ 
  isOpen, 
  onClose, 
  criterion, 
  selectedSubCriteria = [],
  onSelectionChange 
}) {
  const [localSelection, setLocalSelection] = useState([]);

  // Sync local selection with props
  useEffect(() => {
    setLocalSelection(selectedSubCriteria);
  }, [selectedSubCriteria, criterion]);

  if (!isOpen || !criterion) return null;

  /**
   * Handle individual sub-criteria toggle
   */
  const handleToggle = (subCriteriaId) => {
    const newSelection = localSelection.includes(subCriteriaId)
      ? localSelection.filter(id => id !== subCriteriaId)
      : [...localSelection, subCriteriaId];
    setLocalSelection(newSelection);
  };

  /**
   * Handle select all toggle
   */
  const handleSelectAll = () => {
    if (localSelection.length === criterion.subCriteria.length) {
      setLocalSelection([]);
    } else {
      setLocalSelection(criterion.subCriteria.map(sc => sc.id));
    }
  };

  /**
   * Save selections
   */
  const handleSave = () => {
    onSelectionChange(criterion.id, localSelection);
    onClose();
  };

  const allSelected = criterion.subCriteria.length > 0 && 
    localSelection.length === criterion.subCriteria.length;

  return (
    <>
      {/* Overlay */}
      <div className="drawer-overlay" onClick={onClose} />
      
      {/* Drawer */}
      <div className="drawer">
        <div className="drawer__header">
          <h3 className="drawer__title">
            Criterion {criterion.id}: {criterion.name}
          </h3>
          <button className="drawer__close" onClick={onClose}>✕</button>
        </div>
        
        <div className="drawer__body">
          {/* Select All Option */}
          <div style={{ marginBottom: '16px', paddingBottom: '16px', borderBottom: '1px solid var(--color-gray-200)' }}>
            <Checkbox
              id="select-all-sub"
              label="Select All Sub-Criteria"
              checked={allSelected}
              onChange={handleSelectAll}
            />
          </div>
          
          {/* Sub-criteria List */}
          <ul className="subcriteria-list">
            {criterion.subCriteria.map((subCriteria) => (
              <li key={subCriteria.id} className="subcriteria-item">
                <Checkbox
                  id={`sub-${subCriteria.id}`}
                  label={`${subCriteria.id} - ${subCriteria.name}`}
                  checked={localSelection.includes(subCriteria.id)}
                  onChange={() => handleToggle(subCriteria.id)}
                />
              </li>
            ))}
          </ul>
        </div>
        
        <div className="drawer__footer">
          <div className="btn-group">
            <Button variant="secondary" onClick={onClose}>
              Cancel
            </Button>
            <Button variant="primary" onClick={handleSave}>
              Save Selection
            </Button>
          </div>
        </div>
      </div>
    </>
  );
}

export default SubCriteriaDrawer;
