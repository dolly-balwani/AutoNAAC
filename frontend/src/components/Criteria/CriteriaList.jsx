import { Checkbox } from '../UI';

/**
 * CriteriaList Component
 * 
 * Displays the list of NAAC criteria with click handlers.
 * 
 * @param {Object} props
 * @param {Array} props.criteria - Array of criteria objects
 * @param {Function} props.onCriteriaClick - Handler when a criterion is clicked
 * @param {boolean} props.disabled - Whether the list is disabled
 */
function CriteriaList({ criteria = [], onCriteriaClick, disabled = false }) {
  return (
    <ul className="criteria-list">
      {criteria.map((criterion) => (
        <li
          key={criterion.id}
          className={`criteria-item ${disabled ? 'criteria-item--disabled' : ''}`}
          onClick={() => !disabled && onCriteriaClick(criterion)}
        >
          <div className="criteria-item__info">
            <span className="criteria-item__code">Criterion {criterion.id}</span>
            <span className="criteria-item__name">{criterion.name}</span>
          </div>
          <span className="criteria-item__arrow">→</span>
        </li>
      ))}
    </ul>
  );
}

export default CriteriaList;
