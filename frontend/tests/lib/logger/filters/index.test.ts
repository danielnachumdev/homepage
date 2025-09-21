import { describe, it, expect } from 'vitest';
import {
    BaseFilter,
    LevelFilter,
    NameFilter,
    MessageFilter,
    CustomFilter,
    CompositeFilter,
} from '../../../../src/lib/logger/filters';
import { LogLevel } from '../../../../src/lib/logger/types';

describe('Filters Index', () => {
    it('should export all filter classes', () => {
        expect(BaseFilter).toBeDefined();
        expect(LevelFilter).toBeDefined();
        expect(NameFilter).toBeDefined();
        expect(MessageFilter).toBeDefined();
        expect(CustomFilter).toBeDefined();
        expect(CompositeFilter).toBeDefined();
    });

    it('should create instances of all filters', () => {
        const levelFilter = new LevelFilter(LogLevel.INFO);
        const nameFilter = new NameFilter('^test\\..*');
        const messageFilter = new MessageFilter('error');
        const customFilter = new CustomFilter((record: any) => record.level >= LogLevel.WARNING);
        const compositeFilter = new CompositeFilter([levelFilter, messageFilter], 'AND');

        expect(levelFilter).toBeInstanceOf(BaseFilter);
        expect(nameFilter).toBeInstanceOf(BaseFilter);
        expect(messageFilter).toBeInstanceOf(BaseFilter);
        expect(customFilter).toBeInstanceOf(BaseFilter);
        expect(compositeFilter).toBeInstanceOf(BaseFilter);
    });

    it('should filter records correctly', () => {
        const record = {
            name: 'test.logger',
            level: LogLevel.INFO,
            message: 'This is an error message',
            timestamp: new Date(),
            levelName: 'INFO',
            args: [],
            extra: {}
        };

        const levelFilter = new LevelFilter(LogLevel.DEBUG);
        const nameFilter = new NameFilter('^test\\..*');
        const messageFilter = new MessageFilter('error');
        const customFilter = new CustomFilter((record: any) => record.message.includes('error'));

        expect(levelFilter.filter(record)).toBe(true); // INFO >= DEBUG
        expect(nameFilter.filter(record)).toBe(true); // Matches test.*
        expect(messageFilter.filter(record)).toBe(true); // Contains 'error'
        expect(customFilter.filter(record)).toBe(true); // Contains 'error'
    });

    it('should work with composite filters', () => {
        const levelFilter = new LevelFilter(LogLevel.WARNING);
        const nameFilter = new NameFilter('^app\\..*');
        const messageFilter = new MessageFilter('error');

        const andFilter = new CompositeFilter([levelFilter, nameFilter, messageFilter], 'AND');
        const orFilter = new CompositeFilter([levelFilter, messageFilter], 'OR');

        const passRecord = {
            name: 'app.service',
            level: LogLevel.ERROR,
            message: 'Database error occurred',
            timestamp: new Date(),
            levelName: 'ERROR',
            args: [],
            extra: {}
        };

        const partialPassRecord = {
            name: 'test.service',
            level: LogLevel.ERROR,
            message: 'Database error occurred',
            timestamp: new Date(),
            levelName: 'ERROR',
            args: [],
            extra: {}
        };

        const failRecord = {
            name: 'test.service',
            level: LogLevel.INFO,
            message: 'Success message',
            timestamp: new Date(),
            levelName: 'INFO',
            args: [],
            extra: {}
        };

        expect(andFilter.filter(passRecord)).toBe(true);
        expect(andFilter.filter(partialPassRecord)).toBe(false);
        expect(andFilter.filter(failRecord)).toBe(false);

        expect(orFilter.filter(passRecord)).toBe(true);
        expect(orFilter.filter(partialPassRecord)).toBe(true); // Passes level and message
        expect(orFilter.filter(failRecord)).toBe(false);
    });
});
