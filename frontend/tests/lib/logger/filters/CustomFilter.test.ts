import { describe, it, expect } from 'vitest';
import { CustomFilter } from '../../../../src/lib/logger/filters/CustomFilter';
import { LogLevel } from '../../../../src/lib/logger/types';

describe('CustomFilter', () => {
    let filter: CustomFilter;

    describe('Constructor', () => {
        it('should store the filter function', () => {
            const filterFn = (record: any) => record.level >= LogLevel.ERROR;
            filter = new CustomFilter(filterFn);
            expect(filter['filterFn']).toBe(filterFn);
        });
    });

    describe('filter', () => {
        it('should use the provided filter function', () => {
            const filterFn = (record: any) => record.message.includes('important');
            filter = new CustomFilter(filterFn);

            const matchingRecord = {
                name: 'test',
                level: LogLevel.INFO,
                message: 'This is an important message',
                timestamp: new Date(),
                levelName: 'INFO',
                args: [],
                extra: {}
            };

            const nonMatchingRecord = {
                name: 'test',
                level: LogLevel.INFO,
                message: 'This is a regular message',
                timestamp: new Date(),
                levelName: 'INFO',
                args: [],
                extra: {}
            };

            expect(filter.filter(matchingRecord)).toBe(true);
            expect(filter.filter(nonMatchingRecord)).toBe(false);
        });

        it('should handle complex filter logic', () => {
            const filterFn = (record: any) => {
                return record.level >= LogLevel.WARNING &&
                    record.message.length > 10 &&
                    record.name.startsWith('app.');
            };
            filter = new CustomFilter(filterFn);

            const matchingRecord = {
                name: 'app.service',
                level: LogLevel.WARNING,
                message: 'This is a long warning message',
                timestamp: new Date(),
                levelName: 'WARNING',
                args: [],
                extra: {}
            };

            const nonMatchingRecord1 = {
                name: 'test.service',
                level: LogLevel.WARNING,
                message: 'This is a long warning message',
                timestamp: new Date(),
                levelName: 'WARNING',
                args: [],
                extra: {}
            };

            const nonMatchingRecord2 = {
                name: 'app.service',
                level: LogLevel.INFO,
                message: 'This is a long info message',
                timestamp: new Date(),
                levelName: 'INFO',
                args: [],
                extra: {}
            };

            const nonMatchingRecord3 = {
                name: 'app.service',
                level: LogLevel.WARNING,
                message: 'Short',
                timestamp: new Date(),
                levelName: 'WARNING',
                args: [],
                extra: {}
            };

            expect(filter.filter(matchingRecord)).toBe(true);
            expect(filter.filter(nonMatchingRecord1)).toBe(false);
            expect(filter.filter(nonMatchingRecord2)).toBe(false);
            expect(filter.filter(nonMatchingRecord3)).toBe(false);
        });

        it('should handle filter functions that access extra data', () => {
            const filterFn = (record: any) => {
                return !!(record.extra && record.extra.userId && record.extra.userId > 100);
            };
            filter = new CustomFilter(filterFn);

            const matchingRecord = {
                name: 'test',
                level: LogLevel.INFO,
                message: 'User action',
                timestamp: new Date(),
                levelName: 'INFO',
                args: [],
                extra: { userId: 150, action: 'login' }
            };

            const nonMatchingRecord = {
                name: 'test',
                level: LogLevel.INFO,
                message: 'User action',
                timestamp: new Date(),
                levelName: 'INFO',
                args: [],
                extra: { userId: 50, action: 'login' }
            };

            const noExtraRecord = {
                name: 'test',
                level: LogLevel.INFO,
                message: 'User action',
                timestamp: new Date(),
                levelName: 'INFO',
                args: [],
                extra: {}
            };

            expect(filter.filter(matchingRecord)).toBe(true);
            expect(filter.filter(nonMatchingRecord)).toBe(false);
            expect(filter.filter(noExtraRecord)).toBe(false);
        });

        it('should handle filter functions that access args', () => {
            const filterFn = (record: any) => {
                return !!(record.args && record.args.length > 0 && record.args[0].error);
            };
            filter = new CustomFilter(filterFn);

            const matchingRecord = {
                name: 'test',
                level: LogLevel.INFO,
                message: 'Error occurred',
                timestamp: new Date(),
                levelName: 'INFO',
                args: [{ error: true, code: 500 }],
                extra: {}
            };

            const nonMatchingRecord = {
                name: 'test',
                level: LogLevel.INFO,
                message: 'Success',
                timestamp: new Date(),
                levelName: 'INFO',
                args: [{ success: true }],
                extra: {}
            };

            expect(filter.filter(matchingRecord)).toBe(true);
            expect(filter.filter(nonMatchingRecord)).toBe(false);
        });

        it('should handle filter functions that check timestamp', () => {
            const filterFn = (record: any) => {
                const now = new Date();
                const recordTime = new Date(record.timestamp);
                const diffMinutes = (now.getTime() - recordTime.getTime()) / (1000 * 60);
                return diffMinutes < 5; // Only logs from last 5 minutes
            };
            filter = new CustomFilter(filterFn);

            const recentRecord = {
                name: 'test',
                level: LogLevel.INFO,
                message: 'Recent message',
                timestamp: new Date(), // Now
                levelName: 'INFO',
                args: [],
                extra: {}
            };

            const oldRecord = {
                name: 'test',
                level: LogLevel.INFO,
                message: 'Old message',
                timestamp: new Date(Date.now() - 10 * 60 * 1000), // 10 minutes ago
                levelName: 'INFO',
                args: [],
                extra: {}
            };

            expect(filter.filter(recentRecord)).toBe(true);
            expect(filter.filter(oldRecord)).toBe(false);
        });

        it('should handle filter functions that return false for all records', () => {
            const filterFn = (record: any) => false;
            filter = new CustomFilter(filterFn);

            const record = {
                name: 'test',
                level: LogLevel.INFO,
                message: 'Any message',
                timestamp: new Date(),
                levelName: 'INFO',
                args: [],
                extra: {}
            };

            expect(filter.filter(record)).toBe(false);
        });

        it('should handle filter functions that return true for all records', () => {
            const filterFn = (record: any) => true;
            filter = new CustomFilter(filterFn);

            const record = {
                name: 'test',
                level: LogLevel.INFO,
                message: 'Any message',
                timestamp: new Date(),
                levelName: 'INFO',
                args: [],
                extra: {}
            };

            expect(filter.filter(record)).toBe(true);
        });

        it('should handle filter functions that throw errors gracefully', () => {
            const filterFn = (record: any) => {
                if (record.message.includes('error')) {
                    throw new Error('Filter error');
                }
                return true;
            };
            filter = new CustomFilter(filterFn);

            const normalRecord = {
                name: 'test',
                level: LogLevel.INFO,
                message: 'Normal message',
                timestamp: new Date(),
                levelName: 'INFO',
                args: [],
                extra: {}
            };

            const errorRecord = {
                name: 'test',
                level: LogLevel.INFO,
                message: 'This is an error message',
                timestamp: new Date(),
                levelName: 'INFO',
                args: [],
                extra: {}
            };

            expect(() => filter.filter(normalRecord)).not.toThrow();
            expect(() => filter.filter(errorRecord)).toThrow('Filter error');
        });
    });
});
