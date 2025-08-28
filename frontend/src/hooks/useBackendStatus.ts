import { useState, useEffect } from 'react';
import { API_CONFIG, buildApiUrl } from '../config/api';

interface BackendStatus {
    isConnected: boolean;
    lastChecked: Date | null;
    error: string | null;
}

export const useBackendStatus = (checkInterval: number = API_CONFIG.HEALTH_CHECK_INTERVAL) => {
    const [status, setStatus] = useState<BackendStatus>({
        isConnected: false,
        lastChecked: null,
        error: null
    });

    useEffect(() => {
        const checkBackendStatus = async () => {
            try {
                // Try to connect to the backend using the configured endpoint
                const response = await fetch(buildApiUrl(API_CONFIG.HEALTH_CHECK), {
                    method: 'GET',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    // Add a timeout to prevent hanging requests
                    signal: AbortSignal.timeout(API_CONFIG.REQUEST_TIMEOUT)
                });

                if (response.ok) {
                    setStatus({
                        isConnected: true,
                        lastChecked: new Date(),
                        error: null
                    });
                } else {
                    setStatus({
                        isConnected: false,
                        lastChecked: new Date(),
                        error: `HTTP ${response.status}: ${response.statusText}`
                    });
                }
            } catch (error) {
                setStatus({
                    isConnected: false,
                    lastChecked: new Date(),
                    error: error instanceof Error ? error.message : 'Unknown error'
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
