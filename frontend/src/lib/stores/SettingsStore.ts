import { useState, useEffect, useCallback, useMemo } from 'react';
import { settingsService } from '../../services/settings.service';
import type { AppSettings, SettingsResponse } from '../../types/settings';
import { DEFAULT_SETTINGS, parseSettingsFromResponse } from '../../types/settings';
import { getLogger } from '../logger';

interface SettingsStoreState {
    settings: AppSettings;
    loading: boolean;
    error: string | null;
}

class SettingsStore {
    private static instance: SettingsStore;
    private state: SettingsStoreState = {
        settings: DEFAULT_SETTINGS,
        loading: true,
        error: null,
    };
    private listeners: Set<() => void> = new Set();
    private logger = getLogger('SettingsStore');
    private isInitialized = false;

    static getInstance(): SettingsStore {
        if (!SettingsStore.instance) {
            SettingsStore.instance = new SettingsStore();
        }
        return SettingsStore.instance;
    }

    getState(): SettingsStoreState {
        return this.state;
    }

    subscribe(listener: () => void): () => void {
        this.listeners.add(listener);
        return () => {
            this.listeners.delete(listener);
        };
    }

    private notify(): void {
        this.listeners.forEach(listener => listener());
    }

    private setState(newState: Partial<SettingsStoreState>): void {
        this.state = { ...this.state, ...newState };
        this.notify();
    }

    async loadSettings(): Promise<void> {
        if (this.isInitialized) {
            this.logger.debug('Settings already loaded, skipping');
            return;
        }

        // Check if loading is already in progress
        if (this.state.loading) {
            this.logger.debug('Settings loading already in progress, skipping');
            return;
        }

        this.logger.debug('Loading settings');
        this.logger.debug('isInitialized:', this.isInitialized);
        try {
            this.setState({ loading: true, error: null });

            this.logger.debug('Calling settingsService.getAllSettings');
            const response: SettingsResponse = await settingsService.getAllSettings();

            if (response.success) {
                this.logger.info('Settings loaded successfully');
                const parsedSettings = parseSettingsFromResponse(response.settings);
                this.setState({
                    settings: parsedSettings,
                    loading: false,
                    error: null,
                });
                this.isInitialized = true;
            } else {
                this.logger.error('Settings load failed', { message: response.message });
                throw new Error(response.message || 'Failed to load settings');
            }
        } catch (err) {
            this.logger.error('Failed to load settings', { error: err });
            this.setState({
                error: err instanceof Error ? err.message : 'Failed to load settings',
                loading: false,
            });
        }
    }

    async updateSetting<K extends keyof AppSettings>(
        category: K,
        key: keyof AppSettings[K],
        value: any
    ): Promise<void> {
        this.logger.debug('Updating setting', { category, key, value });
        try {
            this.setState({ error: null });

            // Update the setting based on category and key
            if (category === 'widgets' && key === 'speedTest') {
                const response = await settingsService.updateSpeedTestSetting(value.enabled);
                if (response.success) {
                    this.setState({
                        settings: {
                            ...this.state.settings,
                            widgets: {
                                ...this.state.settings.widgets,
                                speedTest: value,
                            },
                        },
                    });
                } else {
                    throw new Error(response.message);
                }
            } else if (category === 'searchEngine' && key === 'selectedEngine') {
                const response = await settingsService.updateSearchEngineSetting(value);
                if (response.success) {
                    this.setState({
                        settings: {
                            ...this.state.settings,
                            searchEngine: {
                                ...this.state.settings.searchEngine,
                                selectedEngine: value,
                            },
                        },
                    });
                } else {
                    throw new Error(response.message);
                }
            } else if (category === 'chromeProfiles' && key === 'profiles') {
                this.setState({
                    settings: {
                        ...this.state.settings,
                        chromeProfiles: {
                            ...this.state.settings.chromeProfiles,
                            profiles: value,
                        },
                    },
                });
            }
        } catch (err) {
            this.logger.error('Failed to update setting', { error: err, key, value });
            this.setState({ error: err instanceof Error ? err.message : 'Failed to update setting' });
            throw err;
        }
    }

    async refresh(): Promise<void> {
        this.isInitialized = false;
        await this.loadSettings();
    }
}

export const settingsStore = SettingsStore.getInstance();

// React hook for using the settings store
export function useSettingsStore() {
    const [state, setState] = useState(settingsStore.getState());
    const logger = getLogger('useSettingsStore');

    useEffect(() => {
        logger.debug('useSettingsStore hook initialized');
        const unsubscribe = settingsStore.subscribe(() => {
            logger.debug('Settings store state changed');
            setState(settingsStore.getState());
        });

        // Load settings if not already loaded
        const currentState = settingsStore.getState();
        logger.debug('Current store state:', { loading: currentState.loading, error: currentState.error, isInitialized: settingsStore['isInitialized'] });

        if (!settingsStore['isInitialized']) {
            logger.debug('Loading settings from hook');
            settingsStore.loadSettings();
        }

        return unsubscribe;
    }, []);

    const updateSetting = useCallback(
        async <K extends keyof AppSettings>(
            category: K,
            key: keyof AppSettings[K],
            value: any
        ) => {
            await settingsStore.updateSetting(category, key, value);
        },
        []
    );

    const refresh = useCallback(async () => {
        await settingsStore.refresh();
    }, []);

    return useMemo(
        () => ({
            settings: state.settings,
            loading: state.loading,
            error: state.error,
            updateSetting,
            refresh,
        }),
        [state.settings, state.loading, state.error, updateSetting, refresh]
    );
}
