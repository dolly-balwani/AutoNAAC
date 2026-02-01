import { useLocation } from 'react-router-dom';

/**
 * Header Component
 * 
 * Top header bar displaying the current page title and system information.
 */
function Header() {
  const location = useLocation();

  // Map routes to page titles
  const pageTitles = {
    '/sources': 'Upload Sources',
    '/processing': 'Processing Documents',
    '/criteria': 'Select Criteria',
    '/evidence': 'Evidence View',
    '/narrative': 'Narrative Editor',
    '/export': 'Export Report'
  };

  const currentTitle = pageTitles[location.pathname] || 'NAAC Automation';

  return (
    <header className="header">
      <div>
        <h1 className="header__title">{currentTitle}</h1>
        <span className="header__subtitle">Institutional Accreditation Management</span>
      </div>
      <div className="header__actions">
        <span className="text-sm text-muted">Academic Year: 2024-25</span>
      </div>
    </header>
  );
}

export default Header;
