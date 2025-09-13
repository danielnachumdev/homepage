import { describe, it, expect, beforeEach, afterEach, afterAll } from 'vitest'
import { RequestManager } from '../../src/lib/RequestManager/RequestManager'
import {
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
} from '../utils/fetch-mock'

describe('RequestManager', () => {
  let requestManager: RequestManager

  beforeEach(() => {
    initFetchMock()
    requestManager = new RequestManager({
      urlPrefix: 'http://localhost:8000',
      defaultTimeout: 5000,
      defaultHeaders: {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
      }
    })
  })

  afterEach(() => {
    resetFetchMock()
  })

  afterAll(() => {
    cleanupFetchMock()
  })

  describe('GET Requests', () => {
    it('should make successful GET request', async () => {
      const mock = mockEndpoint('/api/test', mockSuccess({
        success: true,
        data: { message: 'Hello World' }
      }))

      const response = await requestManager.get('/api/test')

      expect(response.ok).toBe(true)
      expect(response.data.success).toBe(true)
      expect(response.data.data.message).toBe('Hello World')

      // Verify fetch was called exactly once
      expect(mock.getCallCount()).toBe(1)
      expect(mock.wasCalledTimes(1)).toBe(true)

      // Verify the call was made with correct arguments
      expect(mock.wasCalledWith('/api/test')).toBe(true)
      const lastCall = mock.getLastCall()
      expect(lastCall?.options?.method).toBe('GET')
      expect(lastCall?.url).toContain('/api/test')
    })

    it('should handle GET request errors', async () => {
      const mock = mockEndpoint('/api/test', mockError(404, 'Not Found'))

      await expect(requestManager.get('/api/test')).rejects.toThrow()

      // Verify fetch was called exactly once
      expect(mock.getCallCount()).toBe(1)
      expect(mock.wasCalledWith('/api/test')).toBe(true)
    })

    it('should handle network errors', async () => {
      const mock = mockEndpoint('/api/test', mockNetworkError())

      await expect(requestManager.get('/api/test')).rejects.toThrow()

      // Verify fetch was called exactly once
      expect(mock.getCallCount()).toBe(1)
      expect(mock.wasCalledWith('/api/test')).toBe(true)
    })

    it('should verify multiple GET calls', async () => {
      const mock = mockEndpoint('/api/test', mockSuccess({ success: true }))

      // Make multiple calls
      await requestManager.get('/api/test')
      await requestManager.get('/api/test')
      await requestManager.get('/api/test')

      // Verify fetch was called exactly 3 times
      expect(mock.getCallCount()).toBe(3)
      expect(mock.wasCalledTimes(3)).toBe(true)

      // Verify all calls were made with correct arguments
      const calls = mock.getCalls()
      calls.forEach(call => {
        expect(call.options?.method).toBe('GET')
        expect(call.url).toContain('/api/test')
      })
    })
  })

  describe('POST Requests', () => {
    it('should make successful POST request', async () => {
      const mock = mockEndpoint('/api/test', mockSuccess({
        success: true,
        data: { id: 1, created: true }
      }))

      const response = await requestManager.post('/api/test', {
        name: 'Test Item'
      })

      expect(response.ok).toBe(true)
      expect(response.data.success).toBe(true)
      expect(response.data.data.id).toBe(1)

      // Verify fetch was called exactly once
      expect(mock.getCallCount()).toBe(1)
      expect(mock.wasCalledTimes(1)).toBe(true)

      // Verify the call was made with correct arguments
      expect(mock.wasCalledWith('/api/test')).toBe(true)
      const lastCall = mock.getLastCall()
      expect(lastCall?.options?.method).toBe('POST')
      expect(lastCall?.url).toContain('/api/test')
      expect(lastCall?.options?.body).toContain('Test Item')
    })

    it('should handle POST request errors', async () => {
      const mock = mockEndpoint('/api/test', mockError(400, 'Bad Request'))

      await expect(requestManager.post('/api/test', {})).rejects.toThrow()

      // Verify fetch was called exactly once
      expect(mock.getCallCount()).toBe(1)
      expect(mock.wasCalledWith('/api/test')).toBe(true)
    })

    it('should verify POST request with custom headers', async () => {
      const mock = mockEndpoint('/api/test', mockSuccess({ success: true }))

      await requestManager.post('/api/test', { data: 'test' }, {
        headers: {
          'Authorization': 'Bearer token123',
          'X-Custom-Header': 'custom-value'
        }
      })

      // Verify fetch was called with custom headers
      expect(mock.getCallCount()).toBe(1)
      const lastCall = mock.getLastCall()
      expect(lastCall?.options?.headers).toMatchObject({
        'Authorization': 'Bearer token123',
        'X-Custom-Header': 'custom-value'
      })
    })
  })

  describe('PUT Requests', () => {
    it('should make successful PUT request', async () => {
      const mock = mockEndpoint('/api/test/1', mockSuccess({
        success: true,
        data: { id: 1, updated: true }
      }))

      const response = await requestManager.put('/api/test/1', {
        name: 'Updated Item'
      })

      expect(response.ok).toBe(true)
      expect(response.data.success).toBe(true)
      expect(response.data.data.updated).toBe(true)

      // Verify fetch was called exactly once
      expect(mock.getCallCount()).toBe(1)
      expect(mock.wasCalledWith('/api/test/1')).toBe(true)
      const lastCall = mock.getLastCall()
      expect(lastCall?.options?.method).toBe('PUT')
      expect(lastCall?.options?.body).toContain('Updated Item')
    })

    it('should handle PUT request errors', async () => {
      const mock = mockEndpoint('/api/test/1', mockError(404, 'Not Found'))

      await expect(requestManager.put('/api/test/1', {})).rejects.toThrow()

      // Verify fetch was called exactly once
      expect(mock.getCallCount()).toBe(1)
      expect(mock.wasCalledWith('/api/test/1')).toBe(true)
    })
  })

  describe('DELETE Requests', () => {
    it('should make successful DELETE request', async () => {
      const mock = mockEndpoint('/api/test/1', mockSuccess({
        success: true,
        data: { deleted: true }
      }))

      const response = await requestManager.delete('/api/test/1')

      expect(response.ok).toBe(true)
      expect(response.data.success).toBe(true)
      expect(response.data.data.deleted).toBe(true)

      // Verify fetch was called exactly once
      expect(mock.getCallCount()).toBe(1)
      expect(mock.wasCalledWith('/api/test/1')).toBe(true)
      const lastCall = mock.getLastCall()
      expect(lastCall?.options?.method).toBe('DELETE')
    })

    it('should handle DELETE request errors', async () => {
      const mock = mockEndpoint('/api/test/1', mockError(403, 'Forbidden'))

      await expect(requestManager.delete('/api/test/1')).rejects.toThrow()

      // Verify fetch was called exactly once
      expect(mock.getCallCount()).toBe(1)
      expect(mock.wasCalledWith('/api/test/1')).toBe(true)
    })
  })

  describe('Timeout Handling', () => {
    it('should handle request timeout', async () => {
      mockEndpoint('/api/slow', mockTimeout(10000))

      await expect(requestManager.get('/api/slow')).rejects.toThrow()
    })

    it('should handle custom timeout', async () => {
      mockEndpoint('/api/slow', mockTimeout(2000))

      await expect(requestManager.get('/api/slow', { timeout: 1000 })).rejects.toThrow()
    })
  })

  describe('Error Handling', () => {
    it('should handle 400 Bad Request', async () => {
      mockEndpoint('/api/test', mockError(400, 'Bad Request'))

      await expect(requestManager.get('/api/test')).rejects.toThrow()
    })

    it('should handle 401 Unauthorized', async () => {
      mockEndpoint('/api/test', mockError(401, 'Unauthorized'))

      await expect(requestManager.get('/api/test')).rejects.toThrow()
    })

    it('should handle 403 Forbidden', async () => {
      mockEndpoint('/api/test', mockError(403, 'Forbidden'))

      await expect(requestManager.get('/api/test')).rejects.toThrow()
    })

    it('should handle 404 Not Found', async () => {
      mockEndpoint('/api/test', mockError(404, 'Not Found'))

      await expect(requestManager.get('/api/test')).rejects.toThrow()
    })

    it('should handle 500 Internal Server Error', async () => {
      mockEndpoint('/api/test', mockError(500, 'Internal Server Error'))

      await expect(requestManager.get('/api/test')).rejects.toThrow()
    })

    it('should handle 502 Bad Gateway', async () => {
      mockEndpoint('/api/test', mockError(502, 'Bad Gateway'))

      await expect(requestManager.get('/api/test')).rejects.toThrow()
    })

    it('should handle 503 Service Unavailable', async () => {
      mockEndpoint('/api/test', mockError(503, 'Service Unavailable'))

      await expect(requestManager.get('/api/test')).rejects.toThrow()
    })
  })

  describe('Response Processing', () => {
    it('should handle JSON response', async () => {
      mockEndpoint('/api/test', {
        status: 200,
        body: { message: 'Hello' },
        headers: { 'Content-Type': 'application/json' }
      })

      const response = await requestManager.get('/api/test')

      expect(response.ok).toBe(true)
      expect(response.data.message).toBe('Hello')
    })

    it('should handle text response', async () => {
      mockEndpoint('/api/test', {
        status: 200,
        body: 'Hello World',
        headers: { 'Content-Type': 'text/plain' }
      })

      const response = await requestManager.get('/api/test')

      expect(response.ok).toBe(true)
      expect(response.data).toBe('Hello World')
    })

    it('should handle empty response', async () => {
      mockEndpoint('/api/test', {
        status: 204,
        body: undefined,
        headers: {}
      })

      const response = await requestManager.get('/api/test')

      expect(response.ok).toBe(true)
      expect(response.data).toBeInstanceOf(Blob)
      expect(response.data.size).toBe(0)
    })
  })

  describe('Request Configuration', () => {
    it('should use custom headers', async () => {
      const mock = mockEndpoint('/api/test', mockSuccess({ success: true }))

      const response = await requestManager.get('/api/test', {
        headers: {
          'Authorization': 'Bearer token123',
          'X-Custom-Header': 'custom-value'
        }
      })

      expect(response.ok).toBe(true)

      // Verify fetch was called with custom headers
      expect(mock.getCallCount()).toBe(1)
      const lastCall = mock.getLastCall()
      expect(lastCall?.options?.headers).toMatchObject({
        'Authorization': 'Bearer token123',
        'X-Custom-Header': 'custom-value'
      })
    })

    it('should handle custom timeout', async () => {
      const mock = mockEndpoint('/api/test', mockTimeout(2000))

      await expect(requestManager.get('/api/test', { timeout: 1000 })).rejects.toThrow()

      // Verify fetch was called
      expect(mock.getCallCount()).toBe(1)
    })

    it('should skip middlewares when requested', async () => {
      const mock = mockEndpoint('/api/test', mockSuccess({ success: true }))

      const response = await requestManager.get('/api/test', { skipMiddlewares: true })

      expect(response.ok).toBe(true)
      expect(mock.getCallCount()).toBe(1)
    })
  })

  describe('Mock System Verification', () => {
    it('should track multiple different endpoints', async () => {
      const mock1 = mockEndpoint('/api/users', mockSuccess({ users: [] }))
      const mock2 = mockEndpoint('/api/posts', mockSuccess({ posts: [] }))
      const mock3 = mockEndpoint('/api/comments', mockSuccess({ comments: [] }))

      await requestManager.get('/api/users')
      await requestManager.get('/api/posts')
      await requestManager.get('/api/comments')

      // Each endpoint should have been called exactly once
      expect(mock1.getCallCount()).toBe(1)
      expect(mock2.getCallCount()).toBe(1)
      expect(mock3.getCallCount()).toBe(1)
    })

    it('should verify call arguments in detail', async () => {
      const mock = mockEndpoint('/api/test', mockSuccess({ success: true }))

      const testData = { name: 'Test', value: 123 }
      await requestManager.post('/api/test', testData, {
        headers: { 'Content-Type': 'application/json' }
      })

      expect(mock.getCallCount()).toBe(1)
      const call = mock.getCall(0)
      expect(call?.url).toContain('/api/test')
      expect(call?.options?.method).toBe('POST')
      expect(call?.options?.body).toContain('Test')
      expect(call?.options?.body).toContain('123')
      expect(call?.options?.headers).toMatchObject({
        'Content-Type': 'application/json'
      })
    })

    it('should reset mock state between tests', async () => {
      const mock = mockEndpoint('/api/test', mockSuccess({ success: true }))

      // This should be the first call in this test
      await requestManager.get('/api/test')
      expect(mock.getCallCount()).toBe(1)
    })

    it('should verify global fetch mock state', async () => {
      mockEndpoint('/api/test', mockSuccess({ success: true }))

      await requestManager.get('/api/test')

      // Verify global fetch mock was called
      const fetchMock = getFetchMock()
      expect(fetchMock).toBeTruthy()
      expect(fetchMock?.mock.calls.length).toBe(1)

      // Verify the call was made with correct URL
      const calls = getFetchCalls()
      expect(calls[0][0]).toContain('/api/test')
      expect(calls[0][1]?.method).toBe('GET')
    })
  })
})
