import { describe, it, expect, beforeEach, afterEach } from 'vitest';
import { StandardFormatter } from '../../../../src/lib/logger/formatters/StandardFormatter';
import { LogLevel } from '../../../../src/lib/logger/types';

describe('StandardFormatter', () => {
    let formatter: StandardFormatter;

    const createTestRecord = (overrides: any = {}) => ({
        name: 'test-logger',
        level: LogLevel.INFO,
        levelName: 'INFO',
        message: 'Test message',
        timestamp: new Date('2023-01-01T12:00:00.000Z'),
        module: 'test.ts',
        function: 'testFunction',
        line: 42,
        args: [{ data: 'test' }],
        extra: { userId: 123 },
        ...overrides
    });

    beforeEach(() => {
        formatter = new StandardFormatter();
    });

    afterEach(() => {
        // Clean up any global state if needed
    });

    describe('Constructor', () => {
        it('should use default format string', () => {
            expect(formatter['formatString']).toBe('%(asctime)s - %(name)s - %(levelname)s - %(message)s');
        });

        it('should use custom format string', () => {
            const customFormatter = new StandardFormatter('%(levelname)s: %(message)s');
            expect(customFormatter['formatString']).toBe('%(levelname)s: %(message)s');
        });
    });

    describe('format', () => {
        const createTestRecord = (overrides: any = {}) => ({
            name: 'test-logger',
            level: LogLevel.INFO,
            levelName: 'INFO',
            message: 'Test message',
            timestamp: new Date('2023-01-01T12:00:00.000Z'),
            module: 'test.ts',
            function: 'testFunction',
            line: 42,
            args: [{ data: 'test' }],
            extra: { userId: 123 },
            ...overrides
        });

        it('should format with default format string', () => {
            const record = createTestRecord();
            const result = formatter.format(record);

            expect(result).toContain('2023-01-01T12:00:00.000Z');
            expect(result).toContain('test-logger');
            expect(result).toContain('INFO');
            expect(result).toContain('Test message');
        });

        it('should format with custom format string', () => {
            const customFormatter = new StandardFormatter('%(levelname)s: %(message)s');
            const record = createTestRecord();
            const result = customFormatter.format(record);

            expect(result).toBe('INFO: Test message');
        });

        it('should handle all format specifiers', () => {
            const customFormatter = new StandardFormatter(
                '%(asctime)s|%(name)s|%(levelname)s|%(message)s|%(module)s|%(funcName)s|%(lineno)d|%(pathname)s|%(process)d|%(thread)d'
            );
            const record = createTestRecord();
            const result = customFormatter.format(record);

            expect(result).toBe('2023-01-01T12:00:00.000Z|test-logger|INFO|Test message|test.ts|testFunction|42|test.ts|0|0');
        });

        it('should handle missing optional fields', () => {
            const record = createTestRecord({
                module: undefined,
                function: undefined,
                line: undefined
            });
            const result = formatter.format(record);

            expect(result).toContain('2023-01-01T12:00:00.000Z');
            expect(result).toContain('test-logger');
            expect(result).toContain('INFO');
            expect(result).toContain('Test message');
        });

        it('should handle different log levels', () => {
            const levels = [
                { level: LogLevel.DEBUG, levelName: 'DEBUG' },
                { level: LogLevel.INFO, levelName: 'INFO' },
                { level: LogLevel.WARNING, levelName: 'WARNING' },
                { level: LogLevel.ERROR, levelName: 'ERROR' },
                { level: LogLevel.CRITICAL, levelName: 'CRITICAL' },
            ];

            levels.forEach(({ level, levelName }) => {
                const record = createTestRecord({ level, levelName });
                const result = formatter.format(record);
                expect(result).toContain(levelName);
            });
        });

        it('should handle special characters in message', () => {
            const record = createTestRecord({
                message: 'Message with special chars: !@#$%^&*()_+-=[]{}|;:,.<>?'
            });
            const result = formatter.format(record);

            expect(result).toContain('Message with special chars: !@#$%^&*()_+-=[]{}|;:,.<>?');
        });

        it('should handle empty message', () => {
            const record = createTestRecord({ message: '' });
            const result = formatter.format(record);

            expect(result).toContain('2023-01-01T12:00:00.000Z');
            expect(result).toContain('test-logger');
            expect(result).toContain('INFO');
        });

        it('should handle long logger names', () => {
            const record = createTestRecord({
                name: 'very.long.logger.name.that.might.cause.issues'
            });
            const result = formatter.format(record);

            expect(result).toContain('very.long.logger.name.that.might.cause.issues');
        });
    });

    describe('formatTime', () => {
        it('should format timestamp as ISO string', () => {
            const record = createTestRecord({
                timestamp: new Date('2023-12-25T15:30:45.123Z')
            });
            const result = formatter.format(record);

            expect(result).toContain('2023-12-25T15:30:45.123Z');
        });

        it('should handle different timezones', () => {
            const record = createTestRecord({
                timestamp: new Date('2023-01-01T00:00:00.000Z')
            });
            const result = formatter.format(record);

            expect(result).toContain('2023-01-01T00:00:00.000Z');
        });
    });
});
