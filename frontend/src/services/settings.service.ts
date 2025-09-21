import { api } from '../lib/api';
import type { SettingsResponse, SettingUpdateRequest, SettingUpdateResponse, BulkSettingsUpdateRequest, BulkSettingsUpdateResponse } from '../types/settings';
import { getLogger } from '../lib/logger';

class SettingsService {
    private logger = getLogger('SettingsService');

    async getAllSettings(): Promise<SettingsResponse> {
        this.logger.debug('Getting all settings');
        try {
            const response = await api.get<SettingsResponse>('/api/v1/settings/');
            this.logger.info('Settings retrieved successfully');
            return response.data;
        } catch (error) {
            this.logger.error('Failed to get all settings', { error });
            throw error;
        }
    }

    async updateSetting(request: SettingUpdateRequest): Promise<SettingUpdateResponse> {
        try {
            const response = await api.put<SettingUpdateResponse>('/api/v1/settings/update', request);
            return response.data;
        } catch (error) {
            this.logger.error('Failed to update setting', { error, request });
            throw error;
        }
    }

    async bulkUpdateSettings(request: BulkSettingsUpdateRequest): Promise<BulkSettingsUpdateResponse> {
        try {
            const response = await api.put<BulkSettingsUpdateResponse>('/api/v1/settings/bulk-update', request);
            return response.data;
        } catch (error) {
            this.logger.error('Failed to bulk update settings', { error, request });
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
            this.logger.error('Failed to update speed test setting', { error, enabled });
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
            this.logger.error('Failed to update search engine setting', { error, selectedEngine });
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
            this.logger.error('Failed to update Chrome profile setting', { error, profileId, updates });
            throw error;
        }
    }
}

export const settingsService = new SettingsService();