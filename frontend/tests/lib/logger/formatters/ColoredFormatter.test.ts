import { describe, it, expect } from 'vitest';
import { ColoredFormatter } from '../../../../src/lib/logger/formatters/ColoredFormatter';
import { LogLevel } from '../../../../src/lib/logger/types';

describe('ColoredFormatter', () => {
    let formatter: ColoredFormatter;

    beforeEach(() => {
        formatter = new ColoredFormatter();
    });

    describe('Constructor', () => {
        it('should create with default format', () => {
            expect(formatter['baseFormatter']).toBeDefined();
            expect(formatter['baseFormatter']['formatString']).toBe('%(asctime)s - %(name)s - %(levelname)s - %(message)s');
        });

        it('should create with custom format', () => {
            const customFormatter = new ColoredFormatter('%(levelname)s: %(message)s');
            expect(customFormatter['baseFormatter']['formatString']).toBe('%(levelname)s: %(message)s');
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

        it('should add colors to different log levels', () => {
            const levels = [
                { level: LogLevel.DEBUG, levelName: 'DEBUG', expectedColor: '\x1b[36m' }, // Cyan
                { level: LogLevel.INFO, levelName: 'INFO', expectedColor: '\x1b[32m' }, // Green
                { level: LogLevel.WARNING, levelName: 'WARNING', expectedColor: '\x1b[33m' }, // Yellow
                { level: LogLevel.ERROR, levelName: 'ERROR', expectedColor: '\x1b[31m' }, // Red
                { level: LogLevel.CRITICAL, levelName: 'CRITICAL', expectedColor: '\x1b[35m' }, // Magenta
            ];

            levels.forEach(({ level, levelName, expectedColor }) => {
                const record = createTestRecord({ level, levelName });
                const result = formatter.format(record);

                expect(result).toContain(expectedColor);
                expect(result).toContain('\x1b[0m'); // Reset code
                expect(result).toContain('Test message');
            });
        });

        it('should use base formatter for content', () => {
            const record = createTestRecord();
            const result = formatter.format(record);

            // Should contain the base formatted content
            expect(result).toContain('2023-01-01T12:00:00.000Z');
            expect(result).toContain('test-logger');
            expect(result).toContain('INFO');
            expect(result).toContain('Test message');
        });

        it('should handle custom format string', () => {
            const customFormatter = new ColoredFormatter('%(levelname)s: %(message)s');
            const record = createTestRecord();
            const result = customFormatter.format(record);

            expect(result).toContain('\x1b[32m'); // Green for INFO
            expect(result).toContain('INFO: Test message');
            expect(result).toContain('\x1b[0m'); // Reset
        });

        it('should handle unknown log levels', () => {
            const record = createTestRecord({ level: 999, levelName: 'UNKNOWN' });
            const result = formatter.format(record);

            expect(result).toContain('\x1b[0m'); // Reset color for unknown
            expect(result).toContain('Test message');
        });

        it('should preserve special characters in message', () => {
            const record = createTestRecord({
                message: 'Message with special chars: !@#$%^&*()_+-=[]{}|;:,.<>?'
            });
            const result = formatter.format(record);

            expect(result).toContain('\x1b[32m'); // Green for INFO
            expect(result).toContain('Message with special chars: !@#$%^&*()_+-=[]{}|;:,.<>?');
            expect(result).toContain('\x1b[0m'); // Reset
        });

        it('should handle empty message', () => {
            const record = createTestRecord({ message: '' });
            const result = formatter.format(record);

            expect(result).toContain('\x1b[32m'); // Green for INFO
            expect(result).toContain('\x1b[0m'); // Reset
        });

        it('should handle long messages', () => {
            const longMessage = 'A'.repeat(1000);
            const record = createTestRecord({ message: longMessage });
            const result = formatter.format(record);

            expect(result).toContain('\x1b[32m'); // Green for INFO
            expect(result).toContain(longMessage);
            expect(result).toContain('\x1b[0m'); // Reset
        });

        it('should handle different timestamp formats', () => {
            const record = createTestRecord({
                timestamp: new Date('2023-12-25T15:30:45.123Z')
            });
            const result = formatter.format(record);

            expect(result).toContain('\x1b[32m'); // Green for INFO
            expect(result).toContain('2023-12-25T15:30:45.123Z');
            expect(result).toContain('\x1b[0m'); // Reset
        });

        it('should maintain color consistency for same level', () => {
            const record1 = createTestRecord({ message: 'Message 1' });
            const record2 = createTestRecord({ message: 'Message 2' });

            const result1 = formatter.format(record1);
            const result2 = formatter.format(record2);

            // Both should have the same color (green for INFO)
            expect(result1).toContain('\x1b[32m');
            expect(result2).toContain('\x1b[32m');
        });

        it('should handle complex logger names', () => {
            const record = createTestRecord({
                name: 'very.long.logger.name.that.might.cause.issues'
            });
            const result = formatter.format(record);

            expect(result).toContain('\x1b[32m'); // Green for INFO
            expect(result).toContain('very.long.logger.name.that.might.cause.issues');
            expect(result).toContain('\x1b[0m'); // Reset
        });
    });

    describe('getColorForLevel', () => {
        it('should return correct colors for all levels', () => {
            const expectedColors = {
                [LogLevel.DEBUG]: '\x1b[36m', // Cyan
                [LogLevel.INFO]: '\x1b[32m', // Green
                [LogLevel.WARNING]: '\x1b[33m', // Yellow
                [LogLevel.ERROR]: '\x1b[31m', // Red
                [LogLevel.CRITICAL]: '\x1b[35m', // Magenta
            };

            Object.entries(expectedColors).forEach(([level, expectedColor]) => {
                const color = formatter['getColorForLevel'](parseInt(level));
                expect(color).toBe(expectedColor);
            });
        });

        it('should return reset color for unknown level', () => {
            const color = formatter['getColorForLevel'](999);
            expect(color).toBe('\x1b[0m');
        });
    });
});
