import type { LogRecord, Handler, Formatter, Filter } from '../types';
import { LogLevel } from '../types';

/**
 * Base handler class
 */
export abstract class BaseHandler implements Handler {
    level: LogLevel;
    formatter?: Formatter;
    private filters: Filter[] = [];

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

    addFilter(filter: Filter): void {
        this.filters.push(filter);
    }

    removeFilter(filter: Filter): void {
        const index = this.filters.indexOf(filter);
        if (index > -1) {
            this.filters.splice(index, 1);
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
        // Check level first
        if (record.level < this.level) {
            return false;
        }

        // Apply all filters
        for (const filter of this.filters) {
            if (!filter.filter(record)) {
                return false;
            }
        }

        return true;
    }
}
