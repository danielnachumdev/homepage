import type { LogRecord, Handler, Formatter } from '../types';
import { LogLevel } from '../types';
import { BaseHandler } from './BaseHandler';

/**
 * Console handler for browser console output
 */
export class ConsoleHandler extends BaseHandler {
    constructor(level: LogLevel = LogLevel.DEBUG, formatter?: Formatter) {
        super(level, formatter);
    }

    emit(record: LogRecord): void {
        const message = this.format(record);
        const consoleMethod = this.getConsoleMethod(record.level);

        if (record.args.length > 0) {
            consoleMethod(message, ...record.args);
        } else {
            consoleMethod(message);
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
