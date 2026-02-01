import { useState, useCallback, useRef, useEffect } from 'react';

// Global state to share processing status across components
let globalProcessingState = {
  isProcessing: false,
  listeners: new Set()
};

/**
 * useProcessing Hook
 * 
 * Manages document processing state and simulation.
 * Uses global state to share processing status across components.
 * 
 * @returns {Object} Processing state and methods
 */
export function useProcessing() {
  const [isProcessing, setIsProcessing] = useState(globalProcessingState.isProcessing);
  const [progress, setProgress] = useState(0);
  const [currentFile, setCurrentFile] = useState('');
  const [logs, setLogs] = useState([]);
  const [stats, setStats] = useState({
    total: 0,
    processed: 0,
    success: 0,
    failed: 0
  });
  
  const intervalRef = useRef(null);

  // Subscribe to global state changes
  useEffect(() => {
    const listener = (processing) => {
      setIsProcessing(processing);
    };
    globalProcessingState.listeners.add(listener);
    return () => {
      globalProcessingState.listeners.delete(listener);
    };
  }, []);

  /**
   * Update global processing state
   */
  const updateGlobalState = (processing) => {
    globalProcessingState.isProcessing = processing;
    globalProcessingState.listeners.forEach(listener => listener(processing));
  };

  /**
   * Add a log entry
   */
  const addLog = useCallback((message, type = 'info') => {
    const time = new Date().toLocaleTimeString('en-US', { 
      hour12: false,
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    });
    setLogs(prev => [...prev, { time, message, type }]);
  }, []);

  /**
   * Start processing simulation with provided files
   */
  const startProcessing = useCallback((files) => {
    if (files.length === 0) return;

    // Reset state
    setProgress(0);
    setLogs([]);
    setStats({
      total: files.length,
      processed: 0,
      success: 0,
      failed: 0
    });
    updateGlobalState(true);
    setIsProcessing(true);

    addLog('Processing started...', 'info');
    addLog(`Found ${files.length} file(s) to process`, 'info');

    let currentIndex = 0;
    let processedCount = 0;

    // Simulate processing each file
    intervalRef.current = setInterval(() => {
      if (currentIndex < files.length) {
        const file = files[currentIndex];
        setCurrentFile(file.name);
        addLog(`Processing: ${file.name}`, 'info');

        // Simulate success/failure (90% success rate)
        const isSuccess = Math.random() > 0.1;
        
        setTimeout(() => {
          processedCount++;
          if (isSuccess) {
            addLog(`✓ Completed: ${file.name}`, 'success');
            setStats(prev => ({
              ...prev,
              processed: prev.processed + 1,
              success: prev.success + 1
            }));
          } else {
            addLog(`✗ Failed: ${file.name}`, 'error');
            setStats(prev => ({
              ...prev,
              processed: prev.processed + 1,
              failed: prev.failed + 1
            }));
          }

          // Update progress
          const newProgress = Math.round((processedCount / files.length) * 100);
          setProgress(newProgress);

          // Check if complete
          if (processedCount === files.length) {
            addLog('Processing complete!', 'success');
            setCurrentFile('');
            updateGlobalState(false);
            setIsProcessing(false);
            if (intervalRef.current) {
              clearInterval(intervalRef.current);
            }
          }
        }, 500);

        currentIndex++;
      }
    }, 1500);
  }, [addLog]);

  /**
   * Stop processing
   */
  const stopProcessing = useCallback(() => {
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
    }
    addLog('Processing stopped by user', 'warning');
    updateGlobalState(false);
    setIsProcessing(false);
    setCurrentFile('');
  }, [addLog]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, []);

  return {
    isProcessing,
    progress,
    currentFile,
    logs,
    stats,
    startProcessing,
    stopProcessing,
    addLog
  };
}

export default useProcessing;
