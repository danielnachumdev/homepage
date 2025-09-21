import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { ConsoleHandler } from '../../../../src/lib/logger/handlers/ConsoleHandler';
import { LogLevel } from '../../../../src/lib/logger/types';

describe('ConsoleHandler', () => {
    let handler: ConsoleHandler;
    let consoleSpy: any;
    let originalConsole: any;

    beforeEach(() => {
        // Store original console
        originalConsole = { ...console };

        handler = new ConsoleHandler();
        consoleSpy = {
            debug: vi.fn(),
            info: vi.fn(),
            warn: vi.fn(),
            error: vi.fn(),
            log: vi.fn(),
        };

        // Mock console methods
        vi.spyOn(console, 'debug').mockImplementation(consoleSpy.debug);
        vi.spyOn(console, 'info').mockImplementation(consoleSpy.info);
        vi.spyOn(console, 'warn').mockImplementation(consoleSpy.warn);
        vi.spyOn(console, 'error').mockImplementation(consoleSpy.error);
        vi.spyOn(console, 'log').mockImplementation(consoleSpy.log);
    });

    afterEach(() => {
        // Restore original console
        Object.assign(console, originalConsole);

        // Clear all mocks
        vi.restoreAllMocks();
    });

    describe('Constructor', () => {
        it('should set default level to DEBUG', () => {
            expect(handler.level).toBe(LogLevel.DEBUG);
        });

        it('should set custom level', () => {
            const customHandler = new ConsoleHandler(LogLevel.INFO);
            expect(customHandler.level).toBe(LogLevel.INFO);
        });
    });

    describe('emit', () => {
        it('should call console.debug for DEBUG level', () => {
            const record = {
                level: LogLevel.DEBUG,
                message: 'Debug message',
                args: [],
                timestamp: new Date(),
                name: 'test',
                levelName: 'DEBUG',
                module: undefined,
                function: undefined,
                line: undefined,
                extra: {}
            };

            handler.emit(record);

            expect(consoleSpy.debug).toHaveBeenCalledWith('Debug message');
        });

        it('should call console.info for INFO level', () => {
            const record = {
                level: LogLevel.INFO,
                message: 'Info message',
                args: [],
                timestamp: new Date(),
                name: 'test',
                levelName: 'INFO',
                module: undefined,
                function: undefined,
                line: undefined,
                extra: {}
            };

            handler.emit(record);

            expect(consoleSpy.info).toHaveBeenCalledWith('Info message');
        });

        it('should call console.warn for WARNING level', () => {
            const record = {
                level: LogLevel.WARNING,
                message: 'Warning message',
                args: [],
                timestamp: new Date(),
                name: 'test',
                levelName: 'WARNING',
                module: undefined,
                function: undefined,
                line: undefined,
                extra: {}
            };

            handler.emit(record);

            expect(consoleSpy.warn).toHaveBeenCalledWith('Warning message');
        });

        it('should call console.error for ERROR level', () => {
            const record = {
                level: LogLevel.ERROR,
                message: 'Error message',
                args: [],
                timestamp: new Date(),
                name: 'test',
                levelName: 'ERROR',
                module: undefined,
                function: undefined,
                line: undefined,
                extra: {}
            };

            handler.emit(record);

            expect(consoleSpy.error).toHaveBeenCalledWith('Error message');
        });

        it('should call console.error for CRITICAL level', () => {
            const record = {
                level: LogLevel.CRITICAL,
                message: 'Critical message',
                args: [],
                timestamp: new Date(),
                name: 'test',
                levelName: 'CRITICAL',
                module: undefined,
                function: undefined,
                line: undefined,
                extra: {}
            };

            handler.emit(record);

            expect(consoleSpy.error).toHaveBeenCalledWith('Critical message');
        });

        it('should call console.log for unknown level', () => {
            const record = {
                level: 999 as any, // Unknown level
                message: 'Unknown message',
                args: [],
                timestamp: new Date(),
                name: 'test',
                levelName: 'UNKNOWN',
                module: undefined,
                function: undefined,
                line: undefined,
                extra: {}
            };

            handler.emit(record);

            expect(consoleSpy.log).toHaveBeenCalledWith('Unknown message');
        });

        it('should pass additional arguments to console method', () => {
            const record = {
                level: LogLevel.INFO,
                message: 'Info message',
                args: [{ data: 'test' }, 'extra'],
                timestamp: new Date(),
                name: 'test',
                levelName: 'INFO',
                module: undefined,
                function: undefined,
                line: undefined,
                extra: {}
            };

            handler.emit(record);

            expect(consoleSpy.info).toHaveBeenCalledWith('Info message', { data: 'test' }, 'extra');
        });

        it('should not emit when level is below handler level', () => {
            handler.level = LogLevel.WARNING;

            const record = {
                level: LogLevel.INFO,
                message: 'Info message',
                args: [],
                timestamp: new Date(),
                name: 'test',
                levelName: 'INFO',
                module: undefined,
                function: undefined,
                line: undefined,
                extra: {}
            };

            handler.handle(record);

            expect(consoleSpy.info).not.toHaveBeenCalled();
        });

        it('should use formatter when provided', () => {
            const formatter = { format: (record: any) => `FORMATTED: ${record.message}` };
            const customHandler = new ConsoleHandler(LogLevel.DEBUG, formatter);

            const record = {
                level: LogLevel.INFO,
                message: 'Info message',
                args: [],
                timestamp: new Date(),
                name: 'test',
                levelName: 'INFO',
                module: undefined,
                function: undefined,
                line: undefined,
                extra: {}
            };

            customHandler.emit(record);

            expect(consoleSpy.info).toHaveBeenCalledWith('FORMATTED: Info message');
        });
    });
});
