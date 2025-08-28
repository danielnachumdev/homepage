import { RequestManager } from '../RequestManager/RequestManager';
import {
    authMiddleware,
    requestIdMiddleware,
    loggingMiddleware,
    responseLoggingMiddleware,
    errorLoggingMiddleware,
    userFriendlyErrorMiddleware,
    networkErrorMiddleware
} from '../RequestManager/middlewares';

// Get backend URL from environment or use default
const BACKEND_URL = import.meta.env.VITE_BACKEND_URL || 'http://localhost:8000';

// Create the main API instance
export const api = new RequestManager({
    urlPrefix: BACKEND_URL,
    defaultTimeout: 10000,
    defaultHeaders: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
    },
    // Add common middlewares
    requestMiddlewares: [
        requestIdMiddleware,    // Add unique request ID
        loggingMiddleware,      // Log outgoing requests
        authMiddleware,         // Add auth token if available
    ],
    responseMiddlewares: [
        responseLoggingMiddleware, // Log incoming responses
    ],
    errorMiddlewares: [
        errorLoggingMiddleware,        // Log all errors
        networkErrorMiddleware,        // Handle network errors
        userFriendlyErrorMiddleware,   // Convert errors to user-friendly messages
    ]
});

// Export the RequestManager class for advanced usage
export { RequestManager } from '../RequestManager/RequestManager';

// Export types for external use
export type {
    ApiResponse,
    ApiError,
    RequestOptions,
    RequestMiddleware,
    ResponseMiddleware,
    ErrorMiddleware
} from '../RequestManager/types';

// Export common middlewares
export * from '../RequestManager/middlewares';
