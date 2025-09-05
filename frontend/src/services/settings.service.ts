import { api } from '../lib/api';
import type { SettingsResponse, SettingUpdateRequest, SettingUpdateResponse, BulkSettingsUpdateRequest, BulkSettingsUpdateResponse } from '../types/settings';

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

    async updateSetting(request: SettingUpdateRequest): Promise<SettingUpdateResponse> {
        try {
            const response = await api.put<SettingUpdateResponse>('/api/v1/settings/update', request);
            return response.data;
        } catch (error) {
            console.error('Failed to update setting:', error);
            throw error;
        }
    }

    async bulkUpdateSettings(request: BulkSettingsUpdateRequest): Promise<BulkSettingsUpdateResponse> {
        try {
            const response = await api.put<BulkSettingsUpdateResponse>('/api/v1/settings/bulk-update', request);
            return response.data;
        } catch (error) {
            console.error('Failed to bulk update settings:', error);
            throw error;
        }
    }

    // Convenience methods for specific setting types
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
}

export const settingsService = new SettingsService();