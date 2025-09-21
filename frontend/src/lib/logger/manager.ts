import type { Logger, LoggerManager, Handler } from './types';
import { LogLevel } from './types';
import { LoggerImpl } from './logger';

/**
 * Logger manager implementation
 */
export class LoggerManagerImpl implements LoggerManager {
    private loggers: Map<string, Logger> = new Map();
    private rootLogger: Logger;
    private defaultLevel: LogLevel = LogLevel.WARNING;
    private defaultHandlers: Handler[] = [];

    constructor() {
        // Create root logger
        this.rootLogger = new LoggerImpl({
            name: 'root',
            level: this.defaultLevel,
            handlers: [...this.defaultHandlers],
            propagate: false,
        });
        this.loggers.set('root', this.rootLogger);
    }

    getLogger(name: string = 'root'): Logger {
        if (this.loggers.has(name)) {
            return this.loggers.get(name)!;
        }

        // Create new logger
        const logger = new LoggerImpl({
            name,
            level: this.defaultLevel,
            handlers: [...this.defaultHandlers],
            propagate: true,
        });

        // Set parent logger
        const parentName = this.getParentName(name);
        if (parentName && this.loggers.has(parentName)) {
            logger.parent = this.loggers.get(parentName);
        } else {
            logger.parent = this.rootLogger;
        }

        this.loggers.set(name, logger);
        return logger;
    }

    setLevel(level: LogLevel): void {
        this.defaultLevel = level;
        this.rootLogger.setLevel(level);

        // Update all existing loggers
        for (const logger of this.loggers.values()) {
            if (logger !== this.rootLogger) {
                logger.setLevel(level);
            }
        }
    }

    addHandler(handler: Handler): void {
        this.defaultHandlers.push(handler);
        this.rootLogger.addHandler(handler);

        // Add to all existing loggers
        for (const logger of this.loggers.values()) {
            if (logger !== this.rootLogger) {
                logger.addHandler(handler);
            }
        }
    }

    removeHandler(handler: Handler): void {
        const index = this.defaultHandlers.indexOf(handler);
        if (index > -1) {
            this.defaultHandlers.splice(index, 1);
        }

        this.rootLogger.removeHandler(handler);

        // Remove from all existing loggers
        for (const logger of this.loggers.values()) {
            if (logger !== this.rootLogger) {
                logger.removeHandler(handler);
            }
        }
    }

    shutdown(): void {
        // Close all handlers
        for (const logger of this.loggers.values()) {
            for (const handler of logger.handlers) {
                if (handler.close) {
                    try {
                        handler.close();
                    } catch (error) {
                        console.error('Error closing handler:', error);
                    }
                }
            }
        }

        // Clear all loggers
        this.loggers.clear();
        this.defaultHandlers = [];
    }

    private getParentName(name: string): string | null {
        const parts = name.split('.');
        if (parts.length <= 1) {
            return 'root';
        }
        return parts.slice(0, -1).join('.');
    }
}
