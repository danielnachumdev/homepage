import type { LogRecord, Filter } from '../types';

/**
 * Base filter class
 */
export abstract class BaseFilter implements Filter {
    abstract filter(record: LogRecord): boolean;
}
