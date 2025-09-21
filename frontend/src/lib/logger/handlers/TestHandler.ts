import type { LogRecord, Handler } from '../types';
import { LogLevel } from '../types';
import { BaseHandler } from './BaseHandler';

/**
 * Test handler that captures log records for testing purposes
 */
export class TestHandler extends BaseHandler {
    public capturedRecords: LogRecord[] = [];
    public emittedRecords: LogRecord[] = [];

    constructor(level: LogLevel = LogLevel.NOTSET) {
        super(level);
    }

    emit(record: LogRecord): void {
        this.capturedRecords.push(record);
        this.emittedRecords.push(record);
    }

    handle(record: LogRecord): void {
        // Always capture the record
        this.capturedRecords.push(record);

        // Only emit if it passes the level filter
        if (this.shouldEmit(record)) {
            this.emittedRecords.push(record);
        }
    }

    flush(): void {
        // No-op for test handler
    }

    close(): void {
        // No-op for test handler
    }

    /**
     * Get all captured records
     */
    getCapturedRecords(): LogRecord[] {
        return [...this.capturedRecords];
    }

    /**
     * Get only emitted records (after level filtering)
     */
    getEmittedRecords(): LogRecord[] {
        return [...this.emittedRecords];
    }

    /**
     * Get records by level
     */
    getRecordsByLevel(level: LogLevel): LogRecord[] {
        return this.capturedRecords.filter(record => record.level === level);
    }

    /**
     * Get records by logger name
     */
    getRecordsByName(name: string): LogRecord[] {
        return this.capturedRecords.filter(record => record.name === name);
    }

    /**
     * Get records by message content
     */
    getRecordsByMessage(message: string): LogRecord[] {
        return this.capturedRecords.filter(record => record.message.includes(message));
    }

    /**
     * Clear all captured records
     */
    clear(): void {
        this.capturedRecords = [];
        this.emittedRecords = [];
    }

    /**
     * Get count of captured records
     */
    getRecordCount(): number {
        return this.capturedRecords.length;
    }

    /**
     * Get count of emitted records
     */
    getEmittedCount(): number {
        return this.emittedRecords.length;
    }

    /**
     * Check if a specific message was logged
     */
    hasMessage(message: string): boolean {
        return this.capturedRecords.some(record => record.message.includes(message));
    }

    /**
     * Check if a specific level was logged
     */
    hasLevel(level: LogLevel): boolean {
        return this.capturedRecords.some(record => record.level === level);
    }

    /**
     * Get the last captured record
     */
    getLastRecord(): LogRecord | undefined {
        return this.capturedRecords[this.capturedRecords.length - 1];
    }

    /**
     * Get the last emitted record
     */
    getLastEmittedRecord(): LogRecord | undefined {
        return this.emittedRecords[this.emittedRecords.length - 1];
    }
}
