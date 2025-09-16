// Request Manager for Homepage Companion Extension Popup
// Provides a clean HTTP client interface with retry logic and timeout support

export interface RequestConfig {
    baseUrl: string;
    timeout: number;
    retryAttempts: number;
}

export class RequestManager {
    private config: RequestConfig;

    constructor(baseUrl: string = 'http://localhost:8000') {
        this.config = {
            baseUrl,
            timeout: 5000, // 5 seconds
            retryAttempts: 3
        };
    }

    // Generic request method
    async request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
        const url = `${this.config.baseUrl}${endpoint}`;

        const requestOptions: RequestInit = {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        };

        // Add timeout
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), this.config.timeout);

        try {
            const response = await fetch(url, {
                ...requestOptions,
                signal: controller.signal
            });

            clearTimeout(timeoutId);

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            return await response.json();
        } catch (error) {
            clearTimeout(timeoutId);
            throw error;
        }
    }

    // Convenience methods
    async get<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
        return this.request<T>(endpoint, { ...options, method: 'GET' });
    }

    async post<T>(endpoint: string, data?: any, options: RequestInit = {}): Promise<T> {
        return this.request<T>(endpoint, {
            ...options,
            method: 'POST',
            body: data ? JSON.stringify(data) : undefined
        });
    }

    async put<T>(endpoint: string, data?: any, options: RequestInit = {}): Promise<T> {
        return this.request<T>(endpoint, {
            ...options,
            method: 'PUT',
            body: data ? JSON.stringify(data) : undefined
        });
    }

    async delete<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
        return this.request<T>(endpoint, { ...options, method: 'DELETE' });
    }

    // Retry logic for failed requests
    async requestWithRetry<T>(
        requestFn: () => Promise<T>,
        attempts: number = this.config.retryAttempts
    ): Promise<T> {
        try {
            return await requestFn();
        } catch (error) {
            if (attempts > 0) {
                console.log(`Retrying request, ${attempts} attempts left...`);
                await this.delay(1000); // Wait 1 second before retry
                return this.requestWithRetry(requestFn, attempts - 1);
            }
            throw error;
        }
    }


    private delay(ms: number): Promise<void> {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
}
