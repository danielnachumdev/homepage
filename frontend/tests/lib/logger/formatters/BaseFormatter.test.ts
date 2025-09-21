import { describe, it, expect } from 'vitest';
import { BaseFormatter } from '../../../../src/lib/logger/formatters/BaseFormatter';
import { LogLevel } from '../../../../src/lib/logger/types';

// Concrete implementation for testing
class TestFormatter extends BaseFormatter {
    format(record: any): string {
        return `TEST: ${record.message}`;
    }
}

describe('BaseFormatter', () => {
    let formatter: TestFormatter;

    beforeEach(() => {
        formatter = new TestFormatter();
    });

    describe('format', () => {
        it('should be implemented by concrete classes', () => {
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
            expect(result).toBe('TEST: Test message');
        });
    });
});
