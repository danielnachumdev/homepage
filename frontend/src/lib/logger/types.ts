/**
 * Logging levels similar to Python's logging module
 */
export const LogLevel = {
    DEBUG: 0,
    INFO: 1,
    WARNING: 2,
    ERROR: 3,
    CRITICAL: 4,
    NOTSET: -1,
} as const;

export type LogLevel = typeof LogLevel[keyof typeof LogLevel];

/**
 * Log record structure
 */
export interface LogRecord {
    name: string;
    level: LogLevel;
    levelName: string;
    message: string;
    timestamp: Date;
    module?: string;
    function?: string;
    line?: number;
    args: any[];
    extra: Record<string, any>;
}

/**
 * Formatter interface for customizing log output
 */
export interface Formatter {
    format(record: LogRecord): string;
}

/**
 * Handler interface for processing log records
 */
export interface Handler {
    level: LogLevel;
    formatter?: Formatter;
    emit(record: LogRecord): void;
    handle(record: LogRecord): void;
    flush?(): void;
    close?(): void;
}

/**
 * Logger configuration
 */
export interface LoggerConfig {
    name: string;
    level: LogLevel;
    handlers: Handler[];
    propagate: boolean;
    filters?: Filter[];
}

/**
 * Filter interface for log filtering
 */
export interface Filter {
    filter(record: LogRecord): boolean;
}

/**
 * Logger interface
 */
export interface Logger {
    name: string;
    level: LogLevel;
    handlers: Handler[];
    propagate: boolean;
    filters: Filter[];
    parent?: Logger;
    children: Map<string, Logger>;

    debug(message: string, ...args: any[]): void;
    info(message: string, ...args: any[]): void;
    warning(message: string, ...args: any[]): void;
    error(message: string, ...args: any[]): void;
    critical(message: string, ...args: any[]): void;
    log(level: LogLevel, message: string, ...args: any[]): void;

    addHandler(handler: Handler): void;
    removeHandler(handler: Handler): void;
    setLevel(level: LogLevel): void;
    addFilter(filter: Filter): void;
    removeFilter(filter: Filter): void;
    isEnabledFor(level: LogLevel): boolean;
}

/**
 * Logger manager interface
 */
export interface LoggerManager {
    getLogger(name?: string): Logger;
    setLevel(level: LogLevel): void;
    addHandler(handler: Handler): void;
    removeHandler(handler: Handler): void;
    shutdown(): void;
}
