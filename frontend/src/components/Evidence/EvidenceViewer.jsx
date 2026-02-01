/**
 * EvidenceViewer Component
 * 
 * Scrollable panel displaying extracted evidence items.
 * 
 * @param {Object} props
 * @param {Array} props.items - Array of evidence items
 * @param {string} props.type - Type of evidence: 'text' | 'images' | 'tables'
 */
function EvidenceViewer({ items = [], type = 'text' }) {
  if (items.length === 0) {
    return (
      <div className="empty-state">
        <div className="empty-state__icon">📭</div>
        <h3 className="empty-state__title">No Evidence Found</h3>
        <p className="empty-state__description">
          No {type} evidence has been extracted yet.
        </p>
      </div>
    );
  }

  return (
    <div className="evidence-viewer">
      {items.map((item, index) => (
        <div key={index} className="evidence-item">
          {/* Source Information */}
          <div className="evidence-item__source">
            <span>📄 {item.sourceFile}</span>
            <span>•</span>
            <span>Page {item.pageNumber}</span>
          </div>
          
          {/* Content based on type */}
          {type === 'text' && (
            <p className="evidence-item__content">{item.content}</p>
          )}
          
          {type === 'images' && (
            <img 
              src={item.content} 
              alt={item.description || 'Evidence image'}
              className="evidence-item__image"
            />
          )}
          
          {type === 'tables' && (
            <table className="evidence-table">
              <thead>
                <tr>
                  {item.headers.map((header, i) => (
                    <th key={i}>{header}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {item.rows.map((row, rowIndex) => (
                  <tr key={rowIndex}>
                    {row.map((cell, cellIndex) => (
                      <td key={cellIndex}>{cell}</td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      ))}
    </div>
  );
}

export default EvidenceViewer;
