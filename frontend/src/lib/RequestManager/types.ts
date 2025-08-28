// Request configuration types
export interface RequestConfig {
    url: string;
    method: 'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE';
    headers?: Record<string, string>;
    body?: any;
    timeout?: number;
    signal?: AbortSignal;
}

// Response wrapper type
export interface ApiResponse<T = any> {
    data: T;
    status: number;
    statusText: string;
    headers: Record<string, string>;
    ok: boolean;
}

// Error type for failed requests
export interface ApiError {
    message: string;
    status?: number;
    statusText?: string;
    data?: any;
    originalError?: Error;
}

// Middleware types
export type RequestMiddleware = (config: RequestConfig) => RequestConfig | Promise<RequestConfig>;
export type ResponseMiddleware = (response: Response, config: RequestConfig) => Response | Promise<Response>;
export type ErrorMiddleware = (error: ApiError, config: RequestConfig) => ApiError | Promise<ApiError>;

// Request manager configuration
export interface RequestManagerConfig {
    urlPrefix: string;
    defaultHeaders?: Record<string, string>;
    defaultTimeout?: number;
    requestMiddlewares?: RequestMiddleware[];
    responseMiddlewares?: ResponseMiddleware[];
    errorMiddlewares?: ErrorMiddleware[];
}

// HTTP methods for convenience
export type HttpMethod = 'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE';

// Request options that can be passed to individual requests
export interface RequestOptions {
    headers?: Record<string, string>;
    timeout?: number;
    signal?: AbortSignal;
    skipMiddlewares?: boolean;
}
