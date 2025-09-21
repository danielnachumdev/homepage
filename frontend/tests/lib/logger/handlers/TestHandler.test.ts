import { describe, it, expect, beforeEach, afterEach } from 'vitest';
import { TestHandler } from '../../../../src/lib/logger/handlers/TestHandler';
import { LogLevel } from '../../../../src/lib/logger/types';

describe('TestHandler', () => {
    let handler: TestHandler;

    beforeEach(() => {
        handler = new TestHandler();
    });

    afterEach(() => {
        // Clear handler to ensure clean state between tests
        if (handler) {
            handler.clear();
        }
    });

    describe('Constructor', () => {
        it('should initialize with empty records', () => {
            expect(handler.getRecordCount()).toBe(0);
            expect(handler.getEmittedCount()).toBe(0);
        });

        it('should set custom level', () => {
            const customHandler = new TestHandler(LogLevel.INFO);
            expect(customHandler.level).toBe(LogLevel.INFO);
        });
    });

    describe('emit', () => {
        it('should capture all records', () => {
            const record = {
                level: LogLevel.INFO,
                message: 'Test message',
                args: [],
                timestamp: new Date(),
                name: 'test',
                levelName: 'INFO',
                module: undefined,
                function: undefined,
                line: undefined,
                extra: {}
            };

            handler.emit(record);

            expect(handler.getRecordCount()).toBe(1);
            expect(handler.getCapturedRecords()).toHaveLength(1);
            expect(handler.getCapturedRecords()[0]).toEqual(record);
        });

        it('should emit records that pass level filter', () => {
            handler.level = LogLevel.INFO;

            const infoRecord = {
                level: LogLevel.INFO,
                message: 'Info message',
                args: [],
                timestamp: new Date(),
                name: 'test',
                levelName: 'INFO',
                module: undefined,
                function: undefined,
                line: undefined,
                extra: {}
            };

            const debugRecord = {
                level: LogLevel.DEBUG,
                message: 'Debug message',
                args: [],
                timestamp: new Date(),
                name: 'test',
                levelName: 'DEBUG',
                module: undefined,
                function: undefined,
                line: undefined,
                extra: {}
            };

            handler.handle(infoRecord);
            handler.handle(debugRecord);

            expect(handler.getRecordCount()).toBe(2);
            expect(handler.getEmittedCount()).toBe(1);
            expect(handler.getEmittedRecords()).toHaveLength(1);
            expect(handler.getEmittedRecords()[0]).toEqual(infoRecord);
        });
    });

    describe('getRecordsByLevel', () => {
        it('should filter records by level', () => {
            const infoRecord = {
                level: LogLevel.INFO,
                message: 'Info message',
                args: [],
                timestamp: new Date(),
                name: 'test',
                levelName: 'INFO',
                module: undefined,
                function: undefined,
                line: undefined,
                extra: {}
            };

            const errorRecord = {
                level: LogLevel.ERROR,
                message: 'Error message',
                args: [],
                timestamp: new Date(),
                name: 'test',
                levelName: 'ERROR',
                module: undefined,
                function: undefined,
                line: undefined,
                extra: {}
            };

            handler.emit(infoRecord);
            handler.emit(errorRecord);

            const infoRecords = handler.getRecordsByLevel(LogLevel.INFO);
            const errorRecords = handler.getRecordsByLevel(LogLevel.ERROR);

            expect(infoRecords).toHaveLength(1);
            expect(errorRecords).toHaveLength(1);
            expect(infoRecords[0]).toEqual(infoRecord);
            expect(errorRecords[0]).toEqual(errorRecord);
        });
    });

    describe('getRecordsByName', () => {
        it('should filter records by logger name', () => {
            const record1 = {
                level: LogLevel.INFO,
                message: 'Message 1',
                args: [],
                timestamp: new Date(),
                name: 'logger1',
                levelName: 'INFO',
                module: undefined,
                function: undefined,
                line: undefined,
                extra: {}
            };

            const record2 = {
                level: LogLevel.INFO,
                message: 'Message 2',
                args: [],
                timestamp: new Date(),
                name: 'logger2',
                levelName: 'INFO',
                module: undefined,
                function: undefined,
                line: undefined,
                extra: {}
            };

            handler.emit(record1);
            handler.emit(record2);

            const logger1Records = handler.getRecordsByName('logger1');
            const logger2Records = handler.getRecordsByName('logger2');

            expect(logger1Records).toHaveLength(1);
            expect(logger2Records).toHaveLength(1);
            expect(logger1Records[0]).toEqual(record1);
            expect(logger2Records[0]).toEqual(record2);
        });
    });

    describe('getRecordsByMessage', () => {
        it('should filter records by message content', () => {
            const record1 = {
                level: LogLevel.INFO,
                message: 'Important message',
                args: [],
                timestamp: new Date(),
                name: 'test',
                levelName: 'INFO',
                module: undefined,
                function: undefined,
                line: undefined,
                extra: {}
            };

            const record2 = {
                level: LogLevel.INFO,
                message: 'Regular message',
                args: [],
                timestamp: new Date(),
                name: 'test',
                levelName: 'INFO',
                module: undefined,
                function: undefined,
                line: undefined,
                extra: {}
            };

            handler.emit(record1);
            handler.emit(record2);

            const importantRecords = handler.getRecordsByMessage('Important');
            const regularRecords = handler.getRecordsByMessage('Regular');

            expect(importantRecords).toHaveLength(1);
            expect(regularRecords).toHaveLength(1);
            expect(importantRecords[0]).toEqual(record1);
            expect(regularRecords[0]).toEqual(record2);
        });
    });

    describe('hasMessage', () => {
        it('should check if message exists', () => {
            const record = {
                level: LogLevel.INFO,
                message: 'Test message',
                args: [],
                timestamp: new Date(),
                name: 'test',
                levelName: 'INFO',
                module: undefined,
                function: undefined,
                line: undefined,
                extra: {}
            };

            handler.emit(record);

            expect(handler.hasMessage('Test message')).toBe(true);
            expect(handler.hasMessage('Other message')).toBe(false);
        });
    });

    describe('hasLevel', () => {
        it('should check if level exists', () => {
            const record = {
                level: LogLevel.INFO,
                message: 'Test message',
                args: [],
                timestamp: new Date(),
                name: 'test',
                levelName: 'INFO',
                module: undefined,
                function: undefined,
                line: undefined,
                extra: {}
            };

            handler.emit(record);

            expect(handler.hasLevel(LogLevel.INFO)).toBe(true);
            expect(handler.hasLevel(LogLevel.ERROR)).toBe(false);
        });
    });

    describe('getLastRecord', () => {
        it('should return the last captured record', () => {
            const record1 = {
                level: LogLevel.INFO,
                message: 'First message',
                args: [],
                timestamp: new Date(),
                name: 'test',
                levelName: 'INFO',
                module: undefined,
                function: undefined,
                line: undefined,
                extra: {}
            };

            const record2 = {
                level: LogLevel.ERROR,
                message: 'Second message',
                args: [],
                timestamp: new Date(),
                name: 'test',
                levelName: 'ERROR',
                module: undefined,
                function: undefined,
                line: undefined,
                extra: {}
            };

            handler.emit(record1);
            handler.emit(record2);

            expect(handler.getLastRecord()).toEqual(record2);
        });

        it('should return undefined when no records', () => {
            expect(handler.getLastRecord()).toBeUndefined();
        });
    });

    describe('getLastEmittedRecord', () => {
        it('should return the last emitted record', () => {
            handler.level = LogLevel.INFO;

            const record1 = {
                level: LogLevel.DEBUG,
                message: 'Debug message',
                args: [],
                timestamp: new Date(),
                name: 'test',
                levelName: 'DEBUG',
                module: undefined,
                function: undefined,
                line: undefined,
                extra: {}
            };

            const record2 = {
                level: LogLevel.INFO,
                message: 'Info message',
                args: [],
                timestamp: new Date(),
                name: 'test',
                levelName: 'INFO',
                module: undefined,
                function: undefined,
                line: undefined,
                extra: {}
            };

            handler.emit(record1);
            handler.emit(record2);

            expect(handler.getLastEmittedRecord()).toEqual(record2);
        });
    });

    describe('clear', () => {
        it('should clear all records', () => {
            const record = {
                level: LogLevel.INFO,
                message: 'Test message',
                args: [],
                timestamp: new Date(),
                name: 'test',
                levelName: 'INFO',
                module: undefined,
                function: undefined,
                line: undefined,
                extra: {}
            };

            handler.emit(record);
            expect(handler.getRecordCount()).toBe(1);

            handler.clear();
            expect(handler.getRecordCount()).toBe(0);
            expect(handler.getEmittedCount()).toBe(0);
        });
    });
});
