/**
 * Checkbox Component
 * 
 * Styled checkbox input with label.
 * 
 * @param {Object} props
 * @param {string} props.label - Checkbox label text
 * @param {boolean} props.checked - Checked state
 * @param {Function} props.onChange - Change handler
 * @param {boolean} props.disabled - Disabled state
 * @param {string} props.id - Unique identifier
 */
function Checkbox({ label, checked, onChange, disabled = false, id }) {
  const handleChange = (e) => {
    onChange(e.target.checked);
  };

  return (
    <label className="checkbox" htmlFor={id}>
      <input
        type="checkbox"
        id={id}
        className="checkbox__input"
        checked={checked}
        onChange={handleChange}
        disabled={disabled}
      />
      <span className="checkbox__label">{label}</span>
    </label>
  );
}

export default Checkbox;
