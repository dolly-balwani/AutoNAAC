/**
 * API Service for NAAC Report Generator
 * Handles communication with the FastAPI backend
 */

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

/**
 * Generate a NAAC report for the specified criterion
 * @param {string} criterion - The NAAC criterion to generate a report for
 * @returns {Promise<Object>} - The generated report data
 */
export async function generateReport(criterion) {
    const response = await fetch(`${API_BASE_URL}/api/generate-report`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ criterion }),
    });

    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to generate report');
    }

    return response.json();
}

/**
 * Get list of available NAAC criteria
 * @returns {Promise<Object>} - List of available criteria
 */
export async function getCriteria() {
    const response = await fetch(`${API_BASE_URL}/api/criteria`);

    if (!response.ok) {
        throw new Error('Failed to fetch criteria');
    }

    return response.json();
}

/**
 * Check API health status
 * @returns {Promise<Object>} - Health status
 */
export async function healthCheck() {
    const response = await fetch(`${API_BASE_URL}/api/health`);

    if (!response.ok) {
        throw new Error('API is not healthy');
    }

    return response.json();
}

/**
 * Upload an Excel file containing NAAC criterion data
 * @param {File} file - The Excel file to upload
 * @returns {Promise<Object>} - Upload result with available criteria
 */
export async function uploadExcel(file) {
    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch(`${API_BASE_URL}/api/upload-excel`, {
        method: 'POST',
        body: formData,
    });

    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to upload Excel file');
    }

    return response.json();
}

/**
 * Compile an enhanced NAAC report from uploaded Excel
 * @param {string} excelFilename - Name of the uploaded Excel file
 * @param {string} criterion - The criterion to generate report for (e.g., "5.1.3")
 * @param {boolean} generateCaptions - Whether to generate AI captions for images
 * @returns {Promise<Object>} - Compilation result with download URL
 */
export async function compileReport(excelFilename, criterion, generateCaptions = true) {
    const response = await fetch(`${API_BASE_URL}/api/compile-report`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            excel_filename: excelFilename,
            criterion: criterion,
            generate_captions: generateCaptions,
        }),
    });

    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to compile report');
    }

    return response.json();
}

/**
 * Get the download URL for a generated report
 * @param {string} filename - The report filename
 * @returns {string} - Full download URL
 */
export function getDownloadUrl(filename) {
    return `${API_BASE_URL}/api/download/${filename}`;
}

export default {
    generateReport,
    getCriteria,
    healthCheck,
    uploadExcel,
    compileReport,
    getDownloadUrl,
};
