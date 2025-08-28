import type {
    RequestMiddleware,
    ResponseMiddleware,
    ErrorMiddleware,
    RequestConfig
} from './types';

// Request Middlewares

/**
 * Adds authentication token to requests
 */
export const authMiddleware: RequestMiddleware = (config: RequestConfig) => {
    const token = localStorage.getItem('authToken');
    if (token) {
        return {
            ...config,
            headers: {
                ...config.headers,
                'Authorization': `Bearer ${token}`
            }
        };
    }
    return config;
};

/**
 * Adds request ID for tracking
 */
export const requestIdMiddleware: RequestMiddleware = (config: RequestConfig) => {
    const requestId = `req_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    return {
        ...config,
        headers: {
            ...config.headers,
            'X-Request-ID': requestId
        }
    };
};

/**
 * Logs all outgoing requests
 */
export const loggingMiddleware: RequestMiddleware = (config: RequestConfig) => {
    console.log(`🚀 [${config.method}] ${config.url}`, {
        headers: config.headers,
        body: config.body
    });
    return config;
};

/**
 * Adds CSRF token to requests
 */
export const csrfMiddleware: RequestMiddleware = (config: RequestConfig) => {
    const csrfToken = document.querySelector('meta[name="csrf-token"]')?.getAttribute('content');
    if (csrfToken && config.method !== 'GET') {
        return {
            ...config,
            headers: {
                ...config.headers,
                'X-CSRF-Token': csrfToken
            }
        };
    }
    return config;
};

// Response Middlewares

/**
 * Logs all incoming responses
 */
export const responseLoggingMiddleware: ResponseMiddleware = (response: Response, config: RequestConfig) => {
    console.log(`✅ [${config.method}] ${config.url}`, {
        status: response.status,
        statusText: response.statusText,
        headers: Object.fromEntries(response.headers.entries())
    });
    return response;
};

/**
 * Logs only error responses (4xx and 5xx status codes)
 */
export const errorResponseLoggingMiddleware: ResponseMiddleware = (response: Response, config: RequestConfig) => {
    if (response.status >= 400) {
        console.error(`❌ [${config.method}] ${config.url} - Error Response`, {
            status: response.status,
            statusText: response.statusText,
            headers: Object.fromEntries(response.headers.entries())
        });
    }
    return response;
};

/**
 * Refreshes auth token on 401 responses
 */
export const tokenRefreshMiddleware: ResponseMiddleware = async (response: Response, config: RequestConfig) => {
    if (response.status === 401) {
        // Try to refresh the token
        try {
            const refreshResponse = await fetch('/api/auth/refresh', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    refreshToken: localStorage.getItem('refreshToken')
                })
            });

            if (refreshResponse.ok) {
                const { accessToken } = await refreshResponse.json();
                localStorage.setItem('authToken', accessToken);

                // Retry the original request
                const retryConfig = {
                    ...config,
                    headers: {
                        ...config.headers,
                        'Authorization': `Bearer ${accessToken}`
                    }
                };

                // Note: This would need to be handled differently in a real implementation
                // as we can't retry from within the middleware
                console.log('Token refreshed, retry the request manually');
            }
        } catch (error) {
            console.error('Failed to refresh token:', error);
            // Redirect to login
            window.location.href = '/login';
        }
    }
    return response;
};

/**
 * Handles rate limiting responses
 */
export const rateLimitMiddleware: ResponseMiddleware = (response: Response, config: RequestConfig) => {
    if (response.status === 429) {
        const retryAfter = response.headers.get('Retry-After');
        const delay = retryAfter ? parseInt(retryAfter) * 1000 : 5000;

        console.warn(`Rate limited. Retry after ${delay}ms`);

        // You could implement a retry mechanism here
        // For now, just show a user-friendly message
        if (typeof window !== 'undefined') {
            // Show toast notification or similar
            console.warn('Too many requests. Please wait before trying again.');
        }
    }
    return response;
};

// Error Middlewares

/**
 * Logs all errors
 */
export const errorLoggingMiddleware: ErrorMiddleware = (error, config: RequestConfig) => {
    console.error(`❌ [${config.method}] ${config.url}`, {
        error: error.message,
        status: error.status,
        data: error.data
    });
    return error;
};

/**
 * Handles network errors gracefully
 */
export const networkErrorMiddleware: ErrorMiddleware = (error, config: RequestConfig) => {
    if (error.message.includes('Failed to fetch') || error.message.includes('NetworkError')) {
        return {
            ...error,
            message: 'Network error. Please check your internet connection and try again.'
        };
    }
    return error;
};

/**
 * Converts common HTTP errors to user-friendly messages
 */
export const userFriendlyErrorMiddleware: ErrorMiddleware = (error, config: RequestConfig) => {
    const userFriendlyMessages: Record<number, string> = {
        400: 'Invalid request. Please check your input and try again.',
        401: 'You are not authorized to perform this action. Please log in.',
        403: 'Access denied. You don\'t have permission to perform this action.',
        404: 'The requested resource was not found.',
        409: 'Conflict. The resource already exists or has been modified.',
        422: 'Validation error. Please check your input.',
        429: 'Too many requests. Please wait before trying again.',
        500: 'Server error. Please try again later.',
        502: 'Bad gateway. Please try again later.',
        503: 'Service unavailable. Please try again later.',
        504: 'Gateway timeout. Please try again later.'
    };

    if (error.status && userFriendlyMessages[error.status]) {
        return {
            ...error,
            message: userFriendlyMessages[error.status]
        };
    }

    return error;
};

/**
 * Retry middleware for failed requests
 */
export const retryMiddleware: ErrorMiddleware = (error, config: RequestConfig) => {
    // Only retry on certain errors and methods
    const retryableErrors = [408, 429, 500, 502, 503, 504];
    const retryableMethods = ['GET', 'POST', 'PUT', 'PATCH'];

    if (retryableErrors.includes(error.status || 0) && retryableMethods.includes(config.method)) {
        // In a real implementation, you'd want to implement actual retry logic
        // This is just a placeholder for the concept
        console.log(`Retryable error detected: ${error.status}. Implement retry logic here.`);
    }

    return error;
};
