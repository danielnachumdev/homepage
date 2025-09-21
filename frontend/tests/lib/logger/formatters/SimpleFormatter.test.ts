import { describe, it, expect } from 'vitest';
import { SimpleFormatter } from '../../../../src/lib/logger/formatters/SimpleFormatter';
import { LogLevel } from '../../../../src/lib/logger/types';

describe('SimpleFormatter', () => {
    let formatter: SimpleFormatter;

    beforeEach(() => {
        formatter = new SimpleFormatter();
    });

    describe('format', () => {
        it('should return just the message', () => {
            const record = {
                message: 'Test message',
                level: LogLevel.INFO,
                timestamp: new Date(),
                name: 'test',
                levelName: 'INFO',
                args: [],
                extra: {}
            };

            const result = formatter.format(record);
            expect(result).toBe('Test message');
        });

        it('should handle empty message', () => {
            const record = {
                message: '',
                level: LogLevel.INFO,
                timestamp: new Date(),
                name: 'test',
                levelName: 'INFO',
                args: [],
                extra: {}
            };

            const result = formatter.format(record);
            expect(result).toBe('');
        });

        it('should ignore other record properties', () => {
            const record = {
                message: 'Test message',
                level: LogLevel.ERROR,
                timestamp: new Date('2023-01-01T12:00:00.000Z'),
                name: 'important-logger',
                levelName: 'ERROR',
                args: [{ data: 'test' }],
                extra: { userId: 123 }
            };

            const result = formatter.format(record);
            expect(result).toBe('Test message');
        });
    });
});
