import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { LoggerManagerImpl } from '../../../src/lib/logger/manager';
import { TestHandler } from '../../../src/lib/logger/handlers/TestHandler';
import { LogLevel } from '../../../src/lib/logger/types';

describe('LoggerManagerImpl', () => {
    let manager: LoggerManagerImpl;
    let testHandler: TestHandler;

    beforeEach(() => {
        manager = new LoggerManagerImpl();
        testHandler = new TestHandler(LogLevel.DEBUG);
    });

    afterEach(() => {
        // Shutdown manager to clean up all loggers and handlers
        if (manager) {
            manager.shutdown();
        }

        // Clear test handler
        if (testHandler) {
            testHandler.clear();
        }
    });

    describe('Constructor', () => {
        it('should create root logger', () => {
            const rootLogger = manager.getLogger('root');
            expect(rootLogger).toBeDefined();
            expect(rootLogger.name).toBe('root');
        });

        it('should have default level', () => {
            const rootLogger = manager.getLogger('root');
            expect(rootLogger.level).toBe(LogLevel.WARNING);
        });
    });

    describe('getLogger', () => {
        it('should return existing logger', () => {
            const logger1 = manager.getLogger('test');
            const logger2 = manager.getLogger('test');
            expect(logger1).toBe(logger2);
        });

        it('should create new logger with correct name', () => {
            const logger = manager.getLogger('my-logger');
            expect(logger.name).toBe('my-logger');
        });

        it('should set parent logger for hierarchical names', () => {
            const parentLogger = manager.getLogger('app');
            const childLogger = manager.getLogger('app.service');

            expect(childLogger.parent).toBe(parentLogger);
        });

        it('should set root as parent for top-level loggers', () => {
            const logger = manager.getLogger('test');
            const rootLogger = manager.getLogger('root');

            expect(logger.parent).toBe(rootLogger);
        });

        it('should handle complex hierarchical names', () => {
            const grandParent = manager.getLogger('app');
            const parent = manager.getLogger('app.service');
            const child = manager.getLogger('app.service.user');

            expect(parent.parent).toBe(grandParent);
            expect(child.parent).toBe(parent);
        });

        it('should return root logger when no name provided', () => {
            const logger = manager.getLogger();
            expect(logger.name).toBe('root');
        });
    });

    describe('setLevel', () => {
        it('should set level for root logger', () => {
            manager.setLevel(LogLevel.DEBUG);
            const rootLogger = manager.getLogger('root');
            expect(rootLogger.level).toBe(LogLevel.DEBUG);
        });

        it('should set level for all existing loggers', () => {
            const logger1 = manager.getLogger('test1');
            const logger2 = manager.getLogger('test2');

            manager.setLevel(LogLevel.INFO);

            expect(logger1.level).toBe(LogLevel.INFO);
            expect(logger2.level).toBe(LogLevel.INFO);
        });

        it('should set level for new loggers', () => {
            manager.setLevel(LogLevel.DEBUG);
            const newLogger = manager.getLogger('new-logger');
            expect(newLogger.level).toBe(LogLevel.DEBUG);
        });
    });

    describe('addHandler', () => {
        it('should add handler to root logger', () => {
            manager.addHandler(testHandler);
            const rootLogger = manager.getLogger('root');
            expect(rootLogger.handlers).toContain(testHandler);
        });

        it('should add handler to all existing loggers', () => {
            const logger1 = manager.getLogger('test1');
            const logger2 = manager.getLogger('test2');

            manager.addHandler(testHandler);

            expect(logger1.handlers).toContain(testHandler);
            expect(logger2.handlers).toContain(testHandler);
        });

        it('should add handler to new loggers', () => {
            manager.addHandler(testHandler);
            const newLogger = manager.getLogger('new-logger');
            expect(newLogger.handlers).toContain(testHandler);
        });
    });

    describe('removeHandler', () => {
        it('should remove handler from root logger', () => {
            manager.addHandler(testHandler);
            manager.removeHandler(testHandler);
            const rootLogger = manager.getLogger('root');
            expect(rootLogger.handlers).not.toContain(testHandler);
        });

        it('should remove handler from all existing loggers', () => {
            const logger1 = manager.getLogger('test1');
            const logger2 = manager.getLogger('test2');

            manager.addHandler(testHandler);
            manager.removeHandler(testHandler);

            expect(logger1.handlers).not.toContain(testHandler);
            expect(logger2.handlers).not.toContain(testHandler);
        });

        it('should not affect new loggers after removal', () => {
            manager.addHandler(testHandler);
            manager.removeHandler(testHandler);
            const newLogger = manager.getLogger('new-logger');
            expect(newLogger.handlers).not.toContain(testHandler);
        });
    });

    describe('shutdown', () => {
        it('should clear all loggers', () => {
            manager.getLogger('test1');
            manager.getLogger('test2');

            manager.shutdown();

            // Should create new loggers after shutdown
            const newLogger = manager.getLogger('test3');
            expect(newLogger).toBeDefined();
        });

        it('should close all handlers', () => {
            const closeSpy = vi.fn();
            const handler = {
                level: LogLevel.DEBUG,
                emit: vi.fn(),
                close: closeSpy
            };

            manager.addHandler(handler);
            manager.shutdown();

            expect(closeSpy).toHaveBeenCalled();
        });

        it('should handle handlers without close method', () => {
            const handler = {
                level: LogLevel.DEBUG,
                emit: vi.fn()
                // No close method
            };

            expect(() => {
                manager.addHandler(handler);
                manager.shutdown();
            }).not.toThrow();
        });

        it('should handle errors in handler close', () => {
            const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => { });
            const handler = {
                level: LogLevel.DEBUG,
                emit: vi.fn(),
                close: () => {
                    throw new Error('Close error');
                }
            };

            manager.addHandler(handler);
            manager.shutdown();

            expect(consoleSpy).toHaveBeenCalledWith('Error closing handler:', expect.any(Error));
            consoleSpy.mockRestore();
        });
    });

    describe('getParentName', () => {
        it('should return root for single-level names', () => {
            const parentName = manager['getParentName']('test');
            expect(parentName).toBe('root');
        });

        it('should return parent for multi-level names', () => {
            const parentName = manager['getParentName']('app.service.user');
            expect(parentName).toBe('app.service');
        });

        it('should return root for two-level names', () => {
            const parentName = manager['getParentName']('app.service');
            expect(parentName).toBe('app');
        });
    });

    describe('Logger Propagation', () => {
        it('should propagate logs to parent when enabled', () => {
            const parentHandler = new TestHandler(LogLevel.DEBUG);
            const childHandler = new TestHandler(LogLevel.DEBUG);

            manager.addHandler(parentHandler);

            const childLogger = manager.getLogger('app.service');
            childLogger.addHandler(childHandler);

            childLogger.info('Test message');

            expect(childHandler.getRecordCount()).toBe(1);
            expect(parentHandler.getRecordCount()).toBe(1); // Propagated to parent
        });

        it('should not propagate logs when disabled', () => {
            const parentHandler = new TestHandler(LogLevel.DEBUG);
            const childHandler = new TestHandler(LogLevel.DEBUG);

            manager.addHandler(parentHandler);

            const childLogger = manager.getLogger('app.service');
            childLogger.addHandler(childHandler);
            childLogger.propagate = false;

            childLogger.info('Test message');

            expect(childHandler.getRecordCount()).toBe(1);
            expect(parentHandler.getRecordCount()).toBe(0); // Not propagated
        });
    });

    describe('Multiple Handlers', () => {
        it('should add multiple handlers to all loggers', () => {
            const handler1 = new TestHandler(LogLevel.DEBUG);
            const handler2 = new TestHandler(LogLevel.INFO);

            manager.addHandler(handler1);
            manager.addHandler(handler2);

            const logger = manager.getLogger('test');
            expect(logger.handlers).toContain(handler1);
            expect(logger.handlers).toContain(handler2);
        });

        it('should remove specific handler while keeping others', () => {
            const handler1 = new TestHandler(LogLevel.DEBUG);
            const handler2 = new TestHandler(LogLevel.INFO);

            manager.addHandler(handler1);
            manager.addHandler(handler2);
            manager.removeHandler(handler1);

            const logger = manager.getLogger('test');
            expect(logger.handlers).not.toContain(handler1);
            expect(logger.handlers).toContain(handler2);
        });
    });
});
