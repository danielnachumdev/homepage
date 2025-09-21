import { useState, useEffect, useCallback } from 'react';
import { settingsService } from '../services/settings.service';
import type { AppSettings, UseSettingsReturn, SettingsResponse } from '../types/settings';
import { DEFAULT_SETTINGS, parseSettingsFromResponse } from '../types/settings';
import { useComponentLogger } from './useLogger';

export function useSettings(): UseSettingsReturn {
    const logger = useComponentLogger('useSettings');
    logger.debug('Hook initialized');

    const [settings, setSettings] = useState<AppSettings>(DEFAULT_SETTINGS);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    const loadSettings = useCallback(async () => {
        logger.debug('Loading settings');
        try {
            setLoading(true);
            setError(null);

            // Load all settings in a single request
            logger.debug('Calling settingsService.getAllSettings');
            const response: SettingsResponse = await settingsService.getAllSettings();

            if (response.success) {
                logger.info('Settings loaded successfully');
                // Parse the generic settings response into our structured format
                const parsedSettings = parseSettingsFromResponse(response.settings);
                setSettings(parsedSettings);
            } else {
                logger.error('Settings load failed', { message: response.message });
                throw new Error(response.message || 'Failed to load settings');
            }
        } catch (err) {
            logger.error('Failed to load settings', { error: err });
            setError(err instanceof Error ? err.message : 'Failed to load settings');
            // Keep default settings on error
        } finally {
            logger.debug('Settings loading completed');
            setLoading(false);
        }
    }, []); // Empty dependency array - this function doesn't depend on any props or state

    const updateSetting = useCallback(async <K extends keyof AppSettings>(
        category: K,
        key: keyof AppSettings[K],
        value: any
    ) => {
        logger.debug('Updating setting', { category, key, value });
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
            logger.error('Failed to update setting', { error: err, key, value });
            setError(err instanceof Error ? err.message : 'Failed to update setting');
            throw err;
        }
    }, []);

    const refresh = useCallback(async () => {
        await loadSettings();
    }, [loadSettings]);

    // Load settings on mount
    useEffect(() => {
        logger.debug('useEffect triggered - loading settings');
        loadSettings();
    }, [loadSettings]);

    logger.debug('Returning hook state', { loading, hasError: !!error });

    return {
        settings,
        loading,
        error,
        updateSetting,
        refresh,
    };
}