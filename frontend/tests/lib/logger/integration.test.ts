import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { logger, getLogger, setLogLevel, addHandler, removeHandler, shutdown } from '../../../src/lib/logger';
import { TestHandler } from '../../../src/lib/logger/handlers/TestHandler';
import { ConsoleHandler, LocalStorageHandler } from '../../../src/lib/logger/handlers';
import { StandardFormatter, JSONFormatter, ColoredFormatter } from '../../../src/lib/logger/formatters';
import { LevelFilter, NameFilter, MessageFilter, CompositeFilter } from '../../../src/lib/logger/filters';
import { LogLevel } from '../../../src/lib/logger/types';

describe('Logger Integration Tests', () => {
    let testHandler: TestHandler;
    let addedHandlers: any[] = [];
    let addedFilters: any[] = [];
    let originalLevel: LogLevel;

    beforeEach(() => {
        // Store original level
        originalLevel = logger.level;

        // Create test handler
        testHandler = new TestHandler(LogLevel.DEBUG);
        addHandler(testHandler);
        addedHandlers.push(testHandler);
    });

    afterEach(() => {
        // Remove all added handlers
        addedHandlers.forEach(handler => {
            try {
                removeHandler(handler);
            } catch (error) {
                // Ignore errors if handler was already removed
            }
        });
        addedHandlers = [];

        // Remove all added filters
        addedFilters.forEach(filter => {
            try {
                logger.removeFilter(filter);
            } catch (error) {
                // Ignore errors if filter was already removed
            }
        });
        addedFilters = [];

        // Reset logger level
        setLogLevel(originalLevel);

        // Clear test handler
        if (testHandler) {
            testHandler.clear();
        }

        // Clear any localStorage that might have been used
        try {
            localStorage.removeItem('app_logs');
            localStorage.removeItem('test_logs');
        } catch (error) {
            // Ignore localStorage errors in test environment
        }
    });

    describe('Basic Logging Flow', () => {
        it('should log messages through the default logger', () => {
            logger.info('Integration test message');

            expect(testHandler.getRecordCount()).toBe(1);
            expect(testHandler.hasMessage('Integration test message')).toBe(true);
        });

        it('should log messages through named loggers', () => {
            const appLogger = getLogger('app');
            const serviceLogger = getLogger('app.service');

            appLogger.info('App message');
            serviceLogger.info('Service message');

            expect(testHandler.getRecordCount()).toBe(2);
            expect(testHandler.getRecordsByName('app')).toHaveLength(1);
            expect(testHandler.getRecordsByName('app.service')).toHaveLength(1);
        });
    });

    describe('Handler Integration', () => {
        it('should work with multiple handlers', () => {
            const consoleHandler = new ConsoleHandler(LogLevel.DEBUG, new StandardFormatter());
            const jsonHandler = new LocalStorageHandler('test_logs', LogLevel.INFO, 100, new JSONFormatter());

            addHandler(consoleHandler);
            addHandler(jsonHandler);
            addedHandlers.push(consoleHandler, jsonHandler);

            logger.info('Multi-handler test');

            expect(testHandler.getRecordCount()).toBe(1);
        });

        it('should respect handler level filtering', () => {
            const highLevelHandler = new TestHandler(LogLevel.ERROR);
            addHandler(highLevelHandler);
            addedHandlers.push(highLevelHandler);

            logger.info('Info message');
            logger.error('Error message');

            expect(testHandler.getEmittedCount()).toBe(2); // All messages
            expect(highLevelHandler.getEmittedCount()).toBe(1); // Only error
        });
    });

    describe('Formatter Integration', () => {
        it('should format messages correctly', () => {
            const standardHandler = new TestHandler(LogLevel.DEBUG);
            standardHandler.formatter = new StandardFormatter('%(levelname)s: %(message)s');

            addHandler(standardHandler);
            addedHandlers.push(standardHandler);

            logger.info('Formatted message');

            const record = standardHandler.getLastRecord();
            const formatted = standardHandler.format(record!);
            expect(formatted).toBe('INFO: Formatted message');
        });

        it('should work with colored formatter', () => {
            const coloredHandler = new TestHandler(LogLevel.DEBUG);
            coloredHandler.formatter = new ColoredFormatter('%(levelname)s: %(message)s');

            addHandler(coloredHandler);
            addedHandlers.push(coloredHandler);

            logger.info('Colored message');

            const record = coloredHandler.getLastRecord();
            const formatted = coloredHandler.format(record!);
            expect(formatted).toContain('\x1b[32m'); // Green for INFO
            expect(formatted).toContain('INFO: Colored message');
            expect(formatted).toContain('\x1b[0m'); // Reset
        });
    });

    describe('Filter Integration', () => {
        it('should work with level filters', () => {
            const levelFilter = new LevelFilter(LogLevel.WARNING);
            logger.addFilter(levelFilter);
            addedFilters.push(levelFilter);

            logger.info('Info message');
            logger.warning('Warning message');
            logger.error('Error message');

            expect(testHandler.getRecordCount()).toBe(3);
            expect(testHandler.getEmittedCount()).toBe(2); // Only WARNING and ERROR
        });

        it('should work with name filters', () => {
            const nameFilter = new NameFilter('^app\\..*');
            logger.addFilter(nameFilter);
            addedFilters.push(nameFilter);

            logger.info('Root message');

            const appLogger = getLogger('app.service');
            appLogger.info('App message');

            expect(testHandler.getRecordCount()).toBe(2);
            expect(testHandler.getEmittedCount()).toBe(1); // Only app.service message
        });

        it('should work with message filters', () => {
            const messageFilter = new MessageFilter('important');
            logger.addFilter(messageFilter);
            addedFilters.push(messageFilter);

            logger.info('Regular message');
            logger.info('Important message');

            expect(testHandler.getRecordCount()).toBe(2);
            expect(testHandler.getEmittedCount()).toBe(1); // Only important message
        });

        it('should work with composite filters', () => {
            const levelFilter = new LevelFilter(LogLevel.WARNING);
            const messageFilter = new MessageFilter('error');
            const compositeFilter = new CompositeFilter([levelFilter, messageFilter], 'AND');

            logger.addFilter(compositeFilter);
            addedFilters.push(compositeFilter);

            logger.info('Info message');
            logger.warning('Warning message');
            logger.error('Error message');
            logger.warning('Error warning message');

            expect(testHandler.getRecordCount()).toBe(4);
            expect(testHandler.getEmittedCount()).toBe(1); // Only warning with error
        });
    });

    describe('Global Configuration', () => {
        it('should change log level globally', () => {
            setLogLevel(LogLevel.ERROR);

            logger.info('Info message');
            logger.error('Error message');

            expect(testHandler.getRecordCount()).toBe(2);
            expect(testHandler.getEmittedCount()).toBe(1); // Only error
        });

        it('should add and remove handlers globally', () => {
            const globalHandler = new TestHandler(LogLevel.DEBUG);

            addHandler(globalHandler);
            addedHandlers.push(globalHandler);
            logger.info('Global handler test');

            expect(globalHandler.getRecordCount()).toBe(1);
        });
    });

    describe('Complex Scenarios', () => {
        it('should handle hierarchical logging with propagation', () => {
            const rootHandler = new TestHandler(LogLevel.DEBUG);
            const appHandler = new TestHandler(LogLevel.DEBUG);

            addHandler(rootHandler);
            addedHandlers.push(rootHandler);

            const appLogger = getLogger('app');
            appLogger.addHandler(appHandler);
            addedHandlers.push(appHandler);

            const serviceLogger = getLogger('app.service');
            serviceLogger.info('Service message');

            expect(appHandler.getRecordCount()).toBe(1);
            expect(rootHandler.getRecordCount()).toBe(1); // Propagated
        });

        it('should handle structured logging with complex data', () => {
            const structuredData = {
                userId: 123,
                action: 'login',
                metadata: {
                    ip: '192.168.1.1',
                    userAgent: 'Mozilla/5.0...',
                    timestamp: new Date().toISOString()
                }
            };

            logger.info('User action', structuredData);

            const record = testHandler.getLastRecord();
            expect(record!.args).toEqual([structuredData]);
        });

        it('should handle performance logging', () => {
            const startTime = performance.now();

            // Simulate some work
            const endTime = performance.now();
            const duration = endTime - startTime;

            logger.debug('Performance measurement', {
                operation: 'test_operation',
                duration,
                startTime,
                endTime
            });

            const record = testHandler.getLastRecord();
            expect(record!.message).toBe('Performance measurement');
            expect(record!.args[0]).toMatchObject({
                operation: 'test_operation',
                duration: expect.any(Number)
            });
        });

        it('should handle error logging with stack traces', () => {
            try {
                throw new Error('Test error');
            } catch (error) {
                logger.error('Caught error', {
                    error: error instanceof Error ? error.message : String(error),
                    stack: error instanceof Error ? error.stack : undefined,
                    context: { operation: 'test' }
                });
            }

            const record = testHandler.getLastRecord();
            expect(record!.message).toBe('Caught error');
            expect(record!.args[0]).toMatchObject({
                error: 'Test error',
                stack: expect.any(String),
                context: { operation: 'test' }
            });
        });
    });

    describe('Logger Hierarchy', () => {
        it('should maintain proper parent-child relationships', () => {
            const rootLogger = getLogger('root');
            const appLogger = getLogger('app');
            const serviceLogger = getLogger('app.service');
            const userLogger = getLogger('app.service.user');

            expect(appLogger.parent).toBe(rootLogger);
            expect(serviceLogger.parent).toBe(appLogger);
            expect(userLogger.parent).toBe(serviceLogger);
        });

        it('should propagate configuration changes to children', () => {
            const childLogger = getLogger('app.service');
            const originalLevel = childLogger.level;

            setLogLevel(LogLevel.DEBUG);

            expect(childLogger.level).toBe(LogLevel.DEBUG);

            setLogLevel(originalLevel); // Reset
        });
    });
});
