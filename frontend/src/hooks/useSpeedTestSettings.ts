import { useCallback } from 'react';
import { useSettings } from './useSettings';

interface UseSpeedTestSettingsReturn {
    // Speed test specific data
    enabled: boolean;
    setEnabled: (enabled: boolean) => Promise<void>;

    // Inherited from useSettings
    loading: boolean;
    error: string | null;
    refresh: () => Promise<void>;
}

export function useSpeedTestSettings(): UseSpeedTestSettingsReturn {
    const { settings, updateSetting, loading, error, refresh } = useSettings();

    const setEnabled = useCallback(async (enabled: boolean) => {
        try {
            await updateSetting('widgets', 'speedTest', { enabled });
        } catch (err) {
            console.error('Failed to update speed test setting:', err);
            throw err;
        }
    }, [updateSetting]);

    return {
        // Speed test specific data
        enabled: settings.widgets.speedTest.enabled,
        setEnabled,

        // Inherited from useSettings
        loading,
        error,
        refresh,
    };
}
