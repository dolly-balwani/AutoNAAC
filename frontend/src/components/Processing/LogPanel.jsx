/**
 * LogPanel Component
 * 
 * Displays live processing logs with timestamps and color coding.
 * 
 * @param {Object} props
 * @param {Array} props.logs - Array of log entries { time, message, type }
 */
function LogPanel({ logs = [] }) {
  return (
    <div className="log-panel">
      {logs.length === 0 ? (
        <div className="log-panel__entry">
          <span className="log-panel__message">Waiting for processing to start...</span>
        </div>
      ) : (
        logs.map((log, index) => (
          <div key={index} className="log-panel__entry">
            <span className="log-panel__time">[{log.time}]</span>
            <span className={`log-panel__message log-panel__message--${log.type || 'info'}`}>
              {log.message}
            </span>
          </div>
        ))
      )}
    </div>
  );
}

export default LogPanel;
