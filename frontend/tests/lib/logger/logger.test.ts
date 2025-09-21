import { describe, it, expect, beforeEach, afterEach } from 'vitest';
import { LoggerImpl } from '../../../src/lib/logger/logger';
import { TestHandler } from '../../../src/lib/logger/handlers/TestHandler';
import { LogLevel } from '../../../src/lib/logger/types';

describe('LoggerImpl', () => {
    let logger: LoggerImpl;
    let testHandler: TestHandler;

    beforeEach(() => {
        testHandler = new TestHandler(LogLevel.DEBUG);
        logger = new LoggerImpl({
            name: 'test-logger',
            level: LogLevel.DEBUG,
            handlers: [testHandler],
            propagate: false,
        });
    });

    afterEach(() => {
        // Clear test handler
        if (testHandler) {
            testHandler.clear();
        }

        // Clear any filters that might have been added
        if (logger) {
            logger.filters = [];
        }
    });

    describe('Basic Logging', () => {
        it('should log debug messages', () => {
            logger.debug('Debug message');

            expect(testHandler.getRecordCount()).toBe(1);
            expect(testHandler.getEmittedCount()).toBe(1);
            expect(testHandler.hasMessage('Debug message')).toBe(true);
            expect(testHandler.hasLevel(LogLevel.DEBUG)).toBe(true);
        });

        it('should log info messages', () => {
            logger.info('Info message');

            expect(testHandler.getRecordCount()).toBe(1);
            expect(testHandler.getEmittedCount()).toBe(1);
            expect(testHandler.hasMessage('Info message')).toBe(true);
            expect(testHandler.hasLevel(LogLevel.INFO)).toBe(true);
        });

        it('should log warning messages', () => {
            logger.warning('Warning message');

            expect(testHandler.getRecordCount()).toBe(1);
            expect(testHandler.getEmittedCount()).toBe(1);
            expect(testHandler.hasMessage('Warning message')).toBe(true);
            expect(testHandler.hasLevel(LogLevel.WARNING)).toBe(true);
        });

        it('should log error messages', () => {
            logger.error('Error message');

            expect(testHandler.getRecordCount()).toBe(1);
            expect(testHandler.getEmittedCount()).toBe(1);
            expect(testHandler.hasMessage('Error message')).toBe(true);
            expect(testHandler.hasLevel(LogLevel.ERROR)).toBe(true);
        });

        it('should log critical messages', () => {
            logger.critical('Critical message');

            expect(testHandler.getRecordCount()).toBe(1);
            expect(testHandler.getEmittedCount()).toBe(1);
            expect(testHandler.hasMessage('Critical message')).toBe(true);
            expect(testHandler.hasLevel(LogLevel.CRITICAL)).toBe(true);
        });

        it('should log with additional arguments', () => {
            logger.info('User action', { userId: 123, action: 'login' });

            const record = testHandler.getLastRecord();
            expect(record).toBeDefined();
            expect(record!.message).toBe('User action');
            expect(record!.args).toEqual([{ userId: 123, action: 'login' }]);
        });
    });

    describe('Level Filtering', () => {
        it('should respect logger level filtering', () => {
            logger.setLevel(LogLevel.WARNING);
            testHandler.level = LogLevel.WARNING;

            logger.debug('Debug message');
            logger.info('Info message');
            logger.warning('Warning message');
            logger.error('Error message');

            expect(testHandler.getRecordCount()).toBe(4);
            expect(testHandler.getEmittedCount()).toBe(2); // Only WARNING and ERROR

            const emittedRecords = testHandler.getEmittedRecords();
            expect(emittedRecords.every(record => record.level >= LogLevel.WARNING)).toBe(true);
        });

        it('should respect handler level filtering', () => {
            const highLevelHandler = new TestHandler(LogLevel.ERROR);
            logger.addHandler(highLevelHandler);

            logger.info('Info message');
            logger.warning('Warning message');
            logger.error('Error message');

            expect(testHandler.getEmittedCount()).toBe(3); // All messages
            expect(highLevelHandler.getEmittedCount()).toBe(1); // Only ERROR
        });
    });

    describe('Handler Management', () => {
        it('should add and remove handlers', () => {
            const newHandler = new TestHandler();

            logger.addHandler(newHandler);
            logger.info('Test message');

            expect(testHandler.getRecordCount()).toBe(1);
            expect(newHandler.getRecordCount()).toBe(1);

            logger.removeHandler(newHandler);
            logger.info('Another message');

            expect(testHandler.getRecordCount()).toBe(2);
            expect(newHandler.getRecordCount()).toBe(1); // Should not increase
        });
    });

    describe('Filter Management', () => {
        it('should add and apply filters', () => {
            const messageFilter = {
                filter: (record: any) => record.message.includes('important')
            };

            logger.addFilter(messageFilter);

            logger.info('important message');
            logger.info('regular message');

            expect(testHandler.getRecordCount()).toBe(1);
            expect(testHandler.getEmittedCount()).toBe(1); // Only the important message
        });

        it('should remove filters', () => {
            const messageFilter = {
                filter: (record: any) => record.message.includes('important')
            };

            logger.addFilter(messageFilter);
            logger.info('important message');
            logger.info('regular message');

            expect(testHandler.getEmittedCount()).toBe(1);

            logger.removeFilter(messageFilter);
            logger.info('another regular message');

            expect(testHandler.getEmittedCount()).toBe(2); // Now both messages pass
        });
    });

    describe('Logger Properties', () => {
        it('should have correct name', () => {
            expect(logger.name).toBe('test-logger');
        });

        it('should have correct level', () => {
            expect(logger.level).toBe(LogLevel.DEBUG);

            logger.setLevel(LogLevel.INFO);
            expect(logger.level).toBe(LogLevel.INFO);
        });

        it('should check if enabled for level', () => {
            logger.setLevel(LogLevel.WARNING);

            expect(logger.isEnabledFor(LogLevel.DEBUG)).toBe(false);
            expect(logger.isEnabledFor(LogLevel.INFO)).toBe(false);
            expect(logger.isEnabledFor(LogLevel.WARNING)).toBe(true);
            expect(logger.isEnabledFor(LogLevel.ERROR)).toBe(true);
            expect(logger.isEnabledFor(LogLevel.CRITICAL)).toBe(true);
        });
    });

    describe('Log Record Structure', () => {
        it('should create proper log records', () => {
            logger.info('Test message', { data: 'test' });

            const record = testHandler.getLastRecord();
            expect(record).toBeDefined();
            expect(record!.name).toBe('test-logger');
            expect(record!.level).toBe(LogLevel.INFO);
            expect(record!.levelName).toBe('INFO');
            expect(record!.message).toBe('Test message');
            expect(record!.args).toEqual([{ data: 'test' }]);
            expect(record!.timestamp).toBeInstanceOf(Date);
            expect(record!.extra).toEqual({});
        });
    });

    describe('Multiple Handlers', () => {
        it('should emit to all handlers', () => {
            const handler1 = new TestHandler();
            const handler2 = new TestHandler();

            logger.addHandler(handler1);
            logger.addHandler(handler2);

            logger.info('Test message');

            expect(testHandler.getRecordCount()).toBe(1);
            expect(handler1.getRecordCount()).toBe(1);
            expect(handler2.getRecordCount()).toBe(1);
        });
    });
});
