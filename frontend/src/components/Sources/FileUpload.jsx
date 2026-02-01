import { useRef, useState } from 'react';

/**
 * FileUpload Component
 * 
 * Drag and drop file upload area with file type filtering.
 * 
 * @param {Object} props
 * @param {Function} props.onFilesSelected - Callback when files are selected
 * @param {Array} props.acceptedTypes - Array of accepted file extensions (e.g., ['.pdf', '.docx'])
 * @param {boolean} props.multiple - Allow multiple file selection
 * @param {boolean} props.disabled - Disabled state
 */
function FileUpload({ 
  onFilesSelected, 
  acceptedTypes = [], 
  multiple = true,
  disabled = false 
}) {
  const [isDragOver, setIsDragOver] = useState(false);
  const inputRef = useRef(null);

  // Generate accept string for input
  const acceptString = acceptedTypes.join(',');

  /**
   * Handle file selection from input or drop
   */
  const handleFiles = (files) => {
    if (disabled) return;
    
    const fileArray = Array.from(files);
    
    // Filter by accepted types if specified
    const filteredFiles = acceptedTypes.length > 0
      ? fileArray.filter(file => {
          const ext = '.' + file.name.split('.').pop().toLowerCase();
          return acceptedTypes.includes(ext);
        })
      : fileArray;
    
    if (filteredFiles.length > 0) {
      onFilesSelected(filteredFiles);
    }
  };

  /**
   * Handle drag over event
   */
  const handleDragOver = (e) => {
    e.preventDefault();
    if (!disabled) {
      setIsDragOver(true);
    }
  };

  /**
   * Handle drag leave event
   */
  const handleDragLeave = (e) => {
    e.preventDefault();
    setIsDragOver(false);
  };

  /**
   * Handle file drop event
   */
  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragOver(false);
    if (!disabled && e.dataTransfer.files) {
      handleFiles(e.dataTransfer.files);
    }
  };

  /**
   * Handle input change event
   */
  const handleInputChange = (e) => {
    if (e.target.files) {
      handleFiles(e.target.files);
    }
    // Reset input to allow selecting the same file again
    e.target.value = '';
  };

  /**
   * Trigger file input click
   */
  const handleClick = () => {
    if (!disabled && inputRef.current) {
      inputRef.current.click();
    }
  };

  const className = [
    'file-upload',
    isDragOver ? 'file-upload--drag-over' : '',
    disabled ? 'file-upload--disabled' : ''
  ].filter(Boolean).join(' ');

  return (
    <div
      className={className}
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
      onClick={handleClick}
      style={{ opacity: disabled ? 0.5 : 1, cursor: disabled ? 'not-allowed' : 'pointer' }}
    >
      <input
        ref={inputRef}
        type="file"
        className="file-upload__input"
        accept={acceptString}
        multiple={multiple}
        onChange={handleInputChange}
        disabled={disabled}
      />
      <div className="file-upload__icon">📄</div>
      <p className="file-upload__text">
        Drag and drop files here, or click to browse
      </p>
      <p className="file-upload__hint">
        {acceptedTypes.length > 0 
          ? `Accepted formats: ${acceptedTypes.join(', ')}`
          : 'All file types accepted'
        }
      </p>
    </div>
  );
}

export default FileUpload;
