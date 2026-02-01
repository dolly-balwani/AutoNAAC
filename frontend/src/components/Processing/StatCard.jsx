/**
 * StatCard Component
 * 
 * Displays a single statistic with label and value.
 * 
 * @param {Object} props
 * @param {string} props.label - Stat label
 * @param {string|number} props.value - Stat value
 * @param {string} props.variant - Color variant: 'default' | 'success' | 'error'
 */
function StatCard({ label, value, variant = 'default' }) {
  const valueClass = variant !== 'default' ? `stat-card__value--${variant}` : '';
  
  return (
    <div className="stat-card">
      <div className="stat-card__label">{label}</div>
      <div className={`stat-card__value ${valueClass}`}>{value}</div>
    </div>
  );
}

export default StatCard;
