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

export default {
    generateReport,
    getCriteria,
    healthCheck,
};
