import type { LogRecord, Formatter } from '../types';

/**
 * Base formatter class
 */
export abstract class BaseFormatter implements Formatter {
    abstract format(record: LogRecord): string;
}
