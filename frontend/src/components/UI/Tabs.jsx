/**
 * Tabs Component
 * 
 * Tab navigation for switching between content panels.
 * 
 * @param {Object} props
 * @param {Array} props.tabs - Array of { id, label } objects
 * @param {string} props.activeTab - Currently active tab ID
 * @param {Function} props.onTabChange - Tab change handler
 */
function Tabs({ tabs, activeTab, onTabChange }) {
  return (
    <div className="tabs">
      <ul className="tabs__list">
        {tabs.map((tab) => (
          <li
            key={tab.id}
            className={`tabs__tab ${activeTab === tab.id ? 'tabs__tab--active' : ''}`}
            onClick={() => onTabChange(tab.id)}
          >
            {tab.label}
          </li>
        ))}
      </ul>
    </div>
  );
}

export default Tabs;
