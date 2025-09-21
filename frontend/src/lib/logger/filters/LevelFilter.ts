import type { LogRecord } from '../types';
import { BaseFilter } from './BaseFilter';

/**
 * Level filter - only allow logs at or above a certain level
 */
export class LevelFilter extends BaseFilter {
    private level: number;

    constructor(level: number) {
        super();
        this.level = level;
    }

    filter(record: LogRecord): boolean {
        return record.level >= this.level;
    }
}
