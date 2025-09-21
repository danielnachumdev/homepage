import type { LogRecord, Handler, Formatter } from '../types';
import { LogLevel } from '../types';
import { BaseHandler } from './BaseHandler';
import { BrowserColoredFormatter } from '../formatters/BrowserColoredFormatter';
import { StandardFormatter } from '../formatters/StandardFormatter';

/**
 * Browser console handler for styled console output
 */
export class BrowserConsoleHandler extends BaseHandler {
    constructor(level: LogLevel = LogLevel.DEBUG, formatter?: Formatter) {
        super(level, formatter || new StandardFormatter());
    }

    emit(record: LogRecord): void {
        const message = this.format(record);
        const consoleMethod = this.getConsoleMethod(record.level);

        if (this.formatter instanceof BrowserColoredFormatter) {
            const style = this.formatter.getConsoleStyle(record.level);
            if (record.args.length > 0) {
                consoleMethod(message, style, ...record.args);
            } else {
                consoleMethod(message, style);
            }
        } else {
            // Fallback for other formatters
            if (record.args.length > 0) {
                consoleMethod(message, ...record.args);
            } else {
                consoleMethod(message);
            }
        }
    }

    private getConsoleMethod(level: LogLevel): (...args: any[]) => void {
        switch (level) {
            case LogLevel.DEBUG:
                return console.debug;
            case LogLevel.INFO:
                return console.info;
            case LogLevel.WARNING:
                return console.warn;
            case LogLevel.ERROR:
            case LogLevel.CRITICAL:
                return console.error;
            default:
                return console.log;
        }
    }
}
