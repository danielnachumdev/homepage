import { describe, it, expect, beforeEach, afterEach } from 'vitest';
import { BaseHandler } from '../../../../src/lib/logger/handlers/BaseHandler';
import { LogLevel } from '../../../../src/lib/logger/types';

// Concrete implementation for testing
class TestBaseHandler extends BaseHandler {
    public emittedRecords: any[] = [];

    emit(record: any): void {
        this.emittedRecords.push(record);
    }
}

describe('BaseHandler', () => {
    let handler: TestBaseHandler;

    beforeEach(() => {
        handler = new TestBaseHandler();
    });

    afterEach(() => {
        // Clear emitted records to ensure clean state between tests
        if (handler) {
            handler.emittedRecords = [];
        }
    });

    describe('Constructor', () => {
        it('should set default level to NOTSET', () => {
            expect(handler.level).toBe(LogLevel.NOTSET);
        });

        it('should set custom level', () => {
            const customHandler = new TestBaseHandler(LogLevel.INFO);
            expect(customHandler.level).toBe(LogLevel.INFO);
        });

        it('should accept formatter', () => {
            const formatter = { format: (record: any) => record.message };
            const customHandler = new TestBaseHandler(LogLevel.DEBUG, formatter);
            expect(customHandler.formatter).toBe(formatter);
        });
    });

    describe('shouldEmit', () => {
        it('should emit when record level >= handler level', () => {
            handler.level = LogLevel.INFO;

            const infoRecord = {
                level: LogLevel.INFO,
                name: 'test',
                levelName: 'INFO',
                message: 'test',
                timestamp: new Date(),
                args: [],
                extra: {}
            };
            const errorRecord = {
                level: LogLevel.ERROR,
                name: 'test',
                levelName: 'ERROR',
                message: 'test',
                timestamp: new Date(),
                args: [],
                extra: {}
            };
            const debugRecord = {
                level: LogLevel.DEBUG,
                name: 'test',
                levelName: 'DEBUG',
                message: 'test',
                timestamp: new Date(),
                args: [],
                extra: {}
            };

            expect(handler.shouldEmit(infoRecord)).toBe(true);
            expect(handler.shouldEmit(errorRecord)).toBe(true);
            expect(handler.shouldEmit(debugRecord)).toBe(false);
        });

        it('should emit all records when level is NOTSET', () => {
            handler.level = LogLevel.NOTSET;

            const debugRecord = {
                level: LogLevel.DEBUG,
                name: 'test',
                levelName: 'DEBUG',
                message: 'test',
                timestamp: new Date(),
                args: [],
                extra: {}
            };
            const criticalRecord = {
                level: LogLevel.CRITICAL,
                name: 'test',
                levelName: 'CRITICAL',
                message: 'test',
                timestamp: new Date(),
                args: [],
                extra: {}
            };

            expect(handler.shouldEmit(debugRecord)).toBe(true);
            expect(handler.shouldEmit(criticalRecord)).toBe(true);
        });
    });

    describe('format', () => {
        it('should return message when no formatter is set', () => {
            const record = {
                level: LogLevel.INFO,
                name: 'test',
                levelName: 'INFO',
                message: 'Test message',
                timestamp: new Date(),
                args: [],
                extra: {}
            };
            expect(handler.format(record)).toBe('Test message');
        });

        it('should use formatter when set', () => {
            const formatter = { format: (record: any) => `FORMATTED: ${record.message}` };
            handler.formatter = formatter;

            const record = {
                level: LogLevel.INFO,
                name: 'test',
                levelName: 'INFO',
                message: 'Test message',
                timestamp: new Date(),
                args: [],
                extra: {}
            };
            expect(handler.format(record)).toBe('FORMATTED: Test message');
        });
    });
});
