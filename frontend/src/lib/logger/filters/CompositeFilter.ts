import type { LogRecord, Filter } from '../types';
import { BaseFilter } from './BaseFilter';

/**
 * Composite filter - combine multiple filters with AND/OR logic
 */
export class CompositeFilter extends BaseFilter {
    private filters: Filter[];
    private operator: 'AND' | 'OR';

    constructor(filters: Filter[], operator: 'AND' | 'OR' = 'AND') {
        super();
        this.filters = filters;
        this.operator = operator;
    }

    filter(record: LogRecord): boolean {
        if (this.filters.length === 0) {
            return true;
        }

        if (this.operator === 'AND') {
            return this.filters.every(filter => filter.filter(record));
        } else {
            return this.filters.some(filter => filter.filter(record));
        }
    }
}
