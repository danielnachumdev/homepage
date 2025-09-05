// Unified settings interface for the entire application
export interface AppSettings {
    // Widget settings
    widgets: {
        speedTest: {
            enabled: boolean;
        };
    };

    // Search engine settings
    searchEngine: {
        selectedEngine: string;
    };

    // Chrome profile settings
    chromeProfiles: {
        profiles: Array<{
            profileId: string;
            displayName: string;
            icon: string;
            enabled: boolean;
        }>;
    };
}

// Default settings
export const DEFAULT_SETTINGS: AppSettings = {
    widgets: {
        speedTest: {
            enabled: false, // Default to disabled
        },
    },
    searchEngine: {
        selectedEngine: 'google',
    },
    chromeProfiles: {
        profiles: [],
    },
};

// Settings hook type
export interface UseSettingsReturn {
    settings: AppSettings;
    loading: boolean;
    error: string | null;
    updateSetting: <K extends keyof AppSettings>(
        category: K,
        key: keyof AppSettings[K],
        value: any
    ) => Promise<void>;
    refresh: () => Promise<void>;
}
