import { useState, useCallback } from 'react';

/**
 * useFileUpload Hook
 * 
 * Manages file upload state and operations.
 * 
 * @returns {Object} File upload state and methods
 */
export function useFileUpload() {
  const [files, setFiles] = useState([]);
  const [processingMode, setProcessingMode] = useState('');

  /**
   * Add files to the upload list
   */
  const addFiles = useCallback((newFiles) => {
    setFiles(prev => [...prev, ...newFiles]);
  }, []);

  /**
   * Remove a file by index
   */
  const removeFile = useCallback((index) => {
    setFiles(prev => prev.filter((_, i) => i !== index));
  }, []);

  /**
   * Clear all files
   */
  const clearFiles = useCallback(() => {
    setFiles([]);
  }, []);

  /**
   * Get accepted file types based on processing mode
   */
  const getAcceptedTypes = useCallback(() => {
    const typeMap = {
      pdf: ['.pdf'],
      docx: ['.docx', '.doc'],
      pptx: ['.pptx', '.ppt'],
      images: ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff']
    };
    return typeMap[processingMode] || [];
  }, [processingMode]);

  return {
    files,
    processingMode,
    setProcessingMode,
    addFiles,
    removeFile,
    clearFiles,
    getAcceptedTypes,
    hasFiles: files.length > 0,
    canProcess: files.length > 0 && processingMode !== ''
  };
}

export default useFileUpload;
