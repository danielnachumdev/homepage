import type { LogRecord, Handler, Formatter } from '../types';
import { LogLevel } from '../types';

/**
 * Base handler class
 */
export abstract class BaseHandler implements Handler {
    level: LogLevel;
    formatter?: Formatter;

    constructor(level: LogLevel = LogLevel.NOTSET, formatter?: Formatter) {
        this.level = level;
        this.formatter = formatter;
    }

    abstract emit(record: LogRecord): void;

    handle(record: LogRecord): void {
        if (this.shouldEmit(record)) {
            this.emit(record);
        }
    }

    flush?(): void;
    close?(): void;

    format(record: LogRecord): string {
        if (this.formatter) {
            return this.formatter.format(record);
        }
        return record.message;
    }

    shouldEmit(record: LogRecord): boolean {
        return record.level >= this.level;
    }
}
