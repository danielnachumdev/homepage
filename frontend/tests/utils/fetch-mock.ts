import { vi, type MockedFunction } from 'vitest'

// Types for our fetch mock system
export interface MockResponse {
    status: number
    statusText?: string
    headers?: Record<string, string>
    body?: any
    delay?: number
    shouldReject?: boolean
    error?: Error
}

export interface MockCall {
    url: string
    options?: RequestInit
    timestamp: number
}

export interface MockEndpoint {
    calls: MockCall[]
    getCallCount: () => number
    getCalls: () => MockCall[]
    getLastCall: () => MockCall | undefined
    getCall: (index: number) => MockCall | undefined
    wasCalledWith: (url: string, options?: Partial<RequestInit>) => boolean
    wasCalledTimes: (count: number) => boolean
    reset: () => void
    // Direct access to Vitest mock
    mock: MockedFunction<typeof fetch>
}

// Global state
let originalFetch: typeof fetch
let vitestMock: MockedFunction<typeof fetch> | null = null
let mockCalls: MockCall[] = []
let mockConfig: Map<string, MockResponse> = new Map()

// Initialize fetch mocking
export const initFetchMock = () => {
    // Store original fetch
    originalFetch = globalThis.fetch

    // Create Vitest mock for fetch
    vitestMock = vi.fn().mockImplementation(async (input: RequestInfo | URL, init?: RequestInit) => {
        const urlString = typeof input === 'string' ? input : input.toString()
        const method = init?.method || 'GET'

        // Track the call
        const call: MockCall = {
            url: urlString,
            options: init ? { ...init } : undefined,
            timestamp: Date.now()
        }
        mockCalls.push(call)

        // Find matching mock response
        const mockResponse = findMockResponse(urlString, method)

        if (!mockResponse) {
            console.log(`🔴 MOCK: No mock found for ${method} ${urlString}`)
            return new Response(
                JSON.stringify({ error: 'No mock found', success: false }),
                {
                    status: 404,
                    statusText: 'Not Found',
                    headers: { 'Content-Type': 'application/json' }
                }
            )
        }

        console.log(`🟡 MOCK: Found mock for ${method} ${urlString} -> ${mockResponse.status} ${mockResponse.statusText || getStatusText(mockResponse.status)}`)

        // Handle rejection
        if (mockResponse.shouldReject) {
            console.log(`🔴 MOCK: Throwing error for ${method} ${urlString}: ${mockResponse.error?.message || 'Mock fetch error'}`)
            throw mockResponse.error || new Error('Mock fetch error')
        }

        // Handle delay
        if (mockResponse.delay) {
            console.log(`⏳ MOCK: Adding delay of ${mockResponse.delay}ms for ${method} ${urlString}`)
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

        // For error status codes, we need to return a Response that will cause the RequestManager to throw
        // The RequestManager checks response.ok, which is false for 4xx and 5xx status codes
        const response = new Response(
            responseBody,
            {
                status: mockResponse.status,
                statusText: mockResponse.statusText || getStatusText(mockResponse.status),
                headers: mockResponse.headers || { 'Content-Type': 'application/json' }
            }
        )

        const isError = !response.ok
        const statusIcon = isError ? '🔴' : '🟢'
        console.log(`${statusIcon} MOCK: Returning ${method} ${urlString} -> ${response.status} ${response.statusText} (ok: ${response.ok})`)

        return response
    }) as MockedFunction<typeof fetch>

    // Replace global fetch
    globalThis.fetch = vitestMock
}

// Clean up fetch mocking
export const cleanupFetchMock = () => {
    if (originalFetch) {
        globalThis.fetch = originalFetch
    }
    mockCalls = []
    mockConfig.clear()
    vitestMock = null
}

// Reset mocks between tests
export const resetFetchMock = () => {
    mockCalls = []
    mockConfig.clear()
    if (vitestMock) {
        vitestMock.mockClear()
    }
}

// Set up a single endpoint mock
export const mockEndpoint = (endpoint: string, response: MockResponse): MockEndpoint => {
    if (!vitestMock) {
        throw new Error('initFetchMock() must be called before mockEndpoint()')
    }

    // Store the mock response
    mockConfig.set(endpoint, response)

    // Create a filtered view of calls for this endpoint
    const getCallsForEndpoint = () => {
        return mockCalls.filter(call => isUrlMatch(call.url, endpoint))
    }

    return {
        calls: getCallsForEndpoint(),
        getCallCount: () => getCallsForEndpoint().length,
        getCalls: () => [...getCallsForEndpoint()],
        getLastCall: () => {
            const calls = getCallsForEndpoint()
            return calls[calls.length - 1]
        },
        getCall: (index: number) => {
            const calls = getCallsForEndpoint()
            return calls[index]
        },
        wasCalledWith: (url: string, options?: Partial<RequestInit>) => {
            return getCallsForEndpoint().some(call => {
                // Extract the path from the full URL for comparison
                const callPath = call.url.replace(/^https?:\/\/[^\/]+/, '')
                const expectedPath = url.replace(/^https?:\/\/[^\/]+/, '')

                const urlMatch = callPath === expectedPath || callPath.includes(expectedPath) || expectedPath.includes(callPath)
                if (!urlMatch) return false

                if (!options) return true

                // Check method
                if (options.method && call.options?.method !== options.method) return false

                // Check headers
                if (options.headers) {
                    const callHeaders = call.options?.headers as Record<string, string> || {}
                    const expectedHeaders = options.headers as Record<string, string>
                    for (const [key, value] of Object.entries(expectedHeaders)) {
                        if (callHeaders[key] !== value) return false
                    }
                }

                // Check body
                if (options.body && call.options?.body !== options.body) return false

                return true
            })
        },
        wasCalledTimes: (count: number) => getCallsForEndpoint().length === count,
        reset: () => {
            // Remove calls for this endpoint
            mockCalls = mockCalls.filter(call => !isUrlMatch(call.url, endpoint))
        },
        // Direct access to the underlying Vitest mock
        mock: vitestMock
    }
}

// Find matching mock response
const findMockResponse = (url: string, method: string): MockResponse | null => {
    // Try exact match first
    const exactKey = `${method.toUpperCase()} ${url}`
    if (mockConfig.has(exactKey)) {
        return mockConfig.get(exactKey)!
    }

    // Try pattern matching
    for (const [pattern, response] of mockConfig.entries()) {
        if (isUrlMatch(url, pattern)) {
            return response
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

    // Path matching (extract path from full URL)
    const urlPath = url.replace(/^https?:\/\/[^\/]+/, '')
    const patternPath = cleanPattern.replace(/^https?:\/\/[^\/]+/, '')

    if (urlPath === patternPath) return true
    if (urlPath.includes(patternPath) || patternPath.includes(urlPath)) return true

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

// Direct access to Vitest mock for advanced usage
export const getFetchMock = (): MockedFunction<typeof fetch> | null => {
    return vitestMock
}

export const getFetchCalls = () => {
    return vitestMock?.mock.calls || []
}

// Export everything
export default {
    initFetchMock,
    cleanupFetchMock,
    resetFetchMock,
    mockEndpoint,
    mockSuccess,
    mockError,
    mockNetworkError,
    mockTimeout,
    getFetchMock,
    getFetchCalls
}