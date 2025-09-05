import { useState, useEffect, useCallback } from 'react';
import { settingsService } from '../services/settings.service';
import type { AppSettings, UseSettingsReturn, SettingsResponse } from '../types/settings';
import { DEFAULT_SETTINGS, parseSettingsFromResponse } from '../types/settings';

export function useSettings(): UseSettingsReturn {
    const [settings, setSettings] = useState<AppSettings>(DEFAULT_SETTINGS);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    const loadSettings = useCallback(async () => {
        try {
            setLoading(true);
            setError(null);

            // Load all settings in a single request
            const response: SettingsResponse = await settingsService.getAllSettings();

            if (response.success) {
                // Parse the generic settings response into our structured format
                const parsedSettings = parseSettingsFromResponse(response.settings);
                setSettings(parsedSettings);
            } else {
                throw new Error(response.message || 'Failed to load settings');
            }
        } catch (err) {
            console.error('Failed to load settings:', err);
            setError(err instanceof Error ? err.message : 'Failed to load settings');
            // Keep default settings on error
        } finally {
            setLoading(false);
        }
    }, []);

    const updateSetting = useCallback(async <K extends keyof AppSettings>(
        category: K,
        key: keyof AppSettings[K],
        value: any
    ) => {
        try {
            setError(null);

            // Update the setting based on category and key
            if (category === 'widgets' && key === 'speedTest') {
                const response = await settingsService.updateSpeedTestSetting(value.enabled);
                if (response.success) {
                    setSettings(prev => ({
                        ...prev,
                        widgets: {
                            ...prev.widgets,
                            speedTest: value,
                        },
                    }));
                } else {
                    throw new Error(response.message);
                }
            } else if (category === 'searchEngine' && key === 'selectedEngine') {
                const response = await settingsService.updateSearchEngineSetting(value);
                if (response.success) {
                    setSettings(prev => ({
                        ...prev,
                        searchEngine: {
                            ...prev.searchEngine,
                            selectedEngine: value,
                        },
                    }));
                } else {
                    throw new Error(response.message);
                }
            } else if (category === 'chromeProfiles' && key === 'profiles') {
                // For Chrome profiles, we need to update each profile individually
                // This is more complex and might need to be handled differently
                setSettings(prev => ({
                    ...prev,
                    chromeProfiles: {
                        ...prev.chromeProfiles,
                        profiles: value,
                    },
                }));
            }
        } catch (err) {
            console.error('Failed to update setting:', err);
            setError(err instanceof Error ? err.message : 'Failed to update setting');
            throw err;
        }
    }, []);

    const refresh = useCallback(async () => {
        await loadSettings();
    }, [loadSettings]);

    // Load settings on mount
    useEffect(() => {
        loadSettings();
    }, [loadSettings]);

    return {
        settings,
        loading,
        error,
        updateSetting,
        refresh,
    };
}