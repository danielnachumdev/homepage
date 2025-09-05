// Backend response types
export interface SettingValue {
    id: string;
    category: string;
    setting_type: string;
    value: any;
    description?: string;
    is_user_editable: boolean;
    created_at?: string;
    updated_at?: string;
}

export interface SettingsResponse {
    success: boolean;
    message?: string;
    settings: SettingValue[];
}

export interface SettingUpdateRequest {
    id: string;
    value: any;
}

export interface SettingUpdateResponse {
    success: boolean;
    message: string;
    setting?: SettingValue;
}

export interface BulkSettingsUpdateRequest {
    settings: SettingUpdateRequest[];
}

export interface BulkSettingsUpdateResponse {
    success: boolean;
    updated_settings: SettingValue[];
    failed_updates: Array<Record<string, any>>;
    message?: string;
}

// Parsed settings interface for the frontend
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
            enabled: false,
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

// Utility function to parse settings from backend response
export function parseSettingsFromResponse(settings: SettingValue[]): AppSettings {
    const parsed: AppSettings = {
        widgets: {
            speedTest: {
                enabled: false,
            },
        },
        searchEngine: {
            selectedEngine: 'google',
        },
        chromeProfiles: {
            profiles: [],
        },
    };

    // Parse each setting based on its ID and category
    for (const setting of settings) {
        switch (setting.id) {
            case 'speed_test_enabled':
                if (setting.value && typeof setting.value === 'object' && 'enabled' in setting.value) {
                    parsed.widgets.speedTest.enabled = setting.value.enabled;
                } else {
                    parsed.widgets.speedTest.enabled = Boolean(setting.value);
                }
                break;

            case 'search_engine_preference':
                if (setting.value && typeof setting.value === 'object' && 'selected_engine' in setting.value) {
                    parsed.searchEngine.selectedEngine = setting.value.selected_engine;
                } else {
                    parsed.searchEngine.selectedEngine = String(setting.value || 'google');
                }
                break;

            default:
                // Handle Chrome profile settings
                if (setting.id.startsWith('chrome_profile_') && setting.category === 'chrome_profiles') {
                    if (setting.value && typeof setting.value === 'object') {
                        parsed.chromeProfiles.profiles.push({
                            profileId: setting.value.profile_id || setting.id.replace('chrome_profile_', ''),
                            displayName: setting.value.display_name || 'Unknown Profile',
                            icon: setting.value.icon || 'default',
                            enabled: Boolean(setting.value.enabled),
                        });
                    }
                }
                break;
        }
    }

    return parsed;
}