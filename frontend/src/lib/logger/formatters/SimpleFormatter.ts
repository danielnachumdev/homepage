import type { LogRecord } from '../types';
import { BaseFormatter } from './BaseFormatter';

/**
 * Simple formatter - just the message
 */
export class SimpleFormatter extends BaseFormatter {
    format(record: LogRecord): string {
        return record.message;
    }
}
