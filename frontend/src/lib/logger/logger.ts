import type { LogRecord, Logger, Handler, Filter, LoggerConfig } from './types';
import { LogLevel } from './types';

/**
 * Logger implementation similar to Python's logging module
 */
export class LoggerImpl implements Logger {
    name: string;
    level: LogLevel;
    handlers: Handler[];
    propagate: boolean;
    filters: Filter[];
    parent?: Logger;
    children: Map<string, Logger>;

    constructor(config: LoggerConfig) {
        this.name = config.name;
        this.level = config.level;
        this.handlers = [...config.handlers];
        this.propagate = config.propagate;
        this.filters = config.filters || [];
        this.children = new Map();
    }

    debug(message: string, ...args: any[]): void {
        this.log(LogLevel.DEBUG, message, ...args);
    }

    info(message: string, ...args: any[]): void {
        this.log(LogLevel.INFO, message, ...args);
    }

    warning(message: string, ...args: any[]): void {
        this.log(LogLevel.WARNING, message, ...args);
    }

    error(message: string, ...args: any[]): void {
        this.log(LogLevel.ERROR, message, ...args);
    }

    critical(message: string, ...args: any[]): void {
        this.log(LogLevel.CRITICAL, message, ...args);
    }

    log(level: LogLevel, message: string, ...args: any[]): void {
        const record = this.createLogRecord(level, message, args);

        if (this.shouldLog(record)) {
            this.callHandlers(record);
        }
    }

    addHandler(handler: Handler): void {
        this.handlers.push(handler);
    }

    removeHandler(handler: Handler): void {
        const index = this.handlers.indexOf(handler);
        if (index > -1) {
            this.handlers.splice(index, 1);
        }
    }

    setLevel(level: LogLevel): void {
        this.level = level;
    }

    addFilter(filter: Filter): void {
        this.filters.push(filter);
    }

    removeFilter(filter: Filter): void {
        const index = this.filters.indexOf(filter);
        if (index > -1) {
            this.filters.splice(index, 1);
        }
    }

    isEnabledFor(level: LogLevel): boolean {
        return level >= this.level;
    }

    private createLogRecord(level: LogLevel, message: string, args: any[]): LogRecord {
        const now = new Date();
        const levelName = this.getLevelName(level);

        // Try to get caller information
        const callerInfo = this.getCallerInfo();

        return {
            name: this.name,
            level,
            levelName,
            message,
            timestamp: now,
            module: callerInfo.module,
            function: callerInfo.function,
            line: callerInfo.line,
            args,
            extra: {},
        };
    }

    private getLevelName(level: LogLevel): string {
        switch (level) {
            case LogLevel.DEBUG:
                return 'DEBUG';
            case LogLevel.INFO:
                return 'INFO';
            case LogLevel.WARNING:
                return 'WARNING';
            case LogLevel.ERROR:
                return 'ERROR';
            case LogLevel.CRITICAL:
                return 'CRITICAL';
            default:
                return 'UNKNOWN';
        }
    }

    private getCallerInfo(): { module?: string; function?: string; line?: number } {
        try {
            const stack = new Error().stack;
            if (!stack) {
                return {};
            }

            const lines = stack.split('\n');
            // Skip the first few lines (Error, getCallerInfo, createLogRecord, log)
            const callerLine = lines[4];
            if (!callerLine) {
                return {};
            }

            // Parse stack trace line (format varies by browser)
            const match = callerLine.match(/at\s+(.+?)\s+\((.+?):(\d+):(\d+)\)/) ||
                callerLine.match(/at\s+(.+?):(\d+):(\d+)/);

            if (match) {
                const [, functionName, file, line] = match;
                const module = file ? file.split('/').pop()?.split('?')[0] : undefined;
                return {
                    module,
                    function: functionName,
                    line: parseInt(line, 10),
                };
            }
        } catch (error) {
            // Ignore errors in stack trace parsing
        }

        return {};
    }

    private shouldLog(record: LogRecord): boolean {
        // Check if the record level is enabled for this logger
        if (!this.isEnabledFor(record.level)) {
            return false;
        }

        // Check filters
        for (const filter of this.filters) {
            if (!filter.filter(record)) {
                return false;
            }
        }

        return true;
    }

    private callHandlers(record: LogRecord): void {
        // Call handlers for this logger
        for (const handler of this.handlers) {
            try {
                handler.handle(record);
            } catch (error) {
                console.error('Error in log handler:', error);
            }
        }

        // Propagate to parent if enabled
        if (this.propagate && this.parent) {
            this.parent.log(record.level, record.message, ...record.args);
        }
    }
}
