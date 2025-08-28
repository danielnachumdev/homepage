// API configuration for backend endpoints
export const API_CONFIG = {
    // Base URL for the backend API
    BASE_URL: import.meta.env.VITE_BACKEND_URL || 'http://localhost:3000',

    // Health check endpoint
    HEALTH_CHECK: '/api/health',

    // Timeout for requests (in milliseconds)
    REQUEST_TIMEOUT: 3000,

    // Health check interval (in milliseconds)
    HEALTH_CHECK_INTERVAL: 5000,
} as const;

// Helper function to build full API URLs
export const buildApiUrl = (endpoint: string): string => {
    return `${API_CONFIG.BASE_URL}${endpoint}`;
};
