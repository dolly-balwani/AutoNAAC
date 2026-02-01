/**
 * Badge Component
 * 
 * Small status indicator label.
 * 
 * @param {Object} props
 * @param {React.ReactNode} props.children - Badge content
 * @param {string} props.variant - Color variant: 'success' | 'warning' | 'error' | 'info' | 'neutral'
 */
function Badge({ children, variant = 'neutral' }) {
  return (
    <span className={`badge badge--${variant}`}>
      {children}
    </span>
  );
}

export default Badge;
