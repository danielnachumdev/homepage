import type { LogRecord, Handler, Formatter } from '../types';
import { LogLevel } from '../types';
import { BaseHandler } from './BaseHandler';

/**
 * Local storage handler for persistent logging in browser
 */
export class LocalStorageHandler extends BaseHandler {
    private storageKey: string;
    private maxEntries: number;

    constructor(
        storageKey: string = 'app_logs',
        level: LogLevel = LogLevel.INFO,
        maxEntries: number = 1000,
        formatter?: Formatter
    ) {
        super(level, formatter);
        this.storageKey = storageKey;
        this.maxEntries = maxEntries;
    }

    emit(record: LogRecord): void {
        try {
            const message = this.format(record);
            const logs = this.getStoredLogs();
            logs.push(message);

            // Keep only the last maxEntries logs
            if (logs.length > this.maxEntries) {
                logs.splice(0, logs.length - this.maxEntries);
            }

            localStorage.setItem(this.storageKey, JSON.stringify(logs));
        } catch (error) {
            console.error('Failed to store log in localStorage:', error);
        }
    }

    private getStoredLogs(): string[] {
        try {
            const stored = localStorage.getItem(this.storageKey);
            return stored ? JSON.parse(stored) : [];
        } catch {
            return [];
        }
    }

    getLogs(): string[] {
        return this.getStoredLogs();
    }

    clearLogs(): void {
        localStorage.removeItem(this.storageKey);
    }
}
