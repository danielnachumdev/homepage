import type { LogRecord } from '../types';
import { BaseFilter } from './BaseFilter';

/**
 * Name filter - filter by logger name patterns
 */
export class NameFilter extends BaseFilter {
    private pattern: RegExp;

    constructor(pattern: string | RegExp) {
        super();
        this.pattern = typeof pattern === 'string' ? new RegExp(pattern) : pattern;
    }

    filter(record: LogRecord): boolean {
        return this.pattern.test(record.name);
    }
}
