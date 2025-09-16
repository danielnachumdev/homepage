import { useState, useEffect } from 'react';
import { RequestManager } from '../lib/RequestManager';

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
        const requestManager = new RequestManager('http://localhost:8000');

        const checkBackendStatus = async () => {
            try {
                // Use the RequestManager to check backend health
                await requestManager.get<{ status: string }>('/health');

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
