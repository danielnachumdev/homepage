import { useState, useEffect, useCallback, useRef } from 'react';
import { api } from '../lib/api';
import { useAppSettings } from '../contexts/SettingsContext';

export interface SpeedTestPartialResult {
    download_speed_mbps?: number;
    upload_speed_mbps?: number;
    ping_ms?: number;
    timestamp?: string;
    server_name?: string;
    server_sponsor?: string;
    is_download_complete?: boolean;
    is_upload_complete?: boolean;
    is_ping_complete?: boolean;
}

export interface SpeedTestState {
    result: SpeedTestPartialResult | null;
    isLoading: boolean;
    isRunning: boolean;
    error: string | null;
    loadingMessage: string;
    isDownloadLoading: boolean;
    isUploadLoading: boolean;
    isPingLoading: boolean;
}

export interface UseSpeedTestOptions {
    intervalSeconds?: number;
    autoStart?: boolean;
}

export interface UseSpeedTestReturn extends SpeedTestState {
    // Speed test actions
    performSpeedTest: () => Promise<void>;
    startContinuousTesting: () => Promise<void>;
    stopContinuousTesting: () => Promise<void>;
    toggleTesting: () => void;
    getLatestResult: () => Promise<void>;

    // Speed test settings
    enabled: boolean;
    setEnabled: (enabled: boolean) => Promise<void>;

    // Inherited from useSettings
    loading: boolean;
    error: string | null;
    refresh: () => Promise<void>;
}

export const useSpeedTest = (options: UseSpeedTestOptions = {}): UseSpeedTestReturn => {
    const { intervalSeconds = 1, autoStart = true } = options;

    // Get settings from useSettings hook
    const { settings, updateSetting, loading, error: settingsError, refresh } = useAppSettings();

    const [state, setState] = useState<SpeedTestState>({
        result: null,
        isLoading: false,
        isRunning: false,
        error: null,
        loadingMessage: '',
        isDownloadLoading: false,
        isUploadLoading: false,
        isPingLoading: false,
    });

    const intervalRef = useRef<number | null>(null);
    const isInitializedRef = useRef(false);

    const updateState = useCallback((updates: Partial<SpeedTestState>) => {
        setState(prev => ({ ...prev, ...updates }));
    }, []);

    const setEnabled = useCallback(async (enabled: boolean) => {
        try {
            await updateSetting('widgets', 'speedTest', { enabled });
        } catch (err) {
            console.error('Failed to update speed test setting:', err);
            throw err;
        }
    }, [updateSetting]);

    const performSpeedTest = useCallback(async () => {
        try {
            updateState({
                isLoading: true,
                error: null,
                loadingMessage: 'Internet speed test',
                isDownloadLoading: true,
                isUploadLoading: true,
                isPingLoading: true,
            });

            const response = await api.post('/api/v1/speedtest/test', {
                interval_seconds: intervalSeconds
            });

            if (response.data.success && response.data.result) {
                const result = response.data.result;
                updateState({
                    result,
                    isDownloadLoading: !result.is_download_complete,
                    isUploadLoading: !result.is_upload_complete,
                    isPingLoading: !result.is_ping_complete,
                });
            } else {
                throw new Error(response.data.message || 'Speed test failed');
            }
        } catch (err: any) {
            const errorMessage = err?.message || 'Unknown error occurred';
            updateState({
                error: errorMessage,
                isDownloadLoading: false,
                isUploadLoading: false,
                isPingLoading: false,
            });
            console.error('Speed test error:', err);
        } finally {
            updateState({
                isLoading: false,
                loadingMessage: '',
            });
        }
    }, [intervalSeconds, updateState]);

    const startContinuousTesting = useCallback(async () => {
        try {
            updateState({
                error: null,
                loadingMessage: 'Starting speed test',
            });

            const response = await api.post('/api/v1/speedtest/start', {
                interval_seconds: intervalSeconds
            });

            if (response.data.success) {
                updateState({ isRunning: true });
            } else {
                throw new Error(response.data.message || 'Failed to start continuous testing');
            }
        } catch (err: any) {
            const errorMessage = err?.message || 'Unknown error occurred';
            updateState({ error: errorMessage });
            console.error('Start continuous testing error:', err);
        } finally {
            updateState({ loadingMessage: '' });
        }
    }, [intervalSeconds, updateState]);

    const stopContinuousTesting = useCallback(async () => {
        try {
            updateState({
                error: null,
                loadingMessage: 'Stopping speed test',
            });

            const response = await api.post('/api/v1/speedtest/stop');

            if (response.data.success) {
                updateState({ isRunning: false });
            } else {
                throw new Error(response.data.message || 'Failed to stop continuous testing');
            }
        } catch (err: any) {
            const errorMessage = err?.message || 'Unknown error occurred';
            updateState({ error: errorMessage });
            console.error('Stop continuous testing error:', err);
        } finally {
            updateState({ loadingMessage: '' });
        }
    }, [updateState]);

    const getLatestResult = useCallback(async () => {
        try {
            const response = await api.get('/api/v1/speedtest/partial-result');

            if (response.data.success && response.data.result) {
                const result = response.data.result;
                updateState({
                    result,
                    isDownloadLoading: !result.is_download_complete,
                    isUploadLoading: !result.is_upload_complete,
                    isPingLoading: !result.is_ping_complete,
                });
            }
        } catch (err) {
            console.error('Get latest result error:', err);
        }
    }, [updateState]);

    const checkStatus = useCallback(async () => {
        try {
            const response = await api.get('/api/v1/speedtest/status');
            const data = response.data;

            updateState({ isRunning: data.is_running });

            if (data.has_result) {
                await getLatestResult();
            }

            // Auto-start if enabled and not already running
            if (autoStart && !data.is_running && !state.result && !isInitializedRef.current) {
                await startContinuousTesting();
                isInitializedRef.current = true;
            }
        } catch (err) {
            console.error('Status check error:', err);
            // If auto-start is enabled and we get an error, try to start anyway
            if (autoStart && !state.result && !isInitializedRef.current) {
                await startContinuousTesting();
                isInitializedRef.current = true;
            }
        }
    }, [autoStart, state.result, getLatestResult, startContinuousTesting, updateState]);

    const toggleTesting = useCallback(() => {
        if (state.isRunning) {
            stopContinuousTesting();
        } else {
            startContinuousTesting();
        }
    }, [state.isRunning, startContinuousTesting, stopContinuousTesting]);

    // Initialize on mount
    useEffect(() => {
        checkStatus();
    }, [checkStatus]);

    // Set up polling for latest results when continuous testing is running
    useEffect(() => {
        if (!state.isRunning) {
            if (intervalRef.current) {
                clearInterval(intervalRef.current);
                intervalRef.current = null;
            }
            return;
        }

        intervalRef.current = window.setInterval(() => {
            getLatestResult();
        }, intervalSeconds * 1000);

        return () => {
            if (intervalRef.current) {
                window.clearInterval(intervalRef.current);
                intervalRef.current = null;
            }
        };
    }, [state.isRunning, intervalSeconds, getLatestResult]);

    // Cleanup on unmount
    useEffect(() => {
        return () => {
            if (intervalRef.current) {
                window.clearInterval(intervalRef.current);
            }
        };
    }, []);

    return {
        ...state,
        // Speed test actions
        performSpeedTest,
        startContinuousTesting,
        stopContinuousTesting,
        toggleTesting,
        getLatestResult,

        // Speed test settings
        enabled: settings.widgets.speedTest.enabled,
        setEnabled,

        // Inherited from useSettings
        loading,
        error: state.error || settingsError,
        refresh,
    };
};
