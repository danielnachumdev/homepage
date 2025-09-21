import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { LocalStorageHandler } from '../../../../src/lib/logger/handlers/LocalStorageHandler';
import { LogLevel } from '../../../../src/lib/logger/types';

// Mock localStorage
const localStorageMock = {
    getItem: vi.fn(),
    setItem: vi.fn(),
    removeItem: vi.fn(),
    clear: vi.fn(),
};

Object.defineProperty(window, 'localStorage', {
    value: localStorageMock,
});

describe('LocalStorageHandler', () => {
    let handler: LocalStorageHandler;
    let originalLocalStorage: Storage;

    beforeEach(() => {
        // Store original localStorage
        originalLocalStorage = window.localStorage;

        // Clear all mocks
        vi.clearAllMocks();

        // Reset localStorage mock state
        localStorageMock.getItem.mockReturnValue('[]');
        localStorageMock.setItem.mockClear();
        localStorageMock.removeItem.mockClear();
        localStorageMock.clear.mockClear();

        handler = new LocalStorageHandler();
    });

    afterEach(() => {
        // Clear any logs that might have been stored
        if (handler) {
            handler.clearLogs();
        }

        // Restore original localStorage
        Object.defineProperty(window, 'localStorage', {
            value: originalLocalStorage,
            writable: true,
        });

        // Clear all mocks
        vi.clearAllMocks();
    });

    describe('Constructor', () => {
        it('should set default values', () => {
            expect(handler.level).toBe(LogLevel.INFO);
            expect(handler['storageKey']).toBe('app_logs');
            expect(handler['maxEntries']).toBe(1000);
        });

        it('should set custom values', () => {
            const customHandler = new LocalStorageHandler('custom_key', LogLevel.DEBUG, 500);
            expect(customHandler.level).toBe(LogLevel.DEBUG);
            expect(customHandler['storageKey']).toBe('custom_key');
            expect(customHandler['maxEntries']).toBe(500);
        });
    });

    describe('emit', () => {
        it('should store log in localStorage', () => {
            const record = {
                level: LogLevel.INFO,
                message: 'Test message',
                args: [],
                timestamp: new Date(),
                name: 'test',
                levelName: 'INFO',
                module: undefined,
                function: undefined,
                line: undefined,
                extra: {}
            };

            localStorageMock.getItem.mockReturnValue('[]');

            handler.emit(record);

            expect(localStorageMock.setItem).toHaveBeenCalledWith(
                'app_logs',
                expect.stringContaining('Test message')
            );
        });

        it('should append to existing logs', () => {
            const existingLogs = ['{"message":"Existing log"}'];
            localStorageMock.getItem.mockReturnValue(JSON.stringify(existingLogs));

            const record = {
                level: LogLevel.INFO,
                message: 'New message',
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

            const setItemCall = localStorageMock.setItem.mock.calls[0];
            const storedLogs = JSON.parse(setItemCall[1]);
            expect(storedLogs).toHaveLength(2);
            expect(storedLogs[0]).toBe('{"message":"Existing log"}');
            expect(storedLogs[1]).toContain('New message');
        });

        it('should respect level filtering', () => {
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

            localStorageMock.getItem.mockReturnValue('[]');

            handler.emit(record);

            expect(localStorageMock.setItem).not.toHaveBeenCalled();
        });

        it('should limit max entries', () => {
            const customHandler = new LocalStorageHandler('test_key', LogLevel.DEBUG, 2);
            localStorageMock.getItem.mockReturnValue('[]');

            // Emit 3 records
            for (let i = 0; i < 3; i++) {
                const record = {
                    level: LogLevel.INFO,
                    message: `Message ${i}`,
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
            }

            const setItemCalls = localStorageMock.setItem.mock.calls;
            const lastCall = setItemCalls[setItemCalls.length - 1];
            const storedLogs = JSON.parse(lastCall[1]);
            expect(storedLogs).toHaveLength(2);
            expect(storedLogs[0]).toContain('Message 1'); // First message should be removed
            expect(storedLogs[1]).toContain('Message 2');
        });

        it('should handle localStorage errors gracefully', () => {
            localStorageMock.setItem.mockImplementation(() => {
                throw new Error('Storage quota exceeded');
            });

            const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => { });

            const record = {
                level: LogLevel.INFO,
                message: 'Test message',
                args: [],
                timestamp: new Date(),
                name: 'test',
                levelName: 'INFO',
                module: undefined,
                function: undefined,
                line: undefined,
                extra: {}
            };

            localStorageMock.getItem.mockReturnValue('[]');

            handler.emit(record);

            expect(consoleSpy).toHaveBeenCalledWith(
                'Failed to store log in localStorage:',
                expect.any(Error)
            );

            consoleSpy.mockRestore();
        });

        it('should handle corrupted localStorage data', () => {
            localStorageMock.getItem.mockReturnValue('invalid json');

            const record = {
                level: LogLevel.INFO,
                message: 'Test message',
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

            expect(localStorageMock.setItem).toHaveBeenCalled();
        });
    });

    describe('getLogs', () => {
        it('should return stored logs', () => {
            const expectedLogs = ['{"message":"Log 1"}', '{"message":"Log 2"}'];
            localStorageMock.getItem.mockReturnValue(JSON.stringify(expectedLogs));

            const logs = handler.getLogs();
            expect(logs).toEqual(expectedLogs);
        });

        it('should return empty array when no logs', () => {
            localStorageMock.getItem.mockReturnValue(null);

            const logs = handler.getLogs();
            expect(logs).toEqual([]);
        });

        it('should return empty array on parse error', () => {
            localStorageMock.getItem.mockReturnValue('invalid json');

            const logs = handler.getLogs();
            expect(logs).toEqual([]);
        });
    });

    describe('clearLogs', () => {
        it('should remove logs from localStorage', () => {
            handler.clearLogs();
            expect(localStorageMock.removeItem).toHaveBeenCalledWith('app_logs');
        });
    });
});
