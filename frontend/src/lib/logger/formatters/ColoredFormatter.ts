import type { LogRecord } from '../types';
import { LogLevel } from '../types';
import { BaseFormatter } from './BaseFormatter';
import { StandardFormatter } from './StandardFormatter';

/**
 * Colored formatter for console output
 */
export class ColoredFormatter extends BaseFormatter {
    private baseFormatter: StandardFormatter;

    constructor(format?: string) {
        super();
        this.baseFormatter = new StandardFormatter(format);
    }

    format(record: LogRecord): string {
        const baseMessage = this.baseFormatter.format(record);
        const color = this.getColorForLevel(record.level);
        return `${color}${baseMessage}\x1b[0m`;
    }

    private getColorForLevel(level: LogLevel): string {
        switch (level) {
            case LogLevel.DEBUG:
                return '\x1b[36m'; // Cyan
            case LogLevel.INFO:
                return '\x1b[32m'; // Green
            case LogLevel.WARNING:
                return '\x1b[33m'; // Yellow
            case LogLevel.ERROR:
                return '\x1b[31m'; // Red
            case LogLevel.CRITICAL:
                return '\x1b[35m'; // Magenta
            default:
                return '\x1b[0m'; // Reset
        }
    }
}
