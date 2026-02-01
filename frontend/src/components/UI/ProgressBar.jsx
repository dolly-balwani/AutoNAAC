/**
 * ProgressBar Component
 * 
 * Visual progress indicator with percentage display.
 * 
 * @param {Object} props
 * @param {number} props.value - Current progress (0-100)
 * @param {string} props.variant - Color variant: 'default' | 'success' | 'warning' | 'error'
 * @param {boolean} props.showLabel - Show percentage label
 * @param {string} props.size - Bar size: 'md' | 'lg'
 */
function ProgressBar({ 
  value = 0, 
  variant = 'default', 
  showLabel = true,
  size = 'md'
}) {
  // Ensure value is between 0 and 100
  const normalizedValue = Math.min(100, Math.max(0, value));
  
  const barClass = variant !== 'default' ? `progress__bar--${variant}` : '';
  const sizeClass = size === 'lg' ? 'progress--lg' : '';

  return (
    <div>
      {showLabel && (
        <div className="text-sm text-muted" style={{ marginBottom: '8px' }}>
          {normalizedValue}% Complete
        </div>
      )}
      <div className={`progress ${sizeClass}`}>
        <div 
          className={`progress__bar ${barClass}`}
          style={{ width: `${normalizedValue}%` }}
        />
      </div>
    </div>
  );
}

export default ProgressBar;
