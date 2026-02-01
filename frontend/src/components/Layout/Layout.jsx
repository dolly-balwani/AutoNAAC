import { Outlet } from 'react-router-dom';
import Sidebar from './Sidebar.jsx';
import Header from './Header.jsx';

/**
 * Layout Component
 * 
 * Main layout wrapper that provides consistent structure across all pages.
 * Includes the sidebar navigation and header.
 */
function Layout() {
  return (
    <div className="layout">
      <Sidebar />
      <div className="layout__main">
        <Header />
        <main className="layout__content">
          <Outlet />
        </main>
      </div>
    </div>
  );
}

export default Layout;
