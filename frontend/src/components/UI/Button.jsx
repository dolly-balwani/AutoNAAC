/**
 * Button Component
 * 
 * Reusable button with multiple variants and sizes.
 * 
 * @param {Object} props
 * @param {React.ReactNode} props.children - Button content
 * @param {string} props.variant - Button style: 'primary' | 'secondary' | 'success' | 'danger'
 * @param {string} props.size - Button size: 'sm' | 'md' | 'lg'
 * @param {boolean} props.block - Full width button
 * @param {boolean} props.disabled - Disabled state
 * @param {string} props.type - HTML button type
 * @param {Function} props.onClick - Click handler
 * @param {string} props.className - Additional CSS classes
 */
function Button({
  children,
  variant = 'primary',
  size = 'md',
  block = false,
  disabled = false,
  type = 'button',
  onClick,
  className = ''
}) {
  const classes = [
    'btn',
    `btn--${variant}`,
    size !== 'md' ? `btn--${size}` : '',
    block ? 'btn--block' : '',
    className
  ].filter(Boolean).join(' ');

  return (
    <button
      type={type}
      className={classes}
      disabled={disabled}
      onClick={onClick}
    >
      {children}
    </button>
  );
}

export default Button;
