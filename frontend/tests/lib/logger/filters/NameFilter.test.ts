import { describe, it, expect } from 'vitest';
import { NameFilter } from '../../../../src/lib/logger/filters/NameFilter';
import { LogLevel } from '../../../../src/lib/logger/types';

describe('NameFilter', () => {
    let filter: NameFilter;

    describe('Constructor', () => {
        it('should create regex from string pattern', () => {
            filter = new NameFilter('^test\\..*');
            expect(filter['pattern']).toBeInstanceOf(RegExp);
            expect(filter['pattern'].source).toBe('^test\\..*');
        });

        it('should use regex directly when provided', () => {
            const regex = /^app\./;
            filter = new NameFilter(regex);
            expect(filter['pattern']).toBe(regex);
        });
    });

    describe('filter', () => {
        it('should match logger names with string pattern', () => {
            filter = new NameFilter('^test\\..*');

            const matchingRecord = {
                name: 'test.logger',
                level: LogLevel.INFO,
                message: 'Test message',
                timestamp: new Date(),
                levelName: 'INFO',
                args: [],
                extra: {}
            };

            const nonMatchingRecord = {
                name: 'other.logger',
                level: LogLevel.INFO,
                message: 'Test message',
                timestamp: new Date(),
                levelName: 'INFO',
                args: [],
                extra: {}
            };

            expect(filter.filter(matchingRecord)).toBe(true);
            expect(filter.filter(nonMatchingRecord)).toBe(false);
        });

        it('should match logger names with regex pattern', () => {
            filter = new NameFilter(/^app\./);

            const matchingRecord = {
                name: 'app.logger',
                level: LogLevel.INFO,
                message: 'Test message',
                timestamp: new Date(),
                levelName: 'INFO',
                args: [],
                extra: {}
            };

            const nonMatchingRecord = {
                name: 'test.logger',
                level: LogLevel.INFO,
                message: 'Test message',
                timestamp: new Date(),
                levelName: 'INFO',
                args: [],
                extra: {}
            };

            expect(filter.filter(matchingRecord)).toBe(true);
            expect(filter.filter(nonMatchingRecord)).toBe(false);
        });

        it('should handle exact name matches', () => {
            filter = new NameFilter('^exact$');

            const exactMatchRecord = {
                name: 'exact',
                level: LogLevel.INFO,
                message: 'Test message',
                timestamp: new Date(),
                levelName: 'INFO',
                args: [],
                extra: {}
            };

            const partialMatchRecord = {
                name: 'exact.logger',
                level: LogLevel.INFO,
                message: 'Test message',
                timestamp: new Date(),
                levelName: 'INFO',
                args: [],
                extra: {}
            };

            expect(filter.filter(exactMatchRecord)).toBe(true);
            expect(filter.filter(partialMatchRecord)).toBe(false);
        });

        it('should handle wildcard patterns', () => {
            filter = new NameFilter('.*\\.service$');

            const matchingRecord = {
                name: 'user.service',
                level: LogLevel.INFO,
                message: 'Test message',
                timestamp: new Date(),
                levelName: 'INFO',
                args: [],
                extra: {}
            };

            const nonMatchingRecord = {
                name: 'user.controller',
                level: LogLevel.INFO,
                message: 'Test message',
                timestamp: new Date(),
                levelName: 'INFO',
                args: [],
                extra: {}
            };

            expect(filter.filter(matchingRecord)).toBe(true);
            expect(filter.filter(nonMatchingRecord)).toBe(false);
        });

        it('should handle case sensitivity', () => {
            filter = new NameFilter('^Test\\..*');

            const matchingRecord = {
                name: 'Test.logger',
                level: LogLevel.INFO,
                message: 'Test message',
                timestamp: new Date(),
                levelName: 'INFO',
                args: [],
                extra: {}
            };

            const nonMatchingRecord = {
                name: 'test.logger',
                level: LogLevel.INFO,
                message: 'Test message',
                timestamp: new Date(),
                levelName: 'INFO',
                args: [],
                extra: {}
            };

            expect(filter.filter(matchingRecord)).toBe(true);
            expect(filter.filter(nonMatchingRecord)).toBe(false);
        });

        it('should handle case insensitive patterns', () => {
            filter = new NameFilter(/^test\./i);

            const matchingRecord1 = {
                name: 'test.logger',
                level: LogLevel.INFO,
                message: 'Test message',
                timestamp: new Date(),
                levelName: 'INFO',
                args: [],
                extra: {}
            };

            const matchingRecord2 = {
                name: 'Test.logger',
                level: LogLevel.INFO,
                message: 'Test message',
                timestamp: new Date(),
                levelName: 'INFO',
                args: [],
                extra: {}
            };

            expect(filter.filter(matchingRecord1)).toBe(true);
            expect(filter.filter(matchingRecord2)).toBe(true);
        });

        it('should handle complex patterns', () => {
            filter = new NameFilter('^(app|test)\\.(service|controller)\\..*');

            const matchingRecord1 = {
                name: 'app.service.user',
                level: LogLevel.INFO,
                message: 'Test message',
                timestamp: new Date(),
                levelName: 'INFO',
                args: [],
                extra: {}
            };

            const matchingRecord2 = {
                name: 'test.controller.auth',
                level: LogLevel.INFO,
                message: 'Test message',
                timestamp: new Date(),
                levelName: 'INFO',
                args: [],
                extra: {}
            };

            const nonMatchingRecord = {
                name: 'other.service.user',
                level: LogLevel.INFO,
                message: 'Test message',
                timestamp: new Date(),
                levelName: 'INFO',
                args: [],
                extra: {}
            };

            expect(filter.filter(matchingRecord1)).toBe(true);
            expect(filter.filter(matchingRecord2)).toBe(true);
            expect(filter.filter(nonMatchingRecord)).toBe(false);
        });

        it('should handle empty logger names', () => {
            filter = new NameFilter('^test$');

            const emptyNameRecord = {
                name: '',
                level: LogLevel.INFO,
                message: 'Test message',
                timestamp: new Date(),
                levelName: 'INFO',
                args: [],
                extra: {}
            };

            expect(filter.filter(emptyNameRecord)).toBe(false);
        });
    });
});
