import { describe, it, expect, beforeEach, afterEach } from 'vitest'
import { renderHook, waitFor } from '@testing-library/react'
import { useBackendStatus } from '../../src/hooks/useBackendStatus'
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

describe('useBackendStatus Hook', () => {
  beforeEach(() => {
    initFetchMock()
  })

  afterEach(() => {
    resetFetchMock()
  })

  afterAll(() => {
    cleanupFetchMock()
  })

  describe('Success Scenarios', () => {
    it('should return connected status when API call succeeds', async () => {
      const mock = mockEndpoint('/health', mockSuccess({
        status: 'healthy',
        service: 'homepage-backend'
      }))

      const { result } = renderHook(() => useBackendStatus(100))

      await waitFor(() => {
        expect(result.current.isConnected).toBe(true)
        expect(result.current.error).toBe(null)
        expect(result.current.lastChecked).toBeInstanceOf(Date)
      })

      // Verify the API was called
      expect(mock.getCallCount()).toBe(1)
      expect(mock.wasCalledWith('/health')).toBe(true)
      const lastCall = mock.getLastCall()
      expect(lastCall?.options?.method).toBe('GET')
    })

    it('should handle different healthy response formats', async () => {
      mockEndpoint('/health', mockSuccess({
        healthy: true,
        message: 'All systems operational',
        timestamp: new Date().toISOString()
      }))

      const { result } = renderHook(() => useBackendStatus(100))

      await waitFor(() => {
        expect(result.current.isConnected).toBe(true)
        expect(result.current.error).toBe(null)
      })
    })
  })

  describe('Error Scenarios', () => {
    it('should handle 500 server error', async () => {
      mockEndpoint('/health', mockError(500, 'Internal Server Error'))

      const { result } = renderHook(() => useBackendStatus(100))

      await waitFor(() => {
        expect(result.current.isConnected).toBe(false)
        expect(result.current.error).toContain('500')
      })
    })

    it('should handle 404 not found', async () => {
      mockEndpoint('/health', mockError(404, 'Not Found'))

      const { result } = renderHook(() => useBackendStatus(100))

      await waitFor(() => {
        expect(result.current.isConnected).toBe(false)
        expect(result.current.error).toContain('404')
      })
    })

    it('should handle 503 service unavailable', async () => {
      mockEndpoint('/health', mockError(503, 'Service Unavailable'))

      const { result } = renderHook(() => useBackendStatus(100))

      await waitFor(() => {
        expect(result.current.isConnected).toBe(false)
        expect(result.current.error).toContain('503')
      })
    })

    it('should handle network error', async () => {
      mockEndpoint('/health', mockNetworkError())

      const { result } = renderHook(() => useBackendStatus(100))

      await waitFor(() => {
        expect(result.current.isConnected).toBe(false)
        expect(result.current.error).toContain('Network Error')
      })
    })

    it('should handle timeout', async () => {
      mockEndpoint('/health', mockTimeout(200))

      const { result } = renderHook(() => useBackendStatus(50))

      await waitFor(() => {
        expect(result.current.isConnected).toBe(false)
        expect(result.current.error).toContain('timeout')
      })
    })
  })

  describe('Status Code Variations', () => {
    it('should handle 200 OK', async () => {
      mockEndpoint('/health', {
        status: 200,
        body: { status: 'healthy' },
        headers: { 'Content-Type': 'application/json' }
      })

      const { result } = renderHook(() => useBackendStatus(100))

      await waitFor(() => {
        expect(result.current.isConnected).toBe(true)
      })
    })

    it('should handle 201 Created', async () => {
      mockEndpoint('/health', {
        status: 201,
        body: { status: 'healthy' },
        headers: { 'Content-Type': 'application/json' }
      })

      const { result } = renderHook(() => useBackendStatus(100))

      await waitFor(() => {
        expect(result.current.isConnected).toBe(true)
      })
    })

    it('should handle 400 Bad Request', async () => {
      mockEndpoint('/health', mockError(400, 'Bad Request'))

      const { result } = renderHook(() => useBackendStatus(100))

      await waitFor(() => {
        expect(result.current.isConnected).toBe(false)
        expect(result.current.error).toContain('400')
      })
    })

    it('should handle 401 Unauthorized', async () => {
      mockEndpoint('/health', mockError(401, 'Unauthorized'))

      const { result } = renderHook(() => useBackendStatus(100))

      await waitFor(() => {
        expect(result.current.isConnected).toBe(false)
        expect(result.current.error).toContain('401')
      })
    })

    it('should handle 502 Bad Gateway', async () => {
      mockEndpoint('/health', mockError(502, 'Bad Gateway'))

      const { result } = renderHook(() => useBackendStatus(100))

      await waitFor(() => {
        expect(result.current.isConnected).toBe(false)
        expect(result.current.error).toContain('502')
      })
    })
  })

  describe('Timing and Retry Scenarios', () => {
    it('should handle periodic checks with changing status', async () => {
      let callCount = 0
      mockEndpoint('/health', () => {
        callCount++
        if (callCount === 1) {
          return mockSuccess({ status: 'healthy' })
        } else {
          return mockError(500, 'Service Down')
        }
      })

      const { result } = renderHook(() => useBackendStatus(100))

      // First call should succeed
      await waitFor(() => {
        expect(result.current.isConnected).toBe(true)
      })

      // Wait for second call
      await waitFor(() => {
        expect(result.current.isConnected).toBe(false)
        expect(result.current.error).toContain('500')
      }, { timeout: 300 })
    })

    it('should handle rapid successive calls', async () => {
      const mock = mockEndpoint('/health', mockSuccess({ status: 'healthy' }))

      const { result } = renderHook(() => useBackendStatus(50))

      // Should handle multiple rapid calls
      await waitFor(() => {
        expect(result.current.isConnected).toBe(true)
      })

      // Wait a bit and check it's still working
      await new Promise(resolve => setTimeout(resolve, 200))
      expect(result.current.isConnected).toBe(true)

      // Verify multiple calls were made
      expect(mock.getCallCount()).toBeGreaterThan(1)
    })

    it('should verify API call frequency matches interval', async () => {
      const mock = mockEndpoint('/health', mockSuccess({ status: 'healthy' }))

      const { result } = renderHook(() => useBackendStatus(100))

      // Wait for initial call
      await waitFor(() => {
        expect(result.current.isConnected).toBe(true)
      })

      // Wait for at least one more call
      await new Promise(resolve => setTimeout(resolve, 150))

      // Should have made at least 2 calls (initial + periodic)
      expect(mock.getCallCount()).toBeGreaterThanOrEqual(2)

      // All calls should be GET requests to /health
      const calls = mock.getCalls()
      calls.forEach(call => {
        expect(call.options?.method).toBe('GET')
        expect(call.url).toContain('/health')
      })
    })
  })
})
