import { describe, it, expect } from 'vitest';
import {
    BaseHandler,
    ConsoleHandler,
    FileHandler,
    LocalStorageHandler,
    RemoteHandler,
    TestHandler,
} from '../../../../src/lib/logger/handlers';
import { LogLevel } from '../../../../src/lib/logger/types';

describe('Handlers Index', () => {
    it('should export all handler classes', () => {
        expect(BaseHandler).toBeDefined();
        expect(ConsoleHandler).toBeDefined();
        expect(FileHandler).toBeDefined();
        expect(LocalStorageHandler).toBeDefined();
        expect(RemoteHandler).toBeDefined();
        expect(TestHandler).toBeDefined();
    });

    it('should create instances of all handlers', () => {
        const consoleHandler = new ConsoleHandler();
        const fileHandler = new FileHandler();
        const localStorageHandler = new LocalStorageHandler();
        const remoteHandler = new RemoteHandler('http://test.com');
        const testHandler = new TestHandler();

        expect(consoleHandler).toBeInstanceOf(BaseHandler);
        expect(fileHandler).toBeInstanceOf(BaseHandler);
        expect(localStorageHandler).toBeInstanceOf(BaseHandler);
        expect(remoteHandler).toBeInstanceOf(BaseHandler);
        expect(testHandler).toBeInstanceOf(BaseHandler);
    });

    it('should have correct default levels', () => {
        const consoleHandler = new ConsoleHandler();
        const fileHandler = new FileHandler();
        const localStorageHandler = new LocalStorageHandler();
        const remoteHandler = new RemoteHandler('http://test.com');
        const testHandler = new TestHandler();

        expect(consoleHandler.level).toBe(LogLevel.DEBUG);
        expect(fileHandler.level).toBe(LogLevel.INFO);
        expect(localStorageHandler.level).toBe(LogLevel.INFO);
        expect(remoteHandler.level).toBe(LogLevel.ERROR);
        expect(testHandler.level).toBe(LogLevel.NOTSET);
    });
});
