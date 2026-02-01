import { Button } from '../UI';

/**
 * FileList Component
 * 
 * Displays list of uploaded files with remove functionality.
 * 
 * @param {Object} props
 * @param {Array} props.files - Array of file objects
 * @param {Function} props.onRemove - Callback to remove a file by index
 */
function FileList({ files = [], onRemove }) {
  /**
   * Format file size to human readable format
   */
  const formatSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  /**
   * Get file type icon based on extension
   */
  const getFileIcon = (fileName) => {
    const ext = fileName.split('.').pop().toLowerCase();
    const icons = {
      pdf: 'PDF',
      docx: 'DOC',
      doc: 'DOC',
      pptx: 'PPT',
      ppt: 'PPT',
      png: 'IMG',
      jpg: 'IMG',
      jpeg: 'IMG',
      gif: 'IMG'
    };
    return icons[ext] || 'FILE';
  };

  if (files.length === 0) {
    return null;
  }

  return (
    <ul className="file-list">
      {files.map((file, index) => (
        <li key={`${file.name}-${index}`} className="file-list__item">
          <div className="file-list__info">
            <div className="file-list__icon">
              {getFileIcon(file.name)}
            </div>
            <div>
              <div className="file-list__name">{file.name}</div>
              <div className="file-list__size">{formatSize(file.size)}</div>
            </div>
          </div>
          <button 
            className="file-list__remove"
            onClick={() => onRemove(index)}
            title="Remove file"
          >
            ✕
          </button>
        </li>
      ))}
    </ul>
  );
}

export default FileList;
