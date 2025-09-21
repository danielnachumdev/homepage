import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { RemoteHandler } from '../../../../src/lib/logger/handlers/RemoteHandler';
import { LogLevel } from '../../../../src/lib/logger/types';

// Mock fetch
const mockFetch = vi.fn();
global.fetch = mockFetch;

// Mock setTimeout and clearTimeout
const mockSetTimeout = vi.fn();
const mockClearTimeout = vi.fn();

describe('RemoteHandler', () => {
    let handler: RemoteHandler;
    let originalFetch: any;
    let originalSetTimeout: any;
    let originalClearTimeout: any;

    beforeEach(() => {
        // Store original functions
        originalFetch = global.fetch;
        originalSetTimeout = window.setTimeout;
        originalClearTimeout = window.clearTimeout;

        // Set up mocks
        global.fetch = mockFetch;
        Object.defineProperty(window, 'setTimeout', {
            value: mockSetTimeout,
            writable: true,
        });

        Object.defineProperty(window, 'clearTimeout', {
            value: mockClearTimeout,
            writable: true,
        });

        vi.clearAllMocks();
        mockFetch.mockResolvedValue({
            ok: true,
            status: 200,
            json: () => Promise.resolve({ success: true })
        });
        mockSetTimeout.mockImplementation((fn: Function) => {
            fn();
            return 123; // Mock timeout ID
        });
        handler = new RemoteHandler('http://localhost:3000/logs');
    });

    afterEach(() => {
        // Close handler to flush any pending logs
        if (handler) {
            handler.close();
        }

        // Restore original functions
        global.fetch = originalFetch;
        Object.defineProperty(window, 'setTimeout', {
            value: originalSetTimeout,
            writable: true,
        });

        Object.defineProperty(window, 'clearTimeout', {
            value: originalClearTimeout,
            writable: true,
        });

        vi.restoreAllMocks();
    });

    describe('Constructor', () => {
        it('should set default values', () => {
            expect(handler.level).toBe(LogLevel.ERROR);
            expect(handler['endpoint']).toBe('http://localhost:3000/logs');
            expect(handler['batchSize']).toBe(10);
            expect(handler['batchTimeout']).toBe(5000);
        });

        it('should set custom values', () => {
            const customHandler = new RemoteHandler(
                'http://custom.com/logs',
                LogLevel.INFO,
                5,
                2000
            );
            expect(customHandler.level).toBe(LogLevel.INFO);
            expect(customHandler['endpoint']).toBe('http://custom.com/logs');
            expect(customHandler['batchSize']).toBe(5);
            expect(customHandler['batchTimeout']).toBe(2000);
        });
    });

    describe('emit', () => {
        it('should add record to batch', () => {
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

            expect(handler['batch']).toHaveLength(1);
            expect(handler['batch'][0]).toEqual(record);
        });

        it('should respect level filtering', () => {
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

            expect(handler['batch']).toHaveLength(0);
        });

        it('should flush when batch size is reached', () => {
            const flushSpy = vi.spyOn(handler, 'flush');

            // Add records up to batch size
            for (let i = 0; i < 10; i++) {
                const record = {
                    level: LogLevel.ERROR,
                    message: `Error ${i}`,
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
            }

            expect(flushSpy).toHaveBeenCalled();
        });

        it('should set timeout for first record in batch', () => {
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

            expect(mockSetTimeout).toHaveBeenCalledWith(expect.any(Function), 5000);
            expect(handler['timeoutId']).toBe(123);
        });

        it('should not set timeout if one already exists', () => {
            handler['timeoutId'] = 456;

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

            expect(mockSetTimeout).not.toHaveBeenCalled();
        });
    });

    describe('flush', () => {
        it('should send logs to server', async () => {
            mockFetch.mockResolvedValue({ ok: true });

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
            handler.flush();

            expect(mockFetch).toHaveBeenCalledWith(
                'http://localhost:3000/logs',
                {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: expect.stringContaining('Error message'),
                }
            );
        });

        it('should clear batch after flush', () => {
            mockFetch.mockResolvedValue({ ok: true });

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
            expect(handler['batch']).toHaveLength(1);

            handler.flush();
            expect(handler['batch']).toHaveLength(0);
        });

        it('should clear timeout after flush', () => {
            mockFetch.mockResolvedValue({ ok: true });
            handler['timeoutId'] = 123;

            handler.flush();

            expect(mockClearTimeout).toHaveBeenCalledWith(123);
            expect(handler['timeoutId']).toBeUndefined();
        });

        it('should not send request when batch is empty', () => {
            handler.flush();

            expect(mockFetch).not.toHaveBeenCalled();
        });

        it('should handle fetch errors', async () => {
            const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => { });
            mockFetch.mockRejectedValue(new Error('Network error'));

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
            handler.flush();

            // Wait for async operation
            await new Promise(resolve => setTimeout(resolve, 0));

            expect(consoleSpy).toHaveBeenCalledWith(
                'Failed to send logs to server:',
                expect.any(Error)
            );

            consoleSpy.mockRestore();
        });

        it('should format logs using formatter', () => {
            const formatter = { format: (record: any) => `FORMATTED: ${record.message}` };
            const customHandler = new RemoteHandler(
                'http://localhost:3000/logs',
                LogLevel.ERROR,
                1,
                1000,
                formatter
            );

            mockFetch.mockResolvedValue({ ok: true });

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

            customHandler.emit(record);
            customHandler.flush();

            expect(mockFetch).toHaveBeenCalledWith(
                'http://localhost:3000/logs',
                expect.objectContaining({
                    body: expect.stringContaining('FORMATTED: Error message'),
                })
            );
        });
    });

    describe('close', () => {
        it('should flush remaining logs', () => {
            const flushSpy = vi.spyOn(handler, 'flush');

            handler.close();

            expect(flushSpy).toHaveBeenCalled();
        });
    });
});
