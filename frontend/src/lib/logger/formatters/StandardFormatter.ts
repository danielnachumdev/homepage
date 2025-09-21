import type { LogRecord } from '../types';
import { BaseFormatter } from './BaseFormatter';

/**
 * Standard formatter similar to Python's logging
 */
export class StandardFormatter extends BaseFormatter {
    private formatString: string;

    constructor(format?: string) {
        super();
        this.formatString = format || '%(asctime)s - %(name)s - %(levelname)s - %(message)s';
    }

    format(record: LogRecord): string {
        let formatted = this.formatString;

        // Replace format specifiers
        formatted = formatted.replace("%(asctime)s", this.formatTime(record.timestamp));
        formatted = formatted.replace("%(name)s", record.name);
        formatted = formatted.replace("%(levelname)s", record.levelName);
        formatted = formatted.replace("%(message)s", record.message);
        formatted = formatted.replace("%(module)s", record.module || '');
        formatted = formatted.replace("%(funcName)s", record.function || '');
        formatted = formatted.replace("%(lineno)d", record.line?.toString() || '0');
        formatted = formatted.replace("%(pathname)s", record.module || '');
        formatted = formatted.replace("%(process)d", '0');
        formatted = formatted.replace("%(thread)d", '0');

        return formatted;
    }

    private formatTime(date: Date): string {
        return date.toISOString();
    }
}
