import { describe, it, expect, beforeEach, afterEach } from 'vitest'
import { RequestManager } from '../../src/lib/RequestManager/RequestManager'
import {
  initFetchMock,
  cleanupFetchMock,
  resetFetchMock,
  mockEndpoint,
  mockSuccess,
  mockError,
  mockNetworkError,
  mockTimeout
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
      mockEndpoint('/api/test', mockSuccess({
        success: true,
        data: { message: 'Hello World' }
      }))

      const response = await requestManager.get('/api/test')

      expect(response.ok).toBe(true)
      expect(response.data.success).toBe(true)
      expect(response.data.data.message).toBe('Hello World')
    })

    it('should handle GET request errors', async () => {
      mockEndpoint('/api/test', mockError(404, 'Not Found'))

      await expect(requestManager.get('/api/test')).rejects.toThrow()
    })

    it('should handle network errors', async () => {
      mockEndpoint('/api/test', mockNetworkError())

      await expect(requestManager.get('/api/test')).rejects.toThrow()
    })
  })

  describe('POST Requests', () => {
    it('should make successful POST request', async () => {
      mockEndpoint('/api/test', mockSuccess({
        success: true,
        data: { id: 1, created: true }
      }))

      const response = await requestManager.post('/api/test', {
        name: 'Test Item'
      })

      expect(response.ok).toBe(true)
      expect(response.data.success).toBe(true)
      expect(response.data.data.id).toBe(1)
    })

    it('should handle POST request errors', async () => {
      mockEndpoint('/api/test', mockError(400, 'Bad Request'))

      await expect(requestManager.post('/api/test', {})).rejects.toThrow()
    })
  })

  describe('PUT Requests', () => {
    it('should make successful PUT request', async () => {
      mockEndpoint('/api/test/1', mockSuccess({
        success: true,
        data: { id: 1, updated: true }
      }))

      const response = await requestManager.put('/api/test/1', {
        name: 'Updated Item'
      })

      expect(response.ok).toBe(true)
      expect(response.data.success).toBe(true)
      expect(response.data.data.updated).toBe(true)
    })

    it('should handle PUT request errors', async () => {
      mockEndpoint('/api/test/1', mockError(404, 'Not Found'))

      await expect(requestManager.put('/api/test/1', {})).rejects.toThrow()
    })
  })

  describe('DELETE Requests', () => {
    it('should make successful DELETE request', async () => {
      mockEndpoint('/api/test/1', mockSuccess({
        success: true,
        data: { deleted: true }
      }))

      const response = await requestManager.delete('/api/test/1')

      expect(response.ok).toBe(true)
      expect(response.data.success).toBe(true)
      expect(response.data.data.deleted).toBe(true)
    })

    it('should handle DELETE request errors', async () => {
      mockEndpoint('/api/test/1', mockError(403, 'Forbidden'))

      await expect(requestManager.delete('/api/test/1')).rejects.toThrow()
    })
  })

  describe('Timeout Handling', () => {
    it('should handle request timeout', async () => {
      mockEndpoint('/api/slow', mockTimeout(10000))

      await expect(requestManager.get('/api/slow')).rejects.toThrow()
    })

    it('should handle custom timeout', async () => {
      mockEndpoint('/api/slow', mockTimeout(2000))

      await expect(requestManager.get('/api/slow', {}, { timeout: 1000 })).rejects.toThrow()
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
      mockEndpoint('/api/test', mockSuccess({ success: true }))

      const response = await requestManager.get('/api/test', {}, {
        headers: {
          'Authorization': 'Bearer token123',
          'X-Custom-Header': 'custom-value'
        }
      })

      expect(response.ok).toBe(true)
    })

    it('should handle custom timeout', async () => {
      mockEndpoint('/api/test', mockTimeout(2000))

      await expect(requestManager.get('/api/test', {}, { timeout: 1000 })).rejects.toThrow()
    })

    it('should skip middlewares when requested', async () => {
      mockEndpoint('/api/test', mockSuccess({ success: true }))

      const response = await requestManager.get('/api/test', {}, { skipMiddlewares: true })

      expect(response.ok).toBe(true)
    })
  })
})
