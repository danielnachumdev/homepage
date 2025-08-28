import type {
    RequestConfig,
    ApiResponse,
    ApiError,
    RequestMiddleware,
    ResponseMiddleware,
    ErrorMiddleware,
    RequestManagerConfig,
    HttpMethod,
    RequestOptions
} from './types';

export class RequestManager {
    private config: RequestManagerConfig;
    private requestMiddlewares: RequestMiddleware[] = [];
    private responseMiddlewares: ResponseMiddleware[] = [];
    private errorMiddlewares: ErrorMiddleware[] = [];

    constructor(config: RequestManagerConfig) {
        this.config = {
            defaultTimeout: 10000,
            defaultHeaders: {
                'Content-Type': 'application/json',
            },
            ...config
        };

        // Initialize middlewares
        this.requestMiddlewares = config.requestMiddlewares || [];
        this.responseMiddlewares = config.responseMiddlewares || [];
        this.errorMiddlewares = config.errorMiddlewares || [];
    }

    // Add middleware methods
    addRequestMiddleware(middleware: RequestMiddleware): void {
        this.requestMiddlewares.push(middleware);
    }

    addResponseMiddleware(middleware: ResponseMiddleware): void {
        this.responseMiddlewares.push(middleware);
    }

    addErrorMiddleware(middleware: ErrorMiddleware): void {
        this.errorMiddlewares.push(middleware);
    }

    // Remove middleware methods
    removeRequestMiddleware(middleware: RequestMiddleware): void {
        const index = this.requestMiddlewares.indexOf(middleware);
        if (index > -1) {
            this.requestMiddlewares.splice(index, 1);
        }
    }

    removeResponseMiddleware(middleware: ResponseMiddleware): void {
        const index = this.responseMiddlewares.indexOf(middleware);
        if (index > -1) {
            this.responseMiddlewares.splice(index, 1);
        }
    }

    removeErrorMiddleware(middleware: ErrorMiddleware): void {
        const index = this.errorMiddlewares.indexOf(middleware);
        if (index > -1) {
            this.errorMiddlewares.splice(index, 1);
        }
    }

    // Main request method
    async request<T = any>(
        method: HttpMethod,
        endpoint: string,
        data?: any,
        options: RequestOptions = {}
    ): Promise<ApiResponse<T>> {
        const url = this.buildUrl(endpoint);
        const config: RequestConfig = {
            url,
            method,
            headers: { ...this.config.defaultHeaders, ...options.headers },
            body: data,
            timeout: options.timeout || this.config.defaultTimeout,
            signal: options.signal
        };

        try {
            // Apply request middlewares
            let processedConfig = config;
            if (!options.skipMiddlewares) {
                for (const middleware of this.requestMiddlewares) {
                    processedConfig = await middleware(processedConfig);
                }
            }

            // Create fetch request
            const fetchConfig: RequestInit = {
                method: processedConfig.method,
                headers: processedConfig.headers,
                signal: processedConfig.signal
            };

            if (processedConfig.body && method !== 'GET') {
                fetchConfig.body = typeof processedConfig.body === 'string'
                    ? processedConfig.body
                    : JSON.stringify(processedConfig.body);
            }

            // Add timeout if specified
            let timeoutId: number | undefined;
            if (processedConfig.timeout) {
                const controller = new AbortController();
                fetchConfig.signal = controller.signal;
                timeoutId = window.setTimeout(() => controller.abort(), processedConfig.timeout);
            }

            // Make the request
            const response = await fetch(processedConfig.url, fetchConfig);

            // Clear timeout
            if (timeoutId) {
                window.clearTimeout(timeoutId);
            }

            // Apply response middlewares
            let processedResponse = response;
            if (!options.skipMiddlewares) {
                for (const middleware of this.responseMiddlewares) {
                    processedResponse = await middleware(processedResponse, processedConfig);
                }
            }

            // Handle non-OK responses
            if (!processedResponse.ok) {
                const errorData = await this.parseResponse(processedResponse);
                throw this.createApiError(
                    `HTTP ${processedResponse.status}: ${processedResponse.statusText}`,
                    processedResponse.status,
                    processedResponse.statusText,
                    errorData
                );
            }

            // Parse successful response
            const responseData = await this.parseResponse(processedResponse);

            return {
                data: responseData,
                status: processedResponse.status,
                statusText: processedResponse.statusText,
                headers: this.parseHeaders(processedResponse.headers),
                ok: processedResponse.ok
            };

        } catch (error) {
            // Apply error middlewares
            let processedError = this.createApiError(
                error instanceof Error ? error.message : 'Unknown error',
                undefined,
                undefined,
                undefined,
                error instanceof Error ? error : undefined
            );

            if (!options.skipMiddlewares) {
                for (const middleware of this.errorMiddlewares) {
                    processedError = await middleware(processedError, config);
                }
            }

            throw processedError;
        }
    }

    // Convenience methods for HTTP methods
    async get<T = any>(endpoint: string, options?: RequestOptions): Promise<ApiResponse<T>> {
        return this.request<T>('GET', endpoint, undefined, options);
    }

    async post<T = any>(endpoint: string, data?: any, options?: RequestOptions): Promise<ApiResponse<T>> {
        return this.request<T>('POST', endpoint, data, options);
    }

    async put<T = any>(endpoint: string, data?: any, options?: RequestOptions): Promise<ApiResponse<T>> {
        return this.request<T>('PUT', endpoint, data, options);
    }

    async patch<T = any>(endpoint: string, data?: any, options?: RequestOptions): Promise<ApiResponse<T>> {
        return this.request<T>('PATCH', endpoint, data, options);
    }

    async delete<T = any>(endpoint: string, options?: RequestOptions): Promise<ApiResponse<T>> {
        return this.request<T>('DELETE', endpoint, undefined, options);
    }

    // Utility methods
    private buildUrl(endpoint: string): string {
        const cleanEndpoint = endpoint.startsWith('/') ? endpoint : `/${endpoint}`;
        return `${this.config.urlPrefix}${cleanEndpoint}`;
    }

    private async parseResponse(response: Response): Promise<any> {
        const contentType = response.headers.get('content-type');

        if (contentType?.includes('application/json')) {
            return response.json();
        }

        if (contentType?.includes('text/')) {
            return response.text();
        }

        return response.blob();
    }

    private parseHeaders(headers: Headers): Record<string, string> {
        const result: Record<string, string> = {};
        headers.forEach((value, key) => {
            result[key] = value;
        });
        return result;
    }

    private createApiError(
        message: string,
        status?: number,
        statusText?: string,
        data?: any,
        originalError?: Error
    ): ApiError {
        return {
            message,
            status,
            statusText,
            data,
            originalError
        };
    }

    // Configuration getters
    get urlPrefix(): string {
        return this.config.urlPrefix;
    }

    get defaultHeaders(): Record<string, string> {
        return { ...this.config.defaultHeaders };
    }

    get defaultTimeout(): number {
        return this.config.defaultTimeout || 10000;
    }
}
