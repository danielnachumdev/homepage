import type { Handler } from './types';
import { LogLevel } from './types';
import { ConsoleHandler, FileHandler, LocalStorageHandler, RemoteHandler } from './handlers';
import { StandardFormatter, ColoredFormatter, JSONFormatter } from './formatters';

/**
 * Logger configuration presets
 */
export const LoggerConfigs = {
    /**
     * Development configuration with colored console output
     */
    development: {
        level: LogLevel.DEBUG,
        handlers: [
            new ConsoleHandler(LogLevel.DEBUG, new ColoredFormatter()),
            new LocalStorageHandler('dev_logs', LogLevel.DEBUG, 500, new JSONFormatter()),
        ],
    },

    /**
     * Production configuration with minimal console output and remote logging
     */
    production: {
        level: LogLevel.INFO,
        handlers: [
            new ConsoleHandler(LogLevel.WARNING, new StandardFormatter()),
            new LocalStorageHandler('prod_logs', LogLevel.INFO, 1000, new JSONFormatter()),
        ],
    },

    /**
     * Testing configuration with file output
     */
    testing: {
        level: LogLevel.DEBUG,
        handlers: [
            new ConsoleHandler(LogLevel.DEBUG, new StandardFormatter()),
            new FileHandler('test.log', LogLevel.DEBUG, 100, new StandardFormatter()),
        ],
    },

    /**
     * Debug configuration with maximum verbosity
     */
    debug: {
        level: LogLevel.DEBUG,
        handlers: [
            new ConsoleHandler(LogLevel.DEBUG, new ColoredFormatter()),
            new LocalStorageHandler('debug_logs', LogLevel.DEBUG, 2000, new JSONFormatter()),
            new FileHandler('debug.log', LogLevel.DEBUG, 500, new JSONFormatter()),
        ],
    },
};

/**
 * Create a custom logger configuration
 */
export function createLoggerConfig(options: {
    level?: LogLevel;
    console?: boolean;
    localStorage?: boolean;
    file?: boolean;
    remote?: string;
    formatter?: 'standard' | 'colored' | 'json';
    maxEntries?: number;
}): { level: LogLevel; handlers: Handler[] } {
    const {
        level = LogLevel.INFO,
        console: enableConsole = true,
        localStorage: enableLocalStorage = true,
        file: enableFile = false,
        remote: remoteEndpoint,
        formatter = 'standard',
        maxEntries = 1000,
    } = options;

    const handlers: Handler[] = [];
    let formatterInstance;

    switch (formatter) {
        case 'colored':
            formatterInstance = new ColoredFormatter();
            break;
        case 'json':
            formatterInstance = new JSONFormatter();
            break;
        default:
            formatterInstance = new StandardFormatter();
    }

    if (enableConsole) {
        handlers.push(new ConsoleHandler(level, formatterInstance));
    }

    if (enableLocalStorage) {
        handlers.push(new LocalStorageHandler('app_logs', level, maxEntries, new JSONFormatter()));
    }

    if (enableFile) {
        handlers.push(new FileHandler('app.log', level, maxEntries, formatterInstance));
    }

    if (remoteEndpoint) {
        handlers.push(new RemoteHandler(remoteEndpoint, level, 10, 5000, new JSONFormatter()));
    }

    return { level, handlers };
}

/**
 * Environment-based logger configuration
 */
export function getEnvironmentConfig(): { level: LogLevel; handlers: Handler[] } {
    const env = process.env.NODE_ENV || 'development';

    switch (env) {
        case 'production':
            return LoggerConfigs.production;
        case 'test':
            return LoggerConfigs.testing;
        case 'development':
        default:
            return LoggerConfigs.development;
    }
}
