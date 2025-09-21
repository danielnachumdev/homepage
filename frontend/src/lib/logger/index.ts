// Types
export * from './types';

// Core classes
export { LoggerImpl } from './logger';
export { LoggerManagerImpl } from './manager';

// Formatters
export * from './formatters';

// Handlers
export * from './handlers';

// Filters
export * from './filters';

// Default logger instance
import { LoggerManagerImpl } from './manager';
import { ConsoleHandler, LocalStorageHandler } from './handlers';
import { StandardFormatter, ColoredFormatter, JSONFormatter } from './formatters';
import { LogLevel } from './types';

// Create default logger manager
const loggerManager = new LoggerManagerImpl();

// Add default console handler for development
if (import.meta.env.DEV) {
    const consoleHandler = new ConsoleHandler(LogLevel.DEBUG, new ColoredFormatter());
    loggerManager.addHandler(consoleHandler);
} else {
    const consoleHandler = new ConsoleHandler(LogLevel.INFO, new StandardFormatter());
    loggerManager.addHandler(consoleHandler);
}

// Add local storage handler for persistent logging
const localStorageHandler = new LocalStorageHandler('app_logs', LogLevel.INFO, 1000, new JSONFormatter());
loggerManager.addHandler(localStorageHandler);

// Export the default logger manager and a convenience function
export const logger = loggerManager.getLogger('app');
export const getLogger = (name?: string) => loggerManager.getLogger(name);
export const setLogLevel = (level: LogLevel) => loggerManager.setLevel(level);
export const addHandler = (handler: any) => loggerManager.addHandler(handler);
export const removeHandler = (handler: any) => loggerManager.removeHandler(handler);
export const shutdown = () => loggerManager.shutdown();

// Export the manager instance for advanced usage
export { loggerManager };
