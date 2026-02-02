import { useRef } from 'react';

/**
 * ExcelUpload Component
 * 
 * Drag-and-drop file upload for Excel files (.xlsx, .xls)
 */
function ExcelUpload({ onFileSelected, disabled = false, currentFile = null }) {
  const fileInputRef = useRef(null);

  const handleDragOver = (e) => {
    e.preventDefault();
    e.stopPropagation();
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    
    if (disabled) return;
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
      const file = files[0];
      if (isExcelFile(file)) {
        onFileSelected(file);
      }
    }
  };

  const handleClick = () => {
    if (!disabled && fileInputRef.current) {
      fileInputRef.current.click();
    }
  };

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file && isExcelFile(file)) {
      onFileSelected(file);
    }
  };

  const isExcelFile = (file) => {
    const validTypes = [
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
      'application/vnd.ms-excel'
    ];
    const validExtensions = ['.xlsx', '.xls'];
    
    return validTypes.includes(file.type) || 
           validExtensions.some(ext => file.name.toLowerCase().endsWith(ext));
  };

  return (
    <div
      className={`file-upload ${disabled ? 'file-upload--disabled' : ''}`}
      onDragOver={handleDragOver}
      onDrop={handleDrop}
      onClick={handleClick}
    >
      <input
        ref={fileInputRef}
        type="file"
        accept=".xlsx,.xls"
        onChange={handleFileChange}
        style={{ display: 'none' }}
        disabled={disabled}
      />
      
      <div className="file-upload__icon">📊</div>
      
      {currentFile ? (
        <div className="file-upload__content">
          <p className="file-upload__text">
            <strong>{currentFile.name}</strong>
          </p>
          <p className="file-upload__hint">Click to replace file</p>
        </div>
      ) : (
        <div className="file-upload__content">
          <p className="file-upload__text">
            Drag and drop an Excel file here, or <span className="file-upload__link">browse</span>
          </p>
          <p className="file-upload__hint">Supports .xlsx and .xls files</p>
        </div>
      )}
    </div>
  );
}

export default ExcelUpload;
