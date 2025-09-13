import { vi } from 'vitest'

// Types for our mock system
export interface MockResponse {
    status: number
    statusText?: string
    headers?: Record<string, string>
    body?: any
    delay?: number
    shouldReject?: boolean
    error?: Error
}

export interface MockConfig {
    [endpoint: string]: MockResponse | MockResponse[]
}

// Global mock state
let mockConfig: MockConfig = {}
let originalFetch: typeof global.fetch

// Initialize the mock system
export const initFetchMock = () => {
    // Store original fetch
    originalFetch = global.fetch

    // Create mock fetch
    global.fetch = vi.fn().mockImplementation(async (url: string | URL, options?: RequestInit) => {
        const urlString = typeof url === 'string' ? url : url.toString()

        // Find matching mock configuration
        const mockResponse = findMockResponse(urlString, options?.method || 'GET')

        if (!mockResponse) {
            console.warn(`No mock found for ${options?.method || 'GET'} ${urlString}`)
            // Return a default error response instead of calling original fetch to avoid recursion
            return new Response(
                JSON.stringify({ error: 'No mock found', success: false }),
                {
                    status: 404,
                    statusText: 'Not Found',
                    headers: { 'Content-Type': 'application/json' }
                }
            )
        }

        // Handle rejection
        if (mockResponse.shouldReject) {
            throw mockResponse.error || new Error('Mock fetch error')
        }

        // Handle delay
        if (mockResponse.delay) {
            await new Promise(resolve => setTimeout(resolve, mockResponse.delay))
        }

        // Create response
        let responseBody: string | undefined
        if (mockResponse.body !== undefined) {
            const contentType = mockResponse.headers?.['Content-Type'] || 'application/json'
            if (contentType.includes('application/json')) {
                responseBody = JSON.stringify(mockResponse.body)
            } else {
                responseBody = typeof mockResponse.body === 'string' ? mockResponse.body : String(mockResponse.body)
            }
        }

        const response = new Response(
            responseBody,
            {
                status: mockResponse.status,
                statusText: mockResponse.statusText || getStatusText(mockResponse.status),
                headers: mockResponse.headers || { 'Content-Type': 'application/json' }
            }
        )

        return response
    })
}

// Clean up the mock system
export const cleanupFetchMock = () => {
    if (originalFetch) {
        global.fetch = originalFetch
    }
    mockConfig = {}
}

// Reset mocks between tests
export const resetFetchMock = () => {
    mockConfig = {}
    if (global.fetch && vi.isMockFunction(global.fetch)) {
        vi.mocked(global.fetch).mockClear()
    }
}

// Set up mock responses
export const mockFetch = (config: MockConfig) => {
    mockConfig = { ...mockConfig, ...config }
}

// Set up a single endpoint mock
export const mockEndpoint = (endpoint: string, response: MockResponse | MockResponse[]) => {
    mockConfig[endpoint] = response
}

// Find the appropriate mock response for a URL and method
const findMockResponse = (url: string, method: string): MockResponse | null => {
    // Try exact match first
    const exactKey = `${method.toUpperCase()} ${url}`
    if (mockConfig[exactKey]) {
        const response = mockConfig[exactKey]
        return Array.isArray(response) ? response[0] : response
    }

    // Try pattern matching
    for (const [pattern, response] of Object.entries(mockConfig)) {
        if (isUrlMatch(url, pattern)) {
            const responseArray = Array.isArray(response) ? response : [response]
            return responseArray[0]
        }
    }

    return null
}

// Simple URL pattern matching
const isUrlMatch = (url: string, pattern: string): boolean => {
    // Remove method prefix if present
    const cleanPattern = pattern.replace(/^(GET|POST|PUT|DELETE|PATCH)\s+/, '')

    // Exact match
    if (url === cleanPattern) return true

    // Wildcard match
    if (cleanPattern.includes('*')) {
        const regex = new RegExp(cleanPattern.replace(/\*/g, '.*'))
        return regex.test(url)
    }

    // Contains match
    if (cleanPattern.includes(url) || url.includes(cleanPattern)) return true

    return false
}

// Get status text for status codes
const getStatusText = (status: number): string => {
    const statusTexts: Record<number, string> = {
        200: 'OK',
        201: 'Created',
        400: 'Bad Request',
        401: 'Unauthorized',
        403: 'Forbidden',
        404: 'Not Found',
        500: 'Internal Server Error',
        502: 'Bad Gateway',
        503: 'Service Unavailable',
        504: 'Gateway Timeout'
    }
    return statusTexts[status] || 'Unknown'
}

// Helper functions for common scenarios
export const mockSuccess = (body: any, status = 200): MockResponse => ({
    status,
    body,
    headers: { 'Content-Type': 'application/json' }
})

export const mockError = (status = 500, message = 'Server Error'): MockResponse => ({
    status,
    body: { error: message, success: false },
    headers: { 'Content-Type': 'application/json' }
})

export const mockNetworkError = (): MockResponse => ({
    status: 0,
    shouldReject: true,
    error: new Error('Network Error')
})

export const mockTimeout = (delay = 5000): MockResponse => ({
    status: 200,
    body: { success: true },
    delay,
    shouldReject: true,
    error: new Error('Request timed out')
})

// Test scenario builder utility
export const createTestScenario = (name: string, config: MockConfig) => ({
    name,
    setup: () => mockFetch(config),
    cleanup: resetFetchMock
})

// Export everything
export default {
    initFetchMock,
    cleanupFetchMock,
    resetFetchMock,
    mockFetch,
    mockEndpoint,
    mockSuccess,
    mockError,
    mockNetworkError,
    mockTimeout,
    createTestScenario
}
