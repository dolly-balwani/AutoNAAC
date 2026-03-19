import { useState, useCallback } from 'react';
import { uploadExcel, compileReport, getDownloadUrl } from '../services/api';

/**
 * useExcelUpload Hook
 * 
 * Manages Excel file upload and report generation workflow.
 * 
 * @returns {Object} Excel upload state and methods
 */
export function useExcelUpload() {
    // Excel file state
    const [excelFile, setExcelFile] = useState(null);
    const [excelFilename, setExcelFilename] = useState('');
    const [availableCriteria, setAvailableCriteria] = useState([]);
    const [selectedCriterion, setSelectedCriterion] = useState('');

    // Status states
    const [uploadStatus, setUploadStatus] = useState('idle'); // idle, uploading, success, error
    const [reportStatus, setReportStatus] = useState('idle'); // idle, generating, success, error
    const [error, setError] = useState(null);

    // Report result
    const [reportResult, setReportResult] = useState(null);

    /**
     * Handle Excel file upload
     */
    const handleUpload = useCallback(async (file) => {
        if (!file) return;

        setExcelFile(file);
        setUploadStatus('uploading');
        setError(null);
        setAvailableCriteria([]);
        setSelectedCriterion('');
        setReportResult(null);

        try {
            const result = await uploadExcel(file);
            setExcelFilename(result.filename);
            setAvailableCriteria(result.available_criteria || []);
            setUploadStatus('success');

            // Auto-select if only one criterion available
            if (result.available_criteria?.length === 1) {
                setSelectedCriterion(result.available_criteria[0]);
            }
        } catch (err) {
            setUploadStatus('error');
            setError(err.message);
        }
    }, []);

    /**
     * Generate report for selected criterion
     */
    const handleGenerateReport = useCallback(async (generateCaptions = true) => {
        if (!excelFilename || !selectedCriterion) {
            setError('Please upload an Excel file and select a criterion');
            return;
        }

        setReportStatus('generating');
        setError(null);

        try {
            const result = await compileReport(excelFilename, selectedCriterion, generateCaptions);

            if (result.success) {
                setReportResult({
                    ...result,
                    downloadUrl: getDownloadUrl(result.download_url.split('/').pop()),
                });
                setReportStatus('success');
            } else {
                throw new Error(result.error || 'Failed to generate report');
            }
        } catch (err) {
            setReportStatus('error');
            setError(err.message);
        }
    }, [excelFilename, selectedCriterion]);

    /**
     * Reset all state
     */
    const reset = useCallback(() => {
        setExcelFile(null);
        setExcelFilename('');
        setAvailableCriteria([]);
        setSelectedCriterion('');
        setUploadStatus('idle');
        setReportStatus('idle');
        setError(null);
        setReportResult(null);
    }, []);

    return {
        // State
        excelFile,
        excelFilename,
        availableCriteria,
        selectedCriterion,
        setSelectedCriterion,
        uploadStatus,
        reportStatus,
        error,
        reportResult,

        // Computed
        isUploading: uploadStatus === 'uploading',
        isGenerating: reportStatus === 'generating',
        canGenerate: uploadStatus === 'success' && selectedCriterion !== '',
        hasReport: reportStatus === 'success' && reportResult !== null,

        // Methods
        handleUpload,
        handleGenerateReport,
        reset,
    };
}

export default useExcelUpload;
