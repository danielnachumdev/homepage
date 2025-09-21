import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { renderHook } from '@testing-library/react'
import { LogLevel } from '../../../src/lib/logger'
import { TestHandler } from '../../../src/lib/logger/handlers/TestHandler'

// Mock the logger module before importing the hooks
vi.mock('../../../src/lib/logger', () => {
  const mockLogger = {
    name: 'test-logger',
    level: 0, // LogLevel.DEBUG
    handlers: [],
    propagate: false,
    filters: [],
    parent: undefined,
    children: new Map(),
    debug: vi.fn(),
    info: vi.fn(),
    warning: vi.fn(),
    error: vi.fn(),
    critical: vi.fn(),
    log: vi.fn(),
    addHandler: vi.fn(),
    removeHandler: vi.fn(),
    setLevel: vi.fn(),
    addFilter: vi.fn(),
    removeFilter: vi.fn(),
    isEnabledFor: vi.fn()
  }

  const mockGetLogger = vi.fn().mockReturnValue(mockLogger)

  return {
    LogLevel: {
      DEBUG: 0,
      INFO: 1,
      WARNING: 2,
      ERROR: 3,
      CRITICAL: 4,
      NOTSET: 5
    },
    getLogger: mockGetLogger,
    loggerManager: {
      getLogger: mockGetLogger
    }
  }
})

// Import the hooks after mocking
import { useLogger, useLoggerWithLevel, useComponentLogger } from '../../../src/hooks/useLogger'

describe('useLogger Hooks', () => {
  let testHandler: TestHandler
  let mockLogger: any
  let mockGetLogger: any

  beforeEach(async () => {
    // Reset all mocks
    vi.clearAllMocks()

    // Create a test handler to capture logs
    testHandler = new TestHandler(LogLevel.DEBUG)

    // Get the mocked functions
    const { getLogger } = await import('../../../src/lib/logger')
    mockGetLogger = vi.mocked(getLogger)

    // Create a fresh mock logger for each test
    mockLogger = {
      name: 'test-logger',
      level: LogLevel.DEBUG,
      handlers: [testHandler],
      propagate: false,
      filters: [],
      parent: undefined,
      children: new Map(),
      debug: vi.fn(),
      info: vi.fn(),
      warning: vi.fn(),
      error: vi.fn(),
      critical: vi.fn(),
      log: vi.fn(),
      addHandler: vi.fn(),
      removeHandler: vi.fn(),
      setLevel: vi.fn(),
      addFilter: vi.fn(),
      removeFilter: vi.fn(),
      isEnabledFor: vi.fn()
    }

    // Reset the mock function
    mockGetLogger.mockReturnValue(mockLogger)
  })

  afterEach(() => {
    vi.resetAllMocks()
  })

  describe('useLogger', () => {
    it('should return a logger instance', () => {
      const { result } = renderHook(() => useLogger('test-component'))

      expect(result.current).toBe(mockLogger)
      expect(mockGetLogger).toHaveBeenCalledWith('test-component')
    })

    it('should return a logger with default name when no name provided', () => {
      const { result } = renderHook(() => useLogger())

      expect(result.current).toBe(mockLogger)
      expect(mockGetLogger).toHaveBeenCalledWith(undefined)
    })

    it('should memoize the logger based on name', () => {
      const { rerender } = renderHook(
        ({ name }) => useLogger(name),
        { initialProps: { name: 'test1' } }
      )

      expect(mockGetLogger).toHaveBeenCalledTimes(1)
      expect(mockGetLogger).toHaveBeenCalledWith('test1')

      // Rerender with same name - should not call getLogger again
      rerender({ name: 'test1' })
      expect(mockGetLogger).toHaveBeenCalledTimes(1)

      // Rerender with different name - should call getLogger again
      rerender({ name: 'test2' })
      expect(mockGetLogger).toHaveBeenCalledTimes(2)
      expect(mockGetLogger).toHaveBeenCalledWith('test2')
    })

    it('should handle undefined name', () => {
      const { result } = renderHook(() => useLogger(undefined))

      expect(result.current).toBe(mockLogger)
      expect(mockGetLogger).toHaveBeenCalledWith(undefined)
    })

    it('should handle empty string name', () => {
      const { result } = renderHook(() => useLogger(''))

      expect(result.current).toBe(mockLogger)
      expect(mockGetLogger).toHaveBeenCalledWith('')
    })
  })

  describe('useLoggerWithLevel', () => {
    it('should return a logger with set level', () => {
      const { result } = renderHook(() => useLoggerWithLevel('test-component', LogLevel.ERROR))

      expect(result.current).toBe(mockLogger)
      expect(mockGetLogger).toHaveBeenCalledWith('test-component')
      expect(mockLogger.setLevel).toHaveBeenCalledWith(LogLevel.ERROR)
    })

    it('should memoize based on name and level', () => {
      const { rerender } = renderHook(
        ({ name, level }) => useLoggerWithLevel(name, level),
        { initialProps: { name: 'test1', level: LogLevel.DEBUG } }
      )

      expect(mockGetLogger).toHaveBeenCalledTimes(1)
      expect(mockLogger.setLevel).toHaveBeenCalledTimes(1)

      // Rerender with same name and level - should not call getLogger again
      rerender({ name: 'test1', level: LogLevel.DEBUG })
      expect(mockGetLogger).toHaveBeenCalledTimes(1)
      expect(mockLogger.setLevel).toHaveBeenCalledTimes(1)

      // Rerender with different level - should call getLogger and setLevel again
      rerender({ name: 'test1', level: LogLevel.ERROR })
      expect(mockGetLogger).toHaveBeenCalledTimes(2) // Called again due to level change
      expect(mockLogger.setLevel).toHaveBeenCalledTimes(2)
    })

    it('should handle all log levels', () => {
      const levels = [LogLevel.DEBUG, LogLevel.INFO, LogLevel.WARNING, LogLevel.ERROR, LogLevel.CRITICAL]

      levels.forEach(level => {
        const { result } = renderHook(() => useLoggerWithLevel('test', level))
        expect(result.current).toBe(mockLogger)
        expect(mockLogger.setLevel).toHaveBeenCalledWith(level)
      })
    })
  })

  describe('useComponentLogger', () => {
    it('should return a logger with component prefix', () => {
      const { result } = renderHook(() => useComponentLogger('MyComponent'))

      expect(result.current).toBe(mockLogger)
      expect(mockGetLogger).toHaveBeenCalledWith('component.MyComponent')
    })

    it('should handle different component names', () => {
      const components = ['Header', 'Footer', 'Sidebar', 'MainContent']

      components.forEach(componentName => {
        const { result } = renderHook(() => useComponentLogger(componentName))
        expect(result.current).toBe(mockLogger)
        expect(mockGetLogger).toHaveBeenCalledWith(`component.${componentName}`)
      })
    })

    it('should memoize based on component name', () => {
      const { rerender } = renderHook(
        ({ componentName }) => useComponentLogger(componentName),
        { initialProps: { componentName: 'TestComponent' } }
      )

      expect(mockGetLogger).toHaveBeenCalledTimes(1)
      expect(mockGetLogger).toHaveBeenCalledWith('component.TestComponent')

      // Rerender with same component name - should not call getLogger again
      rerender({ componentName: 'TestComponent' })
      expect(mockGetLogger).toHaveBeenCalledTimes(1)

      // Rerender with different component name - should call getLogger again
      rerender({ componentName: 'OtherComponent' })
      expect(mockGetLogger).toHaveBeenCalledTimes(2)
      expect(mockGetLogger).toHaveBeenCalledWith('component.OtherComponent')
    })

    it('should handle empty component name', () => {
      const { result } = renderHook(() => useComponentLogger(''))

      expect(result.current).toBe(mockLogger)
      expect(mockGetLogger).toHaveBeenCalledWith('component.')
    })

    it('should handle special characters in component names', () => {
      const specialNames = ['My-Component', 'My_Component', 'My.Component', 'My Component']

      specialNames.forEach(name => {
        const { result } = renderHook(() => useComponentLogger(name))
        expect(result.current).toBe(mockLogger)
        expect(mockGetLogger).toHaveBeenCalledWith(`component.${name}`)
      })
    })
  })

  describe('Logger Functionality', () => {
    it('should call logger methods correctly', () => {
      const { result } = renderHook(() => useLogger('test-component'))
      const logger = result.current

      // Test all logging methods
      logger.debug('Debug message', { data: 'test' })
      logger.info('Info message', { data: 'test' })
      logger.warning('Warning message', { data: 'test' })
      logger.error('Error message', { data: 'test' })
      logger.critical('Critical message', { data: 'test' })

      expect(mockLogger.debug).toHaveBeenCalledWith('Debug message', { data: 'test' })
      expect(mockLogger.info).toHaveBeenCalledWith('Info message', { data: 'test' })
      expect(mockLogger.warning).toHaveBeenCalledWith('Warning message', { data: 'test' })
      expect(mockLogger.error).toHaveBeenCalledWith('Error message', { data: 'test' })
      expect(mockLogger.critical).toHaveBeenCalledWith('Critical message', { data: 'test' })
    })

    it('should handle logger configuration methods', () => {
      const { result } = renderHook(() => useLogger('test-component'))
      const logger = result.current

      logger.addHandler(testHandler)
      logger.removeHandler(testHandler)
      logger.setLevel(LogLevel.ERROR)

      expect(mockLogger.addHandler).toHaveBeenCalledWith(testHandler)
      expect(mockLogger.removeHandler).toHaveBeenCalledWith(testHandler)
      expect(mockLogger.setLevel).toHaveBeenCalledWith(LogLevel.ERROR)
    })

    it('should check if level is enabled', () => {
      const { result } = renderHook(() => useLogger('test-component'))
      const logger = result.current

      mockLogger.isEnabledFor.mockReturnValue(true)

      const isEnabled = logger.isEnabledFor(LogLevel.DEBUG)
      expect(mockLogger.isEnabledFor).toHaveBeenCalledWith(LogLevel.DEBUG)
      expect(isEnabled).toBe(true)
    })
  })

  describe('Integration with TestHandler', () => {
    it('should capture logs when using TestHandler', () => {
      // Create a mock logger that actually calls handlers
      const realLogger = {
        ...mockLogger,
        handlers: [testHandler],
        debug: vi.fn().mockImplementation((message, data) => {
          testHandler.handle({
            name: 'integration-test',
            level: LogLevel.DEBUG,
            message,
            data,
            timestamp: new Date(),
            pathname: '',
            line: 0,
            column: 0
          })
        }),
        info: vi.fn().mockImplementation((message, data) => {
          testHandler.handle({
            name: 'integration-test',
            level: LogLevel.INFO,
            message,
            data,
            timestamp: new Date(),
            pathname: '',
            line: 0,
            column: 0
          })
        })
      }

      mockGetLogger.mockReturnValue(realLogger)

      const { result } = renderHook(() => useLogger('integration-test'))
      const logger = result.current

      logger.debug('Test debug message')
      logger.info('Test info message')

      const records = testHandler.getCapturedRecords()
      expect(records).toHaveLength(2)
      expect(records[0].message).toBe('Test debug message')
      expect(records[1].message).toBe('Test info message')
    })

    it('should handle multiple log levels with TestHandler', () => {
      // Create a mock logger that actually calls handlers
      const realLogger = {
        ...mockLogger,
        handlers: [testHandler],
        debug: vi.fn().mockImplementation((message, data) => {
          testHandler.handle({
            name: 'multi-level-test',
            level: LogLevel.DEBUG,
            message,
            data,
            timestamp: new Date(),
            pathname: '',
            line: 0,
            column: 0
          })
        }),
        info: vi.fn().mockImplementation((message, data) => {
          testHandler.handle({
            name: 'multi-level-test',
            level: LogLevel.INFO,
            message,
            data,
            timestamp: new Date(),
            pathname: '',
            line: 0,
            column: 0
          })
        }),
        warning: vi.fn().mockImplementation((message, data) => {
          testHandler.handle({
            name: 'multi-level-test',
            level: LogLevel.WARNING,
            message,
            data,
            timestamp: new Date(),
            pathname: '',
            line: 0,
            column: 0
          })
        }),
        error: vi.fn().mockImplementation((message, data) => {
          testHandler.handle({
            name: 'multi-level-test',
            level: LogLevel.ERROR,
            message,
            data,
            timestamp: new Date(),
            pathname: '',
            line: 0,
            column: 0
          })
        }),
        critical: vi.fn().mockImplementation((message, data) => {
          testHandler.handle({
            name: 'multi-level-test',
            level: LogLevel.CRITICAL,
            message,
            data,
            timestamp: new Date(),
            pathname: '',
            line: 0,
            column: 0
          })
        })
      }

      mockGetLogger.mockReturnValue(realLogger)

      const { result } = renderHook(() => useLogger('multi-level-test'))
      const logger = result.current

      logger.debug('Debug message')
      logger.info('Info message')
      logger.warning('Warning message')
      logger.error('Error message')
      logger.critical('Critical message')

      const records = testHandler.getCapturedRecords()
      expect(records).toHaveLength(5)
      expect(records.map(r => r.level)).toEqual([
        LogLevel.DEBUG,
        LogLevel.INFO,
        LogLevel.WARNING,
        LogLevel.ERROR,
        LogLevel.CRITICAL
      ])
    })
  })

  describe('Error Handling', () => {
    it('should handle getLogger throwing an error', () => {
      mockGetLogger.mockImplementation(() => {
        throw new Error('Logger creation failed')
      })

      expect(() => {
        renderHook(() => useLogger('test'))
      }).toThrow('Logger creation failed')
    })

    it('should handle logger methods throwing errors', () => {
      const { result } = renderHook(() => useLogger('test-component'))
      const logger = result.current

      mockLogger.debug.mockImplementation(() => {
        throw new Error('Debug failed')
      })

      expect(() => {
        logger.debug('Test message')
      }).toThrow('Debug failed')
    })
  })
})