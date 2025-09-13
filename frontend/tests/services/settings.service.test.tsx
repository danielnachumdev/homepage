import { describe, it, expect, beforeEach, afterEach } from 'vitest'
import { settingsService } from '../../src/services/settings.service'
import {
  initFetchMock,
  cleanupFetchMock,
  resetFetchMock,
  mockEndpoint,
  mockSuccess,
  mockError,
  mockNetworkError
} from '../utils/fetch-mock'

describe('Settings Service', () => {
  beforeEach(() => {
    initFetchMock()
  })

  afterEach(() => {
    resetFetchMock()
  })

  afterAll(() => {
    cleanupFetchMock()
  })

  describe('getAllSettings', () => {
    it('should fetch all settings successfully', async () => {
      mockEndpoint('/api/v1/settings/', mockSuccess({
        success: true,
        message: 'Settings retrieved successfully',
        data: {
          theme: 'light',
          language: 'en',
          searchEngine: 'google',
          chromeProfiles: [
            { id: 'profile1', name: 'Work Profile' },
            { id: 'profile2', name: 'Personal Profile' }
          ]
        }
      }))

      const result = await settingsService.getAllSettings()

      expect(result.success).toBe(true)
      expect(result.data.theme).toBe('light')
      expect(result.data.chromeProfiles).toHaveLength(2)
    })

    it('should handle 500 server error', async () => {
      mockEndpoint('/api/v1/settings/', mockError(500, 'Internal Server Error'))

      await expect(settingsService.getAllSettings()).rejects.toThrow()
    })

    it('should handle 404 not found', async () => {
      mockEndpoint('/api/v1/settings/', mockError(404, 'Settings not found'))

      await expect(settingsService.getAllSettings()).rejects.toThrow()
    })

    it('should handle network error', async () => {
      mockEndpoint('/api/v1/settings/', mockNetworkError())

      await expect(settingsService.getAllSettings()).rejects.toThrow()
    })

    it('should handle malformed response', async () => {
      mockEndpoint('/api/v1/settings/', {
        status: 200,
        body: { invalid: 'response' },
        headers: { 'Content-Type': 'application/json' }
      })

      const result = await settingsService.getAllSettings()
      expect(result.invalid).toBe('response')
    })
  })

  describe('updateSetting', () => {
    it('should update setting successfully', async () => {
      mockEndpoint('/api/v1/settings/update', mockSuccess({
        success: true,
        message: 'Setting updated successfully',
        data: {
          key: 'theme',
          value: 'dark',
          updated_at: '2024-01-01T00:00:00Z'
        }
      }))

      const result = await settingsService.updateSetting({
        key: 'theme',
        value: 'dark'
      })

      expect(result.success).toBe(true)
      expect(result.data.key).toBe('theme')
      expect(result.data.value).toBe('dark')
    })

    it('should handle validation error', async () => {
      mockEndpoint('/api/v1/settings/update', mockError(400, 'Invalid setting value'))

      await expect(settingsService.updateSetting({
        key: 'theme',
        value: 'invalid-theme'
      })).rejects.toThrow()
    })

    it('should handle unauthorized error', async () => {
      mockEndpoint('/api/v1/settings/update', mockError(401, 'Unauthorized'))

      await expect(settingsService.updateSetting({
        key: 'theme',
        value: 'dark'
      })).rejects.toThrow()
    })

    it('should handle conflict error', async () => {
      mockEndpoint('/api/v1/settings/update', mockError(409, 'Setting conflict'))

      await expect(settingsService.updateSetting({
        key: 'theme',
        value: 'dark'
      })).rejects.toThrow()
    })
  })

  describe('Complex Scenarios', () => {
    it('should handle multiple API calls in sequence', async () => {
      let callCount = 0
      mockEndpoint('/api/v1/settings/', () => {
        callCount++
        if (callCount === 1) {
          return mockSuccess({
            success: true,
            data: { theme: 'light' }
          })
        } else {
          return mockError(500, 'Service unavailable')
        }
      })

      // First call should succeed
      const result1 = await settingsService.getAllSettings()
      expect(result1.success).toBe(true)

      // Second call should fail
      await expect(settingsService.getAllSettings()).rejects.toThrow()
    })

    it('should handle different response formats', async () => {
      mockEndpoint('/api/v1/settings/', mockSuccess({
        // Different response structure
        settings: {
          theme: 'dark',
          language: 'es'
        },
        metadata: {
          version: '2.0.0',
          lastUpdated: '2024-01-01T00:00:00Z'
        }
      }))

      const result = await settingsService.getAllSettings()

      expect(result.settings.theme).toBe('dark')
      expect(result.metadata.version).toBe('2.0.0')
    })

    it('should handle timeout scenarios', async () => {
      mockEndpoint('/api/v1/settings/', {
        status: 200,
        body: { success: true, data: {} },
        delay: 10000, // 10 second delay
        headers: { 'Content-Type': 'application/json' }
      })

      // This should timeout based on the RequestManager timeout
      await expect(settingsService.getAllSettings()).rejects.toThrow()
    })
  })

  describe('Edge Cases', () => {
    it('should handle empty settings response', async () => {
      mockEndpoint('/api/v1/settings/', mockSuccess({
        success: true,
        data: {}
      }))

      const result = await settingsService.getAllSettings()

      expect(result.success).toBe(true)
      expect(result.data).toEqual({})
    })

    it('should handle null response body', async () => {
      mockEndpoint('/api/v1/settings/', {
        status: 200,
        body: null,
        headers: { 'Content-Type': 'application/json' }
      })

      const result = await settingsService.getAllSettings()

      expect(result).toBeNull()
    })

    it('should handle very large response', async () => {
      const largeData = {
        success: true,
        data: {
          theme: 'light',
          // Simulate large data
          largeArray: new Array(1000).fill(0).map((_, i) => ({ id: i, value: `item-${i}` }))
        }
      }

      mockEndpoint('/api/v1/settings/', mockSuccess(largeData))

      const result = await settingsService.getAllSettings()

      expect(result.success).toBe(true)
      expect(result.data.largeArray).toHaveLength(1000)
    })
  })
})
