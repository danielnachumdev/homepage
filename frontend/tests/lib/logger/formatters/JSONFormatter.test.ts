import { describe, it, expect } from 'vitest';
import { JSONFormatter } from '../../../../src/lib/logger/formatters/JSONFormatter';
import { LogLevel } from '../../../../src/lib/logger/types';

describe('JSONFormatter', () => {
    let formatter: JSONFormatter;

    beforeEach(() => {
        formatter = new JSONFormatter();
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

        it('should format as valid JSON', () => {
            const record = createTestRecord();
            const result = formatter.format(record);

            expect(() => JSON.parse(result)).not.toThrow();
        });

        it('should include all record properties', () => {
            const record = createTestRecord();
            const result = formatter.format(record);
            const parsed = JSON.parse(result);

            expect(parsed.timestamp).toBe('2023-01-01T12:00:00.000Z');
            expect(parsed.name).toBe('test-logger');
            expect(parsed.level).toBe('INFO');
            expect(parsed.message).toBe('Test message');
            expect(parsed.module).toBe('test.ts');
            expect(parsed.function).toBe('testFunction');
            expect(parsed.line).toBe(42);
            expect(parsed.args).toEqual([{ data: 'test' }]);
            expect(parsed.extra).toEqual({ userId: 123 });
        });

        it('should handle missing optional fields', () => {
            const record = createTestRecord({
                module: undefined,
                function: undefined,
                line: undefined
            });
            const result = formatter.format(record);
            const parsed = JSON.parse(result);

            expect(parsed.timestamp).toBe('2023-01-01T12:00:00.000Z');
            expect(parsed.name).toBe('test-logger');
            expect(parsed.level).toBe('INFO');
            expect(parsed.message).toBe('Test message');
            expect(parsed.module).toBeUndefined();
            expect(parsed.function).toBeUndefined();
            expect(parsed.line).toBeUndefined();
            expect(parsed.args).toEqual([{ data: 'test' }]);
            expect(parsed.extra).toEqual({ userId: 123 });
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
                const parsed = JSON.parse(result);

                expect(parsed.level).toBe(levelName);
            });
        });

        it('should handle complex args and extra data', () => {
            const record = createTestRecord({
                args: [
                    { userId: 123, action: 'login' },
                    'string arg',
                    42,
                    { nested: { data: 'value' } }
                ],
                extra: {
                    sessionId: 'sess_123',
                    metadata: {
                        ip: '192.168.1.1',
                        userAgent: 'Mozilla/5.0...'
                    }
                }
            });
            const result = formatter.format(record);
            const parsed = JSON.parse(result);

            expect(parsed.args).toEqual([
                { userId: 123, action: 'login' },
                'string arg',
                42,
                { nested: { data: 'value' } }
            ]);
            expect(parsed.extra).toEqual({
                sessionId: 'sess_123',
                metadata: {
                    ip: '192.168.1.1',
                    userAgent: 'Mozilla/5.0...'
                }
            });
        });

        it('should handle special characters in message', () => {
            const record = createTestRecord({
                message: 'Message with "quotes" and \n newlines and \t tabs'
            });
            const result = formatter.format(record);
            const parsed = JSON.parse(result);

            expect(parsed.message).toBe('Message with "quotes" and \n newlines and \t tabs');
        });

        it('should handle empty args and extra', () => {
            const record = createTestRecord({
                args: [],
                extra: {}
            });
            const result = formatter.format(record);
            const parsed = JSON.parse(result);

            expect(parsed.args).toEqual([]);
            expect(parsed.extra).toEqual({});
        });

        it('should handle null and undefined values in extra', () => {
            const record = createTestRecord({
                extra: {
                    nullValue: null,
                    undefinedValue: undefined,
                    emptyString: '',
                    zero: 0,
                    falseValue: false
                }
            });
            const result = formatter.format(record);
            const parsed = JSON.parse(result);

            expect(parsed.extra).toEqual({
                nullValue: null,
                emptyString: '',
                zero: 0,
                falseValue: false
                // undefinedValue should be omitted in JSON
            });
        });

        it('should maintain consistent structure across different records', () => {
            const record1 = createTestRecord({ message: 'Message 1' });
            const record2 = createTestRecord({ message: 'Message 2', level: LogLevel.ERROR });

            const result1 = formatter.format(record1);
            const result2 = formatter.format(record2);

            const parsed1 = JSON.parse(result1);
            const parsed2 = JSON.parse(result2);

            // Both should have the same structure
            expect(Object.keys(parsed1)).toEqual(Object.keys(parsed2));
            expect(parsed1.timestamp).toBeDefined();
            expect(parsed2.timestamp).toBeDefined();
            expect(parsed1.name).toBeDefined();
            expect(parsed2.name).toBeDefined();
        });
    });
});
