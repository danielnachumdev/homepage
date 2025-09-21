import { describe, it, expect } from 'vitest';
import { BaseFilter } from '../../../../src/lib/logger/filters/BaseFilter';
import { LogLevel } from '../../../../src/lib/logger/types';

// Concrete implementation for testing
class TestFilter extends BaseFilter {
    filter(record: any): boolean {
        return record.message.includes('test');
    }
}

describe('BaseFilter', () => {
    let filter: TestFilter;

    beforeEach(() => {
        filter = new TestFilter();
    });

    describe('filter', () => {
        it('should be implemented by concrete classes', () => {
            const record = {
                message: 'This is a test message',
                level: LogLevel.INFO,
                timestamp: new Date(),
                name: 'test',
                levelName: 'INFO',
                args: [],
                extra: {}
            };

            const result = filter.filter(record);
            expect(result).toBe(true);
        });

        it('should return false for non-matching records', () => {
            const record = {
                message: 'This is not a sample',
                level: LogLevel.INFO,
                timestamp: new Date(),
                name: 'test',
                levelName: 'INFO',
                args: [],
                extra: {}
            };

            const result = filter.filter(record);
            expect(result).toBe(false);
        });
    });
});
