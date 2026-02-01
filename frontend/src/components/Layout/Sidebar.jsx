import { NavLink, useLocation } from 'react-router-dom';
import { useProcessing } from '../../hooks/useProcessing.js';

/**
 * Sidebar Component
 * 
 * Left navigation panel with links to all major sections.
 * Disables navigation during processing to prevent interruption.
 */
function Sidebar() {
  const location = useLocation();
  const { isProcessing } = useProcessing();

  // Navigation items configuration
  const navItems = [
    { path: '/sources', label: 'Sources', icon: '📁', description: 'Upload documents' },
    { path: '/processing', label: 'Processing', icon: '⚙️', description: 'View progress' },
    { path: '/criteria', label: 'Criteria', icon: '📋', description: 'Select NAAC criteria' },
    { path: '/evidence', label: 'Evidence View', icon: '🔍', description: 'Review extracted data' },
    { path: '/narrative', label: 'Narrative Editor', icon: '✏️', description: 'Edit report content' },
    { path: '/export', label: 'Export', icon: '📤', description: 'Download reports' }
  ];

  /**
   * Determines if a navigation link should be disabled
   * Navigation is disabled during processing except for the processing page
   */
  const isNavDisabled = (path) => {
    if (!isProcessing) return false;
    return path !== '/processing';
  };

  return (
    <aside className="sidebar">
      {/* Brand/Logo Section */}
      <div className="sidebar__brand">
        <div className="sidebar__logo">
          <div className="sidebar__logo-icon">N</div>
          <span className="sidebar__logo-text">NAAC</span>
        </div>
      </div>

      {/* Navigation Links */}
      <nav className="sidebar__nav">
        <ul className="sidebar__nav-list">
          {navItems.map((item) => (
            <li key={item.path} className="sidebar__nav-item">
              <NavLink
                to={item.path}
                className={({ isActive }) => {
                  let classes = 'sidebar__nav-link';
                  if (isActive) classes += ' sidebar__nav-link--active';
                  if (isNavDisabled(item.path)) classes += ' sidebar__nav-link--disabled';
                  return classes;
                }}
                onClick={(e) => {
                  if (isNavDisabled(item.path)) {
                    e.preventDefault();
                  }
                }}
              >
                <span className="sidebar__nav-icon">{item.icon}</span>
                <span>{item.label}</span>
              </NavLink>
            </li>
          ))}
        </ul>
      </nav>

      {/* Footer */}
      <div className="sidebar__footer">
        <p>NAAC Automation System</p>
        <p>Version 1.0.0</p>
      </div>
    </aside>
  );
}

export default Sidebar;
