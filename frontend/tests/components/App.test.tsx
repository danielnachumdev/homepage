import { describe, it, expect, beforeEach, afterEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import App from '../../src/App'
import {
  initFetchMock,
  cleanupFetchMock,
  resetFetchMock,
  mockEndpoint,
  mockSuccess,
  mockError
} from '../utils/fetch-mock'

describe('App Component', () => {
  beforeEach(() => {
    initFetchMock()
  })

  afterEach(() => {
    resetFetchMock()
  })

  afterAll(() => {
    cleanupFetchMock()
  })

  describe('Basic Rendering', () => {
    it('should render homepage title', async () => {
      // Mock successful health check
      mockEndpoint('/health', mockSuccess({
        status: 'healthy',
        service: 'homepage-backend'
      }))

      render(<App />)

      expect(screen.getByText('Homepage')).toBeInTheDocument()
    })

    it('should render search component', async () => {
      // Mock successful health check
      mockEndpoint('/health', mockSuccess({
        status: 'healthy',
        service: 'homepage-backend'
      }))

      render(<App />)

      expect(screen.getByPlaceholderText(/search/i)).toBeInTheDocument()
    })
  })

  describe('Backend Status Integration', () => {
    it('should handle successful backend connection', async () => {
      // Mock successful health check
      mockEndpoint('/health', mockSuccess({
        status: 'healthy',
        service: 'homepage-backend'
      }))

      render(<App />)

      // Wait for the backend status to be checked
      await waitFor(() => {
        expect(screen.getByText('Homepage')).toBeInTheDocument()
      })
    })

    it('should handle backend connection errors gracefully', async () => {
      // Mock failed health check
      mockEndpoint('/health', mockError(500, 'Server Error'))

      render(<App />)

      // App should still render even if backend is down
      expect(screen.getByText('Homepage')).toBeInTheDocument()
    })

    it('should handle network errors gracefully', async () => {
      // Mock network error
      mockEndpoint('/health', {
        status: 0,
        shouldReject: true,
        error: new Error('Network Error')
      })

      render(<App />)

      // App should still render even with network errors
      expect(screen.getByText('Homepage')).toBeInTheDocument()
    })
  })

  describe('Component Integration', () => {
    it('should render all main components', async () => {
      // Mock successful API responses
      mockEndpoint('/health', mockSuccess({
        status: 'healthy',
        service: 'homepage-backend'
      }))

      mockEndpoint('/api/v1/settings/', mockSuccess({
        success: true,
        data: {
          theme: 'light',
          language: 'en',
          searchEngine: 'google',
          chromeProfiles: []
        }
      }))

      render(<App />)

      // Check for main components
      expect(screen.getByText('Homepage')).toBeInTheDocument()
      expect(screen.getByPlaceholderText(/search/i)).toBeInTheDocument()
    })

    it('should handle component loading states', async () => {
      // Mock delayed response
      mockEndpoint('/health', {
        status: 200,
        body: { status: 'healthy' },
        delay: 1000,
        headers: { 'Content-Type': 'application/json' }
      })

      render(<App />)

      // App should render immediately even with delayed API
      expect(screen.getByText('Homepage')).toBeInTheDocument()
    })
  })
})
