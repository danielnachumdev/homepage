import { useState, useEffect } from 'react';
import { api } from '../lib/api';

interface BackendStatus {
    isConnected: boolean;
    lastChecked: Date | null;
    error: string | null;
}

export const useBackendStatus = (checkInterval: number = 5000) => {
    console.log(`[PERF] useBackendStatus: Hook initialized with interval ${checkInterval}ms at ${new Date().toISOString()}`);

    const [status, setStatus] = useState<BackendStatus>({
        isConnected: false,
        lastChecked: null,
        error: null
    });

    useEffect(() => {
        const checkBackendStatus = async () => {
            console.log(`[PERF] useBackendStatus: Checking backend status at ${new Date().toISOString()}`);
            try {
                // Use the new API instance to check backend health
                await api.get('/health');
                console.log(`[PERF] useBackendStatus: Backend is connected at ${new Date().toISOString()}`);

                setStatus({
                    isConnected: true,
                    lastChecked: new Date(),
                    error: null
                });
            } catch (error: any) {
                console.log(`[PERF] useBackendStatus: Backend connection failed at ${new Date().toISOString()}:`, error.message);
                setStatus({
                    isConnected: false,
                    lastChecked: new Date(),
                    error: error.message || 'Unknown error'
                });
            }
        };

        // Check immediately on mount
        console.log(`[PERF] useBackendStatus: Starting initial check at ${new Date().toISOString()}`);
        checkBackendStatus();

        // Set up interval for periodic checks
        console.log(`[PERF] useBackendStatus: Setting up interval check every ${checkInterval}ms at ${new Date().toISOString()}`);
        const intervalId = setInterval(checkBackendStatus, checkInterval);

        // Cleanup interval on unmount
        return () => {
            console.log(`[PERF] useBackendStatus: Cleaning up interval at ${new Date().toISOString()}`);
            clearInterval(intervalId);
        };
    }, [checkInterval]);

    console.log(`[PERF] useBackendStatus: Returning status - connected: ${status.isConnected}, error: ${status.error ? 'Yes' : 'No'} at ${new Date().toISOString()}`);
    return status;
};
