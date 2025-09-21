import { useState, useEffect, useCallback, useMemo } from 'react';
import { api } from '../lib/api';
import { useComponentLogger } from './useLogger';

interface BackendStatus {
    isConnected: boolean;
    lastChecked: Date | null;
    error: string | null;
}

export const useBackendStatus = (checkInterval: number = 5000) => {
    const logger = useComponentLogger('useBackendStatus');

    const [status, setStatus] = useState<BackendStatus>({
        isConnected: false,
        lastChecked: null,
        error: null
    });

    // Memoize the check function to prevent recreation on every render
    const checkBackendStatus = useCallback(async () => {
        logger.debug('Performing backend health check', { interval: checkInterval });
        try {
            // Use the new API instance to check backend health
            await api.get('/health');
            logger.info('Backend health check successful - service is available');

            setStatus(prevStatus => {
                // Only update if status actually changed
                if (prevStatus.isConnected && !prevStatus.error) {
                    return prevStatus; // No change needed
                }
                logger.info('Backend status changed: connected', {
                    wasConnected: prevStatus.isConnected,
                    hadError: !!prevStatus.error
                });
                return {
                    isConnected: true,
                    lastChecked: new Date(),
                    error: null
                };
            });
        } catch (error: any) {
            logger.error('Backend health check failed - service unavailable', {
                error: error.message,
                statusCode: error.response?.status,
                url: error.config?.url
            });
            setStatus(prevStatus => {
                // Only update if status actually changed
                const newError = error.message || 'Unknown error';
                if (!prevStatus.isConnected && prevStatus.error === newError) {
                    return prevStatus; // No change needed
                }
                logger.warning('Backend status changed: disconnected', {
                    wasConnected: prevStatus.isConnected,
                    newError: newError
                });
                return {
                    isConnected: false,
                    lastChecked: new Date(),
                    error: newError
                };
            });
        }
    }, [logger, checkInterval]);

    useEffect(() => {
        // Check immediately on mount
        logger.debug('Initializing backend status monitoring', { checkInterval });
        checkBackendStatus();

        // Set up interval for periodic checks
        logger.debug('Setting up periodic health checks', {
            interval: checkInterval,
            intervalMs: checkInterval
        });
        const intervalId = setInterval(checkBackendStatus, checkInterval);

        // Cleanup interval on unmount
        return () => {
            logger.debug('Cleaning up backend status monitoring', { intervalId });
            clearInterval(intervalId);
        };
    }, [checkInterval, checkBackendStatus, logger]);

    // Memoize the return value to prevent unnecessary re-renders
    return useMemo(() => {
        logger.debug('Providing backend status to consumers', {
            isConnected: status.isConnected,
            hasError: !!status.error,
            lastChecked: status.lastChecked?.toISOString()
        });
        return status;
    }, [status, logger]);
};
