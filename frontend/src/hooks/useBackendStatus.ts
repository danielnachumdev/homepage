import { useState, useEffect } from 'react';
import { api } from '../lib/api';
import { useComponentLogger } from './useLogger';

interface BackendStatus {
    isConnected: boolean;
    lastChecked: Date | null;
    error: string | null;
}

export const useBackendStatus = (checkInterval: number = 5000) => {
    const logger = useComponentLogger('useBackendStatus');

    logger.debug('Hook initialized', { checkInterval });

    const [status, setStatus] = useState<BackendStatus>({
        isConnected: false,
        lastChecked: null,
        error: null
    });

    useEffect(() => {
        const checkBackendStatus = async () => {
            logger.debug('Checking backend status');
            try {
                // Use the new API instance to check backend health
                await api.get('/health');
                logger.info('Backend is connected');

                setStatus({
                    isConnected: true,
                    lastChecked: new Date(),
                    error: null
                });
            } catch (error: any) {
                logger.error('Backend connection failed', {
                    error: error.message,
                    stack: error.stack
                });
                setStatus({
                    isConnected: false,
                    lastChecked: new Date(),
                    error: error.message || 'Unknown error'
                });
            }
        };

        // Check immediately on mount
        logger.debug('Starting initial check');
        checkBackendStatus();

        // Set up interval for periodic checks
        logger.debug('Setting up interval check', { checkInterval });
        const intervalId = setInterval(checkBackendStatus, checkInterval);

        // Cleanup interval on unmount
        return () => {
            logger.debug('Cleaning up interval');
            clearInterval(intervalId);
        };
    }, [checkInterval, logger]);

    logger.debug('Returning status', {
        isConnected: status.isConnected,
        hasError: !!status.error
    });
    return status;
};
