import { useCallback } from 'react';
import { useSettings } from '../contexts/SettingsContext';

interface UseSpeedTestSettingsReturn {
    enabled: boolean;
    setEnabled: (enabled: boolean) => Promise<void>;
    loading: boolean;
    error: string | null;
}

export function useSpeedTestSettings(): UseSpeedTestSettingsReturn {
    const { settings, updateSetting, loading, error } = useSettings();

    const setEnabled = useCallback(async (enabled: boolean) => {
        try {
            await updateSetting('widgets', 'speedTest', { enabled });
        } catch (err) {
            console.error('Failed to update speed test setting:', err);
            throw err;
        }
    }, [updateSetting]);

    return {
        enabled: settings.widgets.speedTest.enabled,
        setEnabled,
        loading,
        error,
    };
}
