import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { settingsService } from '../services/settings.service';
import type { AppSettings, SettingsContextType } from '../types/settings';
import { DEFAULT_SETTINGS } from '../types/settings';

const SettingsContext = createContext<SettingsContextType | undefined>(undefined);

interface SettingsProviderProps {
    children: React.ReactNode;
}

export const SettingsProvider: React.FC<SettingsProviderProps> = ({ children }) => {
    const [settings, setSettings] = useState<AppSettings>(DEFAULT_SETTINGS);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    const loadSettings = useCallback(async () => {
        try {
            setLoading(true);
            setError(null);

            // Load all settings in parallel
            const [
                speedTestResponse,
                searchEngineResponse,
                chromeProfilesResponse,
            ] = await Promise.all([
                settingsService.getSpeedTestSetting(),
                settingsService.getSearchEngineSetting(),
                settingsService.getChromeProfileSettings(),
            ]);

            const newSettings: AppSettings = {
                widgets: {
                    speedTest: {
                        enabled: speedTestResponse.success ? speedTestResponse.setting.enabled : false,
                    },
                },
                searchEngine: {
                    selectedEngine: searchEngineResponse.success ? searchEngineResponse.setting.selected_engine : 'google',
                },
                chromeProfiles: {
                    profiles: chromeProfilesResponse.success ? chromeProfilesResponse.profiles : [],
                },
            };

            setSettings(newSettings);
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

    const refreshSettings = useCallback(async () => {
        await loadSettings();
    }, [loadSettings]);

    // Load settings on mount
    useEffect(() => {
        loadSettings();
    }, [loadSettings]);

    const value: SettingsContextType = {
        settings,
        loading,
        error,
        updateSetting,
        refreshSettings,
    };

    return (
        <SettingsContext.Provider value={value}>
            {children}
        </SettingsContext.Provider>
    );
};

export const useSettings = (): SettingsContextType => {
    const context = useContext(SettingsContext);
    if (context === undefined) {
        throw new Error('useSettings must be used within a SettingsProvider');
    }
    return context;
};
