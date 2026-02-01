import { Button, Badge } from '../UI';

/**
 * ExportCard Component
 * 
 * Card for export options with status indicator.
 * 
 * @param {Object} props
 * @param {string} props.icon - Icon to display
 * @param {string} props.title - Export format title
 * @param {string} props.description - Format description
 * @param {Function} props.onExport - Export button handler
 * @param {string} props.status - Export status: 'ready' | 'generating' | 'completed' | 'error'
 * @param {boolean} props.disabled - Disabled state
 */
function ExportCard({ 
  icon, 
  title, 
  description, 
  onExport, 
  status = 'ready',
  disabled = false 
}) {
  const statusConfig = {
    ready: { label: 'Ready', variant: 'neutral' },
    generating: { label: 'Generating...', variant: 'warning' },
    completed: { label: 'Completed', variant: 'success' },
    error: { label: 'Error', variant: 'error' }
  };

  const currentStatus = statusConfig[status] || statusConfig.ready;

  return (
    <div className="export-card">
      <div className="export-card__icon">{icon}</div>
      <h3 className="export-card__title">{title}</h3>
      <p className="export-card__description">{description}</p>
      
      <div style={{ marginBottom: '16px' }}>
        <Badge variant={currentStatus.variant}>{currentStatus.label}</Badge>
      </div>
      
      <Button 
        variant="primary" 
        block 
        onClick={onExport}
        disabled={disabled || status === 'generating'}
      >
        {status === 'generating' ? 'Generating...' : 'Download'}
      </Button>
    </div>
  );
}

export default ExportCard;
