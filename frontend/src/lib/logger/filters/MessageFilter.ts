import type { LogRecord } from '../types';
import { BaseFilter } from './BaseFilter';

/**
 * Message filter - filter by message content patterns
 */
export class MessageFilter extends BaseFilter {
    private pattern: RegExp;

    constructor(pattern: string | RegExp) {
        super();
        this.pattern = typeof pattern === 'string' ? new RegExp(pattern) : pattern;
    }

    filter(record: LogRecord): boolean {
        return this.pattern.test(record.message);
    }
}
