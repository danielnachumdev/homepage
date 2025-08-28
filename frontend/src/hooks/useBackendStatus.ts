import { useState, useEffect } from 'react';
import { api } from '../lib/api';

interface BackendStatus {
    isConnected: boolean;
    lastChecked: Date | null;
    error: string | null;
}

export const useBackendStatus = (checkInterval: number = 5000) => {
    const [status, setStatus] = useState<BackendStatus>({
        isConnected: false,
        lastChecked: null,
        error: null
    });

    useEffect(() => {
        const checkBackendStatus = async () => {
            try {
                // Use the new API instance to check backend health
                const response = await api.get('/health');

                setStatus({
                    isConnected: true,
                    lastChecked: new Date(),
                    error: null
                });
            } catch (error: any) {
                setStatus({
                    isConnected: false,
                    lastChecked: new Date(),
                    error: error.message || 'Unknown error'
                });
            }
        };

        // Check immediately on mount
        checkBackendStatus();

        // Set up interval for periodic checks
        const intervalId = setInterval(checkBackendStatus, checkInterval);

        // Cleanup interval on unmount
        return () => clearInterval(intervalId);
    }, [checkInterval]);

    return status;
};
