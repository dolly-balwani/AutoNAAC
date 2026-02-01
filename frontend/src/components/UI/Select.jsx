/**
 * Select Component
 * 
 * Styled dropdown select input.
 * 
 * @param {Object} props
 * @param {string} props.label - Form label text
 * @param {string} props.value - Current selected value
 * @param {Function} props.onChange - Change handler
 * @param {Array} props.options - Array of { value, label } objects
 * @param {boolean} props.disabled - Disabled state
 * @param {string} props.placeholder - Placeholder text
 * @param {boolean} props.required - Required field indicator
 */
function Select({
  label,
  value,
  onChange,
  options = [],
  disabled = false,
  placeholder = 'Select an option',
  required = false
}) {
  return (
    <div className="form-group">
      {label && (
        <label className={`form-label ${required ? 'form-label--required' : ''}`}>
          {label}
        </label>
      )}
      <select
        className="form-input form-select"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        disabled={disabled}
      >
        <option value="">{placeholder}</option>
        {options.map((option) => (
          <option key={option.value} value={option.value}>
            {option.label}
          </option>
        ))}
      </select>
    </div>
  );
}

export default Select;
