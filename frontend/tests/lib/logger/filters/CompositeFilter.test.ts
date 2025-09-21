import { describe, it, expect, beforeEach } from 'vitest';
import { CompositeFilter } from '../../../../src/lib/logger/filters/CompositeFilter';
import { LevelFilter } from '../../../../src/lib/logger/filters/LevelFilter';
import { NameFilter } from '../../../../src/lib/logger/filters/NameFilter';
import { MessageFilter } from '../../../../src/lib/logger/filters/MessageFilter';
import { LogLevel } from '../../../../src/lib/logger/types';

describe('CompositeFilter', () => {
    let filter: CompositeFilter;

    describe('Constructor', () => {
        it('should set default operator to AND', () => {
            const filters = [new LevelFilter(LogLevel.INFO)];
            filter = new CompositeFilter(filters);
            expect(filter['operator']).toBe('AND');
        });

        it('should set custom operator', () => {
            const filters = [new LevelFilter(LogLevel.INFO)];
            filter = new CompositeFilter(filters, 'OR');
            expect(filter['operator']).toBe('OR');
        });

        it('should store filters array', () => {
            const filters = [new LevelFilter(LogLevel.INFO), new NameFilter('test')];
            filter = new CompositeFilter(filters);
            expect(filter['filters']).toBe(filters);
        });
    });

    describe('filter with AND operator', () => {
        beforeEach(() => {
            const levelFilter = new LevelFilter(LogLevel.WARNING);
            const nameFilter = new NameFilter('^app\\..*');
            const messageFilter = new MessageFilter('error');

            filter = new CompositeFilter([levelFilter, nameFilter, messageFilter], 'AND');
        });

        it('should pass when all filters pass', () => {
            const record = {
                name: 'app.service',
                level: LogLevel.ERROR,
                message: 'Database error occurred',
                timestamp: new Date(),
                levelName: 'ERROR',
                args: [],
                extra: {}
            };

            expect(filter.filter(record)).toBe(true);
        });

        it('should fail when any filter fails', () => {
            const levelFailRecord = {
                name: 'app.service',
                level: LogLevel.INFO, // Below WARNING
                message: 'Database error occurred',
                timestamp: new Date(),
                levelName: 'INFO',
                args: [],
                extra: {}
            };

            const nameFailRecord = {
                name: 'test.service', // Doesn't match app.*
                level: LogLevel.ERROR,
                message: 'Database error occurred',
                timestamp: new Date(),
                levelName: 'ERROR',
                args: [],
                extra: {}
            };

            const messageFailRecord = {
                name: 'app.service',
                level: LogLevel.ERROR,
                message: 'Database success occurred', // Doesn't contain 'error'
                timestamp: new Date(),
                levelName: 'ERROR',
                args: [],
                extra: {}
            };

            expect(filter.filter(levelFailRecord)).toBe(false);
            expect(filter.filter(nameFailRecord)).toBe(false);
            expect(filter.filter(messageFailRecord)).toBe(false);
        });

        it('should fail when multiple filters fail', () => {
            const record = {
                name: 'test.service', // Wrong name
                level: LogLevel.INFO, // Wrong level
                message: 'Success message', // Wrong message
                timestamp: new Date(),
                levelName: 'INFO',
                args: [],
                extra: {}
            };

            expect(filter.filter(record)).toBe(false);
        });
    });

    describe('filter with OR operator', () => {
        beforeEach(() => {
            const levelFilter = new LevelFilter(LogLevel.ERROR);
            const nameFilter = new NameFilter('^critical\\..*');
            const messageFilter = new MessageFilter('urgent');

            filter = new CompositeFilter([levelFilter, nameFilter, messageFilter], 'OR');
        });

        it('should pass when any filter passes', () => {
            const levelPassRecord = {
                name: 'app.service',
                level: LogLevel.ERROR, // Passes level filter
                message: 'Regular message',
                timestamp: new Date(),
                levelName: 'ERROR',
                args: [],
                extra: {}
            };

            const namePassRecord = {
                name: 'critical.system', // Passes name filter
                level: LogLevel.INFO,
                message: 'Regular message',
                timestamp: new Date(),
                levelName: 'INFO',
                args: [],
                extra: {}
            };

            const messagePassRecord = {
                name: 'app.service',
                level: LogLevel.INFO,
                message: 'This is urgent', // Passes message filter
                timestamp: new Date(),
                levelName: 'INFO',
                args: [],
                extra: {}
            };

            expect(filter.filter(levelPassRecord)).toBe(true);
            expect(filter.filter(namePassRecord)).toBe(true);
            expect(filter.filter(messagePassRecord)).toBe(true);
        });

        it('should pass when multiple filters pass', () => {
            const record = {
                name: 'critical.system', // Passes name filter
                level: LogLevel.ERROR, // Passes level filter
                message: 'This is urgent', // Passes message filter
                timestamp: new Date(),
                levelName: 'ERROR',
                args: [],
                extra: {}
            };

            expect(filter.filter(record)).toBe(true);
        });

        it('should fail when all filters fail', () => {
            const record = {
                name: 'app.service', // Fails name filter
                level: LogLevel.INFO, // Fails level filter
                message: 'Regular message', // Fails message filter
                timestamp: new Date(),
                levelName: 'INFO',
                args: [],
                extra: {}
            };

            expect(filter.filter(record)).toBe(false);
        });
    });

    describe('filter with empty filters array', () => {
        it('should return true for AND operator', () => {
            filter = new CompositeFilter([], 'AND');

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

        it('should return true for OR operator', () => {
            filter = new CompositeFilter([], 'OR');

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
    });

    describe('filter with single filter', () => {
        it('should work with AND operator', () => {
            const levelFilter = new LevelFilter(LogLevel.WARNING);
            filter = new CompositeFilter([levelFilter], 'AND');

            const passRecord = {
                name: 'test',
                level: LogLevel.ERROR,
                message: 'Any message',
                timestamp: new Date(),
                levelName: 'ERROR',
                args: [],
                extra: {}
            };

            const failRecord = {
                name: 'test',
                level: LogLevel.INFO,
                message: 'Any message',
                timestamp: new Date(),
                levelName: 'INFO',
                args: [],
                extra: {}
            };

            expect(filter.filter(passRecord)).toBe(true);
            expect(filter.filter(failRecord)).toBe(false);
        });

        it('should work with OR operator', () => {
            const levelFilter = new LevelFilter(LogLevel.WARNING);
            filter = new CompositeFilter([levelFilter], 'OR');

            const passRecord = {
                name: 'test',
                level: LogLevel.ERROR,
                message: 'Any message',
                timestamp: new Date(),
                levelName: 'ERROR',
                args: [],
                extra: {}
            };

            const failRecord = {
                name: 'test',
                level: LogLevel.INFO,
                message: 'Any message',
                timestamp: new Date(),
                levelName: 'INFO',
                args: [],
                extra: {}
            };

            expect(filter.filter(passRecord)).toBe(true);
            expect(filter.filter(failRecord)).toBe(false);
        });
    });

    describe('complex filter combinations', () => {
        it('should handle nested composite filters', () => {
            const levelFilter = new LevelFilter(LogLevel.WARNING);
            const nameFilter = new NameFilter('^app\\..*');
            const messageFilter = new MessageFilter('error');

            const innerFilter = new CompositeFilter([levelFilter, nameFilter], 'AND');
            const outerFilter = new CompositeFilter([innerFilter, messageFilter], 'AND');

            filter = outerFilter;

            const passRecord = {
                name: 'app.service',
                level: LogLevel.ERROR,
                message: 'Database error occurred',
                timestamp: new Date(),
                levelName: 'ERROR',
                args: [],
                extra: {}
            };

            const failRecord = {
                name: 'test.service', // Fails name filter
                level: LogLevel.ERROR,
                message: 'Database error occurred',
                timestamp: new Date(),
                levelName: 'ERROR',
                args: [],
                extra: {}
            };

            expect(filter.filter(passRecord)).toBe(true);
            expect(filter.filter(failRecord)).toBe(false);
        });

        it('should handle mixed AND and OR operations', () => {
            const levelFilter = new LevelFilter(LogLevel.WARNING);
            const nameFilter = new NameFilter('^app\\..*');
            const messageFilter = new MessageFilter('error');
            const urgentFilter = new MessageFilter('urgent');

            // (level AND name) OR (urgent message)
            const andFilter = new CompositeFilter([levelFilter, nameFilter], 'AND');
            const orFilter = new CompositeFilter([andFilter, urgentFilter], 'OR');

            filter = orFilter;

            const levelNamePassRecord = {
                name: 'app.service',
                level: LogLevel.ERROR,
                message: 'Database error occurred',
                timestamp: new Date(),
                levelName: 'ERROR',
                args: [],
                extra: {}
            };

            const urgentPassRecord = {
                name: 'test.service',
                level: LogLevel.INFO,
                message: 'This is urgent',
                timestamp: new Date(),
                levelName: 'INFO',
                args: [],
                extra: {}
            };

            const failRecord = {
                name: 'test.service',
                level: LogLevel.INFO,
                message: 'Regular message',
                timestamp: new Date(),
                levelName: 'INFO',
                args: [],
                extra: {}
            };

            expect(filter.filter(levelNamePassRecord)).toBe(true);
            expect(filter.filter(urgentPassRecord)).toBe(true);
            expect(filter.filter(failRecord)).toBe(false);
        });
    });
});
