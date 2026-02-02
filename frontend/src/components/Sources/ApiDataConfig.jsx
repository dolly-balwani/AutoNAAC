/**
 * ApiDataConfig Component
 * 
 * Configuration for API data source (placeholder for future implementation)
 */
function ApiDataConfig() {
  return (
    <div className="api-config">
      <div className="api-config__placeholder">
        <span className="api-config__icon">🔌</span>
        <h3 className="api-config__title">API Data Source</h3>
        <p className="api-config__description">
          Connect to external APIs to fetch NAAC data automatically.
        </p>
        <div className="api-config__coming-soon">
          <span className="badge badge--info">Coming Soon</span>
        </div>
        <p className="api-config__hint">
          This feature will allow you to connect to your institution's data systems 
          and automatically pull evidence for NAAC accreditation.
        </p>
      </div>
    </div>
  );
}

export default ApiDataConfig;
