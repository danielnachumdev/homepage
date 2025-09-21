import { useMemo } from 'react';
import type { Logger } from '../lib/logger';
import { LogLevel } from '../lib/logger';

/**
 * React hook for using logger in components
 * @param name - Logger name (defaults to component name or 'component')
 * @returns Logger instance
 */
export function useLogger(name?: string): Logger {
    return useMemo(() => {
        const { getLogger } = require('../lib/logger');
        return getLogger(name);
    }, [name]);
}

/**
 * Hook for getting a logger with a specific level
 * @param name - Logger name
 * @param level - Log level
 * @returns Logger instance with set level
 */
export function useLoggerWithLevel(name: string, level: LogLevel): Logger {
    return useMemo(() => {
        const { getLogger } = require('../lib/logger');
        const logger = getLogger(name);
        logger.setLevel(level);
        return logger;
    }, [name, level]);
}

/**
 * Hook for component-specific logging with automatic naming
 * @param componentName - Name of the component
 * @returns Logger instance
 */
export function useComponentLogger(componentName: string): Logger {
    return useLogger(`component.${componentName}`);
}
