import { describe, it, expect } from 'vitest';
import { MessageFilter } from '../../../../src/lib/logger/filters/MessageFilter';
import { LogLevel } from '../../../../src/lib/logger/types';

describe('MessageFilter', () => {
    let filter: MessageFilter;

    describe('Constructor', () => {
        it('should create regex from string pattern', () => {
            filter = new MessageFilter('error');
            expect(filter['pattern']).toBeInstanceOf(RegExp);
            expect(filter['pattern'].source).toBe('error');
        });

        it('should use regex directly when provided', () => {
            const regex = /^ERROR:/;
            filter = new MessageFilter(regex);
            expect(filter['pattern']).toBe(regex);
        });
    });

    describe('filter', () => {
        it('should match messages with string pattern', () => {
            filter = new MessageFilter('error');

            const matchingRecord = {
                name: 'test',
                level: LogLevel.INFO,
                message: 'This is an error message',
                timestamp: new Date(),
                levelName: 'INFO',
                args: [],
                extra: {}
            };

            const nonMatchingRecord = {
                name: 'test',
                level: LogLevel.INFO,
                message: 'This is a success message',
                timestamp: new Date(),
                levelName: 'INFO',
                args: [],
                extra: {}
            };

            expect(filter.filter(matchingRecord)).toBe(true);
            expect(filter.filter(nonMatchingRecord)).toBe(false);
        });

        it('should match messages with regex pattern', () => {
            filter = new MessageFilter(/^ERROR:/);

            const matchingRecord = {
                name: 'test',
                level: LogLevel.INFO,
                message: 'ERROR: Something went wrong',
                timestamp: new Date(),
                levelName: 'INFO',
                args: [],
                extra: {}
            };

            const nonMatchingRecord = {
                name: 'test',
                level: LogLevel.INFO,
                message: 'WARNING: Something might be wrong',
                timestamp: new Date(),
                levelName: 'INFO',
                args: [],
                extra: {}
            };

            expect(filter.filter(matchingRecord)).toBe(true);
            expect(filter.filter(nonMatchingRecord)).toBe(false);
        });

        it('should handle case sensitivity', () => {
            filter = new MessageFilter('Error');

            const matchingRecord = {
                name: 'test',
                level: LogLevel.INFO,
                message: 'This is an Error message',
                timestamp: new Date(),
                levelName: 'INFO',
                args: [],
                extra: {}
            };

            const nonMatchingRecord = {
                name: 'test',
                level: LogLevel.INFO,
                message: 'This is an error message',
                timestamp: new Date(),
                levelName: 'INFO',
                args: [],
                extra: {}
            };

            expect(filter.filter(matchingRecord)).toBe(true);
            expect(filter.filter(nonMatchingRecord)).toBe(false);
        });

        it('should handle case insensitive patterns', () => {
            filter = new MessageFilter(/error/i);

            const matchingRecord1 = {
                name: 'test',
                level: LogLevel.INFO,
                message: 'This is an error message',
                timestamp: new Date(),
                levelName: 'INFO',
                args: [],
                extra: {}
            };

            const matchingRecord2 = {
                name: 'test',
                level: LogLevel.INFO,
                message: 'This is an ERROR message',
                timestamp: new Date(),
                levelName: 'INFO',
                args: [],
                extra: {}
            };

            expect(filter.filter(matchingRecord1)).toBe(true);
            expect(filter.filter(matchingRecord2)).toBe(true);
        });

        it('should handle word boundaries', () => {
            filter = new MessageFilter('\\berror\\b');

            const matchingRecord = {
                name: 'test',
                level: LogLevel.INFO,
                message: 'This is an error message',
                timestamp: new Date(),
                levelName: 'INFO',
                args: [],
                extra: {}
            };

            const nonMatchingRecord = {
                name: 'test',
                level: LogLevel.INFO,
                message: 'This is an erroring message',
                timestamp: new Date(),
                levelName: 'INFO',
                args: [],
                extra: {}
            };

            expect(filter.filter(matchingRecord)).toBe(true);
            expect(filter.filter(nonMatchingRecord)).toBe(false);
        });

        it('should handle complex patterns', () => {
            filter = new MessageFilter('^(ERROR|WARNING):\\s+.*');

            const matchingRecord1 = {
                name: 'test',
                level: LogLevel.INFO,
                message: 'ERROR: Database connection failed',
                timestamp: new Date(),
                levelName: 'INFO',
                args: [],
                extra: {}
            };

            const matchingRecord2 = {
                name: 'test',
                level: LogLevel.INFO,
                message: 'WARNING: High memory usage detected',
                timestamp: new Date(),
                levelName: 'INFO',
                args: [],
                extra: {}
            };

            const nonMatchingRecord = {
                name: 'test',
                level: LogLevel.INFO,
                message: 'INFO: Application started',
                timestamp: new Date(),
                levelName: 'INFO',
                args: [],
                extra: {}
            };

            expect(filter.filter(matchingRecord1)).toBe(true);
            expect(filter.filter(matchingRecord2)).toBe(true);
            expect(filter.filter(nonMatchingRecord)).toBe(false);
        });

        it('should handle special characters in messages', () => {
            filter = new MessageFilter('\\$\\{.*\\}');

            const matchingRecord = {
                name: 'test',
                level: LogLevel.INFO,
                message: 'Variable ${USER_ID} is not defined',
                timestamp: new Date(),
                levelName: 'INFO',
                args: [],
                extra: {}
            };

            const nonMatchingRecord = {
                name: 'test',
                level: LogLevel.INFO,
                message: 'Variable $USER_ID is not defined',
                timestamp: new Date(),
                levelName: 'INFO',
                args: [],
                extra: {}
            };

            expect(filter.filter(matchingRecord)).toBe(true);
            expect(filter.filter(nonMatchingRecord)).toBe(false);
        });

        it('should handle empty messages', () => {
            filter = new MessageFilter('error');

            const emptyMessageRecord = {
                name: 'test',
                level: LogLevel.INFO,
                message: '',
                timestamp: new Date(),
                levelName: 'INFO',
                args: [],
                extra: {}
            };

            expect(filter.filter(emptyMessageRecord)).toBe(false);
        });

        it('should handle multiline messages', () => {
            filter = new MessageFilter('stack trace');

            const multilineRecord = {
                name: 'test',
                level: LogLevel.INFO,
                message: 'Error occurred:\nstack trace:\n  at line 1\n  at line 2',
                timestamp: new Date(),
                levelName: 'INFO',
                args: [],
                extra: {}
            };

            expect(filter.filter(multilineRecord)).toBe(true);
        });
    });
});
