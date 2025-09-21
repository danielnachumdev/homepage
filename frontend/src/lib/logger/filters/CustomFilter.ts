import type { LogRecord } from '../types';
import { BaseFilter } from './BaseFilter';

/**
 * Custom filter - allow custom filtering logic
 */
export class CustomFilter extends BaseFilter {
    private filterFn: (record: LogRecord) => boolean;

    constructor(filterFn: (record: LogRecord) => boolean) {
        super();
        this.filterFn = filterFn;
    }

    filter(record: LogRecord): boolean {
        return this.filterFn(record);
    }
}
