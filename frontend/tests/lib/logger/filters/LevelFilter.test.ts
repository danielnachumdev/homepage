import { describe, it, expect } from 'vitest';
import { LevelFilter } from '../../../../src/lib/logger/filters/LevelFilter';
import { LogLevel } from '../../../../src/lib/logger/types';

describe('LevelFilter', () => {
    let filter: LevelFilter;

    describe('Constructor', () => {
        it('should set the level', () => {
            const customFilter = new LevelFilter(LogLevel.WARNING);
            expect(customFilter['level']).toBe(LogLevel.WARNING);
        });
    });

    describe('filter', () => {
        it('should allow records at or above the filter level', () => {
            filter = new LevelFilter(LogLevel.WARNING);

            const warningRecord = {
                level: LogLevel.WARNING,
                message: 'Warning message',
                timestamp: new Date(),
                name: 'test',
                levelName: 'WARNING',
                args: [],
                extra: {}
            };

            const errorRecord = {
                level: LogLevel.ERROR,
                message: 'Error message',
                timestamp: new Date(),
                name: 'test',
                levelName: 'ERROR',
                args: [],
                extra: {}
            };

            const criticalRecord = {
                level: LogLevel.CRITICAL,
                message: 'Critical message',
                timestamp: new Date(),
                name: 'test',
                levelName: 'CRITICAL',
                args: [],
                extra: {}
            };

            expect(filter.filter(warningRecord)).toBe(true);
            expect(filter.filter(errorRecord)).toBe(true);
            expect(filter.filter(criticalRecord)).toBe(true);
        });

        it('should reject records below the filter level', () => {
            filter = new LevelFilter(LogLevel.WARNING);

            const debugRecord = {
                level: LogLevel.DEBUG,
                message: 'Debug message',
                timestamp: new Date(),
                name: 'test',
                levelName: 'DEBUG',
                args: [],
                extra: {}
            };

            const infoRecord = {
                level: LogLevel.INFO,
                message: 'Info message',
                timestamp: new Date(),
                name: 'test',
                levelName: 'INFO',
                args: [],
                extra: {}
            };

            expect(filter.filter(debugRecord)).toBe(false);
            expect(filter.filter(infoRecord)).toBe(false);
        });

        it('should handle different filter levels', () => {
            const debugFilter = new LevelFilter(LogLevel.DEBUG);
            const infoFilter = new LevelFilter(LogLevel.INFO);
            const errorFilter = new LevelFilter(LogLevel.ERROR);

            const record = {
                level: LogLevel.INFO,
                message: 'Info message',
                timestamp: new Date(),
                name: 'test',
                levelName: 'INFO',
                args: [],
                extra: {}
            };

            expect(debugFilter.filter(record)).toBe(true); // INFO >= DEBUG
            expect(infoFilter.filter(record)).toBe(true);  // INFO >= INFO
            expect(errorFilter.filter(record)).toBe(false); // INFO < ERROR
        });

        it('should handle edge cases', () => {
            filter = new LevelFilter(LogLevel.INFO);

            const exactLevelRecord = {
                level: LogLevel.INFO,
                message: 'Info message',
                timestamp: new Date(),
                name: 'test',
                levelName: 'INFO',
                args: [],
                extra: {}
            };

            const justBelowRecord = {
                level: LogLevel.DEBUG,
                message: 'Debug message',
                timestamp: new Date(),
                name: 'test',
                levelName: 'DEBUG',
                args: [],
                extra: {}
            };

            expect(filter.filter(exactLevelRecord)).toBe(true);
            expect(filter.filter(justBelowRecord)).toBe(false);
        });

        it('should handle custom numeric levels', () => {
            const customFilter = new LevelFilter(50);

            const lowLevelRecord = {
                level: 30,
                message: 'Low level message',
                timestamp: new Date(),
                name: 'test',
                levelName: 'CUSTOM',
                args: [],
                extra: {}
            };

            const highLevelRecord = {
                level: 70,
                message: 'High level message',
                timestamp: new Date(),
                name: 'test',
                levelName: 'CUSTOM',
                args: [],
                extra: {}
            };

            expect(customFilter.filter(lowLevelRecord)).toBe(false);
            expect(customFilter.filter(highLevelRecord)).toBe(true);
        });
    });
});
