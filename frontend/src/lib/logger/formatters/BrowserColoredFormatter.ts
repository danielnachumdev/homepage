import type { LogRecord } from '../types';
import { LogLevel } from '../types';
import { BaseFormatter } from './BaseFormatter';
import { StandardFormatter } from './StandardFormatter';

/**
 * Browser-compatible colored formatter for console output
 * Uses CSS styling instead of ANSI escape codes
 */
export class BrowserColoredFormatter extends BaseFormatter {
    private baseFormatter: StandardFormatter;

    constructor(format?: string) {
        super();
        this.baseFormatter = new StandardFormatter(format);
    }

    format(record: LogRecord): string {
        const baseMessage = this.baseFormatter.format(record);
        return `%c${baseMessage}`;
    }

    getConsoleStyle(level: LogLevel): string {
        switch (level) {
            case LogLevel.DEBUG:
                return 'color: #00BCD4; font-weight: normal;'; // Cyan
            case LogLevel.INFO:
                return 'color: #4CAF50; font-weight: normal;'; // Green
            case LogLevel.WARNING:
                return 'color: #FF9800; font-weight: bold;'; // Orange
            case LogLevel.ERROR:
                return 'color: #F44336; font-weight: bold;'; // Red
            case LogLevel.CRITICAL:
                return 'color: #9C27B0; font-weight: bold; background: #FFEBEE;'; // Purple with background
            default:
                return 'color: #000000; font-weight: normal;'; // Black
        }
    }

    private getColorForLevel(_level: LogLevel): string {
        // This method is kept for compatibility but not used in browser
        return '';
    }
}
