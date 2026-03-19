/**
 * CriteriaSelector Component
 * 
 * Dropdown to select NAAC criterion from available options
 */
function CriteriaSelector({ 
  criteria = [], 
  selected = '', 
  onChange, 
  disabled = false,
  loading = false 
}) {
  if (loading) {
    return (
      <div className="criteria-selector criteria-selector--loading">
        <span className="criteria-selector__spinner">⏳</span>
        <span>Loading criteria...</span>
      </div>
    );
  }

  if (criteria.length === 0) {
    return (
      <div className="criteria-selector criteria-selector--empty">
        <span className="text-muted">No criteria found in the uploaded Excel file</span>
      </div>
    );
  }

  return (
    <div className="criteria-selector">
      <label className="criteria-selector__label">Select NAAC Criterion</label>
      <select
        className="criteria-selector__select"
        value={selected}
        onChange={(e) => onChange(e.target.value)}
        disabled={disabled}
      >
        <option value="">-- Select a criterion --</option>
        {criteria.map((criterion) => (
          <option key={criterion} value={criterion}>
            Criterion {criterion}
          </option>
        ))}
      </select>
      {selected && (
        <p className="criteria-selector__hint">
          Report will be generated for <strong>Criterion {selected}</strong>
        </p>
      )}
    </div>
  );
}

export default CriteriaSelector;
