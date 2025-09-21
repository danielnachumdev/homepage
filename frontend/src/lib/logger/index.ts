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
import { BrowserConsoleHandler } from './handlers';
import { BrowserColoredFormatter } from './formatters';
import { LogLevel } from './types';

// Create default logger manager
const loggerManager = new LoggerManagerImpl();

// Set the default level to DEBUG so all messages are processed
loggerManager.setLevel(LogLevel.DEBUG);

// Configure logging: debug level to console with colors
const consoleHandler = new BrowserConsoleHandler(LogLevel.DEBUG, new BrowserColoredFormatter());
loggerManager.addHandler(consoleHandler);

// Export the default logger manager and a convenience function
export const logger = loggerManager.getLogger('app');
export const getLogger = (name?: string) => loggerManager.getLogger(name);
export const setLogLevel = (level: LogLevel) => loggerManager.setLevel(level);
export const addHandler = (handler: any) => loggerManager.addHandler(handler);
export const removeHandler = (handler: any) => loggerManager.removeHandler(handler);
export const shutdown = () => loggerManager.shutdown();

// Export the manager instance for advanced usage
export { loggerManager };
