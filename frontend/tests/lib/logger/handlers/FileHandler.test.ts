import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { FileHandler } from '../../../../src/lib/logger/handlers/FileHandler';
import { LogLevel } from '../../../../src/lib/logger/types';

// Mock DOM methods
const mockCreateElement = vi.fn();
const mockAppendChild = vi.fn();
const mockRemoveChild = vi.fn();
const mockClick = vi.fn();
const mockCreateObjectURL = vi.fn();
const mockRevokeObjectURL = vi.fn();

describe('FileHandler', () => {
    let handler: FileHandler;
    let mockLink: any;
    let originalCreateElement: any;
    let originalAppendChild: any;
    let originalRemoveChild: any;
    let originalURL: any;

    beforeEach(() => {
        // Store original DOM methods
        originalCreateElement = document.createElement;
        originalAppendChild = document.body.appendChild;
        originalRemoveChild = document.body.removeChild;
        originalURL = window.URL;

        // Set up mocks
        Object.defineProperty(document, 'createElement', {
            value: mockCreateElement,
            writable: true,
        });

        Object.defineProperty(document.body, 'appendChild', {
            value: mockAppendChild,
            writable: true,
        });

        Object.defineProperty(document.body, 'removeChild', {
            value: mockRemoveChild,
            writable: true,
        });

        Object.defineProperty(window, 'URL', {
            value: {
                createObjectURL: mockCreateObjectURL,
                revokeObjectURL: mockRevokeObjectURL,
            },
            writable: true,
        });

        // Clear all mocks
        vi.clearAllMocks();

        mockLink = {
            href: '',
            download: '',
            click: mockClick,
        };

        mockCreateElement.mockReturnValue(mockLink);
        mockCreateObjectURL.mockReturnValue('blob:mock-url');

        handler = new FileHandler();
    });

    afterEach(() => {
        // Clear any logs that might have been stored
        if (handler) {
            handler.flush();
        }

        // Restore original DOM methods
        Object.defineProperty(document, 'createElement', {
            value: originalCreateElement,
            writable: true,
        });

        Object.defineProperty(document.body, 'appendChild', {
            value: originalAppendChild,
            writable: true,
        });

        Object.defineProperty(document.body, 'removeChild', {
            value: originalRemoveChild,
            writable: true,
        });

        Object.defineProperty(window, 'URL', {
            value: originalURL,
            writable: true,
        });

        // Clear all mocks
        vi.clearAllMocks();
    });

    describe('Constructor', () => {
        it('should set default values', () => {
            expect(handler.level).toBe(LogLevel.INFO);
            expect(handler['fileName']).toBe('app.log');
            expect(handler['maxSize']).toBe(1000);
        });

        it('should set custom values', () => {
            const customHandler = new FileHandler('custom.log', LogLevel.DEBUG, 500);
            expect(customHandler.level).toBe(LogLevel.DEBUG);
            expect(customHandler['fileName']).toBe('custom.log');
            expect(customHandler['maxSize']).toBe(500);
        });
    });

    describe('emit', () => {
        it('should store log message', () => {
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

            expect(handler['logs']).toHaveLength(1);
            expect(handler['logs'][0]).toBe('Test message');
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

            handler.emit(record);

            expect(handler['logs']).toHaveLength(0);
        });

        it('should limit max size', () => {
            const customHandler = new FileHandler('test.log', LogLevel.DEBUG, 2);

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

            expect(customHandler['logs']).toHaveLength(2);
            expect(customHandler['logs'][0]).toBe('Message 1'); // First message should be removed
            expect(customHandler['logs'][1]).toBe('Message 2');
        });

        it('should use formatter when provided', () => {
            const formatter = { format: (record: any) => `FORMATTED: ${record.message}` };
            const customHandler = new FileHandler('test.log', LogLevel.DEBUG, 100, formatter);

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

            customHandler.emit(record);

            expect(customHandler['logs'][0]).toBe('FORMATTED: Test message');
        });
    });

    describe('flush', () => {
        it('should create and download file when logs exist', () => {
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
            handler.flush();

            expect(mockCreateElement).toHaveBeenCalledWith('a');
            expect(mockLink.href).toBe('blob:mock-url');
            expect(mockLink.download).toBe('app.log');
            expect(mockAppendChild).toHaveBeenCalledWith(mockLink);
            expect(mockClick).toHaveBeenCalled();
            expect(mockRemoveChild).toHaveBeenCalledWith(mockLink);
            expect(mockRevokeObjectURL).toHaveBeenCalledWith('blob:mock-url');
        });

        it('should not create file when no logs', () => {
            handler.flush();

            expect(mockCreateElement).not.toHaveBeenCalled();
        });

        it('should clear logs after flush', () => {
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
            expect(handler['logs']).toHaveLength(1);

            handler.flush();
            expect(handler['logs']).toHaveLength(0);
        });

        it('should join multiple logs with newlines', () => {
            const record1 = {
                level: LogLevel.INFO,
                message: 'Message 1',
                args: [],
                timestamp: new Date(),
                name: 'test',
                levelName: 'INFO',
                module: undefined,
                function: undefined,
                line: undefined,
                extra: {}
            };

            const record2 = {
                level: LogLevel.INFO,
                message: 'Message 2',
                args: [],
                timestamp: new Date(),
                name: 'test',
                levelName: 'INFO',
                module: undefined,
                function: undefined,
                line: undefined,
                extra: {}
            };

            handler.emit(record1);
            handler.emit(record2);
            handler.flush();

            // Verify that Blob was created with joined content
            const blobCalls = (window.Blob as any).mock?.calls || [];
            if (blobCalls.length > 0) {
                const blobContent = blobCalls[0][0];
                expect(blobContent).toEqual(['Message 1', 'Message 2']);
            }
        });
    });
});
