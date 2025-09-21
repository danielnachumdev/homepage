import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { renderHook, act } from '@testing-library/react'
import { LogLevel } from '../../../src/lib/logger'
import { TestHandler } from '../../../src/lib/logger/handlers/TestHandler'
import { LoggerManagerImpl } from '../../../src/lib/logger/manager'
import { ConsoleHandler } from '../../../src/lib/logger/handlers/ConsoleHandler'
import { FileHandler } from '../../../src/lib/logger/handlers/FileHandler'

// Import the hooks after setting up the real logger system
import { useComponentLogger } from '../../../src/hooks/useLogger'
import { loggerManager, getLogger } from '../../../src/lib/logger'

describe('useLogger Integration Tests', () => {
  let testHandler: TestHandler
  let originalConsoleLog: any
  let originalConsoleError: any
  let consoleLogSpy: any
  let consoleErrorSpy: any

  beforeEach(() => {
    // Clear all existing handlers
    loggerManager.shutdown()

    // Create a fresh logger manager
    const freshManager = new LoggerManagerImpl()

    // Add test handler for capturing logs
    testHandler = new TestHandler(LogLevel.DEBUG)
    freshManager.addHandler(testHandler)

    // Mock console methods to capture output
    originalConsoleLog = console.log
    originalConsoleError = console.error
    consoleLogSpy = vi.fn()
    consoleErrorSpy = vi.fn()
    console.log = consoleLogSpy
    console.error = consoleErrorSpy
  })

  afterEach(() => {
    // Restore console methods
    console.log = originalConsoleLog
    console.error = originalConsoleError

    // Clean up
    testHandler.clear()
    vi.clearAllMocks()
  })

  describe('Logger Configuration Debugging', () => {
    it('should verify logger manager is properly configured', () => {
      // Check that we can get a logger
      const logger = getLogger('test-logger')
      expect(logger).toBeDefined()
      expect(logger.name).toBe('test-logger')
    })

    it('should verify handlers are working', () => {
      const logger = getLogger('handler-test')

      // Set logger to DEBUG level to capture all messages
      logger.setLevel(LogLevel.DEBUG)

      // Add the TestHandler to the logger
      logger.addHandler(testHandler)

      // Log a message
      logger.debug('Test debug message')
      logger.error('Test error message')

      // Check that logs were captured by TestHandler
      const records = testHandler.getCapturedRecords()
      expect(records).toHaveLength(2)
      expect(records[0].message).toBe('Test debug message')
      expect(records[0].level).toBe(LogLevel.DEBUG)
      expect(records[1].message).toBe('Test error message')
      expect(records[1].level).toBe(LogLevel.ERROR)
    })

    it('should verify console output for error level', () => {
      const logger = getLogger('console-test')

      // Add console handler for error level
      const consoleHandler = new ConsoleHandler(LogLevel.ERROR)
      logger.addHandler(consoleHandler)

      // Clear any previous calls
      consoleLogSpy.mockClear()
      consoleErrorSpy.mockClear()

      // Log messages at different levels
      act(() => {
        logger.debug('Debug message - should not appear in console')
        logger.info('Info message - should not appear in console')
        logger.warning('Warning message - should not appear in console')
        logger.error('Error message - should appear in console')
        logger.critical('Critical message - should appear in console')
      })

      // Check console.error was called for error and critical levels
      expect(consoleErrorSpy).toHaveBeenCalledTimes(2)
      expect(consoleErrorSpy).toHaveBeenCalledWith(expect.stringContaining('Error message'))
      expect(consoleErrorSpy).toHaveBeenCalledWith(expect.stringContaining('Critical message'))

      // Check console.log was not called for debug/info/warning
      expect(consoleLogSpy).not.toHaveBeenCalled()
    })
  })

  describe('useComponentLogger Integration', () => {
    it('should work with real logger system', () => {
      const { result } = renderHook(() => useComponentLogger('TestComponent'))
      const logger = result.current

      expect(logger).toBeDefined()
      expect(logger.name).toBe('component.TestComponent')

      // Set logger to DEBUG level to capture all messages
      logger.setLevel(LogLevel.DEBUG)

      // Add TestHandler to capture logs
      logger.addHandler(testHandler)

      // Test logging
      act(() => {
        logger.debug('Component debug message')
        logger.info('Component info message')
        logger.error('Component error message')
      })

      // Check that logs were captured
      const records = testHandler.getCapturedRecords()
      expect(records).toHaveLength(3)

      // Check logger names
      const loggerNames = records.map(r => r.name)
      expect(loggerNames).toEqual([
        'component.TestComponent',
        'component.TestComponent',
        'component.TestComponent'
      ])
    })

    it('should handle multiple component loggers', () => {
      const { result: result1 } = renderHook(() => useComponentLogger('Component1'))
      const { result: result2 } = renderHook(() => useComponentLogger('Component2'))

      const logger1 = result1.current
      const logger2 = result2.current

      // Set both loggers to DEBUG level to capture all messages
      logger1.setLevel(LogLevel.DEBUG)
      logger2.setLevel(LogLevel.DEBUG)

      // Add TestHandler to both loggers
      logger1.addHandler(testHandler)
      logger2.addHandler(testHandler)

      expect(logger1.name).toBe('component.Component1')
      expect(logger2.name).toBe('component.Component2')

      act(() => {
        logger1.debug('Message from Component1')
        logger2.debug('Message from Component2')
      })

      const records = testHandler.getCapturedRecords()
      expect(records).toHaveLength(2)
      expect(records[0].name).toBe('component.Component1')
      expect(records[1].name).toBe('component.Component2')
    })

    it('should maintain separate logger instances', () => {
      const { result: result1 } = renderHook(() => useComponentLogger('Component1'))
      const { result: result2 } = renderHook(() => useComponentLogger('Component2'))

      const logger1 = result1.current
      const logger2 = result2.current

      // They should be different instances
      expect(logger1).not.toBe(logger2)

      // But both should be valid loggers
      expect(typeof logger1.debug).toBe('function')
      expect(typeof logger2.debug).toBe('function')
    })
  })

  describe('Log Level Filtering', () => {
    it('should respect log level filtering', () => {
      const logger = getLogger('level-test')

      // Add TestHandler to capture logs
      logger.addHandler(testHandler)

      // Set logger to ERROR level
      logger.setLevel(LogLevel.ERROR)

      act(() => {
        logger.debug('Debug message - should be filtered')
        logger.info('Info message - should be filtered')
        logger.warning('Warning message - should be filtered')
        logger.error('Error message - should pass')
        logger.critical('Critical message - should pass')
      })

      // Only error and critical should be captured
      const records = testHandler.getEmittedRecords()
      expect(records).toHaveLength(2)
      expect(records[0].message).toBe('Error message - should pass')
      expect(records[1].message).toBe('Critical message - should pass')
    })

    it('should handle different log levels correctly', () => {
      const logger = getLogger('level-test-2')

      // Add TestHandler to capture logs
      logger.addHandler(testHandler)

      // Test each level
      const levels = [
        { level: LogLevel.DEBUG, message: 'Debug message' },
        { level: LogLevel.INFO, message: 'Info message' },
        { level: LogLevel.WARNING, message: 'Warning message' },
        { level: LogLevel.ERROR, message: 'Error message' },
        { level: LogLevel.CRITICAL, message: 'Critical message' }
      ]

      levels.forEach(({ level, message }) => {
        logger.setLevel(level)
        testHandler.clear()

        act(() => {
          logger.debug('Debug message')
          logger.info('Info message')
          logger.warning('Warning message')
          logger.error('Error message')
          logger.critical('Critical message')
        })

        const records = testHandler.getEmittedRecords()
        const expectedCount = 5 - level // DEBUG=0, INFO=1, etc.
        expect(records).toHaveLength(expectedCount)
      })
    })
  })

  describe('File Handler Integration', () => {
    it('should test file handler initialization', () => {

      // Mock window.location for file handler
      Object.defineProperty(window, 'location', {
        value: {
          origin: 'http://localhost:3000'
        },
        writable: true
      })

      // Create file handler
      const fileHandler = new FileHandler('test.log', LogLevel.DEBUG, 100)

      // Check that it was initialized with a full path
      expect(fileHandler.getFullPath()).toContain('http://localhost:3000')
      expect(fileHandler.getFullPath()).toContain('test-')
      expect(fileHandler.getFullPath()).toContain('.log')
    })

    it('should test file handler with component logger', () => {

      // Mock window.location
      Object.defineProperty(window, 'location', {
        value: {
          origin: 'http://localhost:3000'
        },
        writable: true
      })

      const fileHandler = new FileHandler('component-test.log', LogLevel.DEBUG, 100)
      const logger = getLogger('file-test')
      logger.addHandler(fileHandler)

      const { result } = renderHook(() => useComponentLogger('FileTestComponent'))
      const componentLogger = result.current

      act(() => {
        componentLogger.debug('File test message')
        componentLogger.info('File info message')
      })

      // The file handler should have received the logs
      // (We can't easily test the actual file download in a test environment)
      expect(componentLogger.name).toBe('component.FileTestComponent')
    })
  })

  describe('Error Scenarios', () => {
    it('should handle logger creation errors gracefully', () => {
      // Test that the hook propagates errors when getLogger throws
      const mockGetLogger = vi.fn().mockImplementation(() => {
        throw new Error('Logger creation failed')
      })

      // Mock the logger module to return our error-throwing function
      vi.doMock('../../../src/lib/logger', () => ({
        getLogger: mockGetLogger,
        LogLevel: LogLevel
      }))

      // The hook should propagate the error from getLogger
      expect(() => {
        renderHook(() => useComponentLogger('ErrorComponent'))
      }).toThrow('Logger creation failed')

      // Verify the mock was called
      expect(mockGetLogger).toHaveBeenCalledWith('component.ErrorComponent')

      // Restore mocks
      vi.restoreAllMocks()
    })

    it('should handle logging errors gracefully', () => {
      const { result } = renderHook(() => useComponentLogger('ErrorTestComponent'))
      const logger = result.current

      // Mock a handler to throw an error
      const errorHandler = {
        level: LogLevel.DEBUG,
        handle: vi.fn().mockImplementation(() => {
          throw new Error('Handler error')
        }),
        emit: vi.fn()
      }

      logger.addHandler(errorHandler)

      // This should not throw, but the error should be caught
      expect(() => {
        act(() => {
          logger.debug('Test message')
        })
      }).not.toThrow()

      // Verify the handler was called despite the error
      expect(errorHandler.handle).toHaveBeenCalled()
    })
  })
})
