/**
 * Card Component
 * 
 * A versatile container component for content sections.
 * Provides consistent styling with optional header and footer.
 * 
 * @param {Object} props
 * @param {string} props.title - Optional card title
 * @param {string} props.subtitle - Optional card subtitle
 * @param {React.ReactNode} props.children - Card body content
 * @param {React.ReactNode} props.footer - Optional footer content
 * @param {string} props.className - Additional CSS classes
 */
function Card({ title, subtitle, children, footer, className = '' }) {
  return (
    <div className={`card ${className}`}>
      {/* Card Header - only rendered if title is provided */}
      {title && (
        <div className="card__header">
          <h3 className="card__title">{title}</h3>
          {subtitle && <p className="card__subtitle">{subtitle}</p>}
        </div>
      )}
      
      {/* Card Body */}
      <div className="card__body">
        {children}
      </div>
      
      {/* Card Footer - only rendered if footer content is provided */}
      {footer && (
        <div className="card__footer">
          {footer}
        </div>
      )}
    </div>
  );
}

export default Card;
