import { api } from '../lib/api';

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
    settings: SettingValue[];
    message?: string;
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

export interface ChromeProfileSettingValue {
    profile_id: string;
    display_name: string;
    icon: string;
    enabled: boolean;
}

export interface ChromeProfileSettingsResponse {
    success: boolean;
    profiles: ChromeProfileSettingValue[];
    message?: string;
}

export interface SearchEngineSettingValue {
    selected_engine: string;
}

export interface SearchEngineSettingsResponse {
    success: boolean;
    setting: SearchEngineSettingValue;
    message?: string;
}

export interface SpeedTestSettingValue {
    enabled: boolean;
}

export interface SpeedTestSettingsResponse {
    success: boolean;
    setting: SpeedTestSettingValue;
    message?: string;
}

class SettingsService {
    async getAllSettings(): Promise<SettingsResponse> {
        try {
            const response = await api.get<SettingsResponse>('/api/v1/settings/');
            return response.data;
        } catch (error) {
            console.error('Failed to get all settings:', error);
            throw error;
        }
    }

    async getSettingsByCategory(category: string): Promise<SettingsResponse> {
        try {
            const response = await api.get<SettingsResponse>(`/api/v1/settings/category/${category}`);
            return response.data;
        } catch (error) {
            console.error(`Failed to get settings for category ${category}:`, error);
            throw error;
        }
    }

    async updateSetting(request: SettingUpdateRequest): Promise<SettingUpdateResponse> {
        try {
            const response = await api.put<SettingUpdateResponse>('/api/v1/settings/update', request);
            return response.data;
        } catch (error) {
            console.error('Failed to update setting:', error);
            throw error;
        }
    }

    async getChromeProfileSettings(): Promise<ChromeProfileSettingsResponse> {
        try {
            const response = await api.get<ChromeProfileSettingsResponse>('/api/v1/settings/chrome-profiles');
            return response.data;
        } catch (error) {
            console.error('Failed to get Chrome profile settings:', error);
            throw error;
        }
    }

    async updateChromeProfileSetting(
        profileId: string,
        displayName: string,
        icon: string,
        enabled: boolean
    ): Promise<SettingUpdateResponse> {
        try {
            const response = await api.put<SettingUpdateResponse>(
                `/api/v1/settings/chrome-profiles/${profileId}?display_name=${encodeURIComponent(displayName)}&icon=${encodeURIComponent(icon)}&enabled=${enabled}`,
                null
            );
            return response.data;
        } catch (error) {
            console.error('Failed to update Chrome profile setting:', error);
            throw error;
        }
    }

    async getSearchEngineSetting(): Promise<SearchEngineSettingsResponse> {
        try {
            const response = await api.get<SearchEngineSettingsResponse>('/api/v1/settings/search-engine');
            return response.data;
        } catch (error) {
            console.error('Failed to get search engine setting:', error);
            throw error;
        }
    }

    async updateSearchEngineSetting(selectedEngine: string): Promise<SettingUpdateResponse> {
        try {
            const response = await api.put<SettingUpdateResponse>(
                `/api/v1/settings/search-engine?selected_engine=${encodeURIComponent(selectedEngine)}`,
                null
            );
            return response.data;
        } catch (error) {
            console.error('Failed to update search engine setting:', error);
            throw error;
        }
    }

    async getSpeedTestSetting(): Promise<SpeedTestSettingsResponse> {
        try {
            const response = await api.get<SpeedTestSettingsResponse>('/api/v1/settings/speed-test');
            return response.data;
        } catch (error) {
            console.error('Failed to get speed test setting:', error);
            throw error;
        }
    }

    async updateSpeedTestSetting(enabled: boolean): Promise<SettingUpdateResponse> {
        try {
            const response = await api.put<SettingUpdateResponse>(
                `/api/v1/settings/speed-test?enabled=${enabled}`,
                null
            );
            return response.data;
        } catch (error) {
            console.error('Failed to update speed test setting:', error);
            throw error;
        }
    }
}

export const settingsService = new SettingsService();
