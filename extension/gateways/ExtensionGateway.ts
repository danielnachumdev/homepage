// Extension Gateway for Homepage Companion Extension
// Abstracts the backend API with domain-specific operations

import { RequestManager } from '../core/RequestManager';
import { BackendConfig, FeatureConfig } from '../core/types';

export class ExtensionGateway {
    private requestManager: RequestManager;

    constructor(requestManager: RequestManager) {
        this.requestManager = requestManager;
    }

    // Domain-specific operations that abstract the backend API

    // Get all feature configurations from backend
    async getFeatureConfigs(): Promise<BackendConfig | null> {
        try {
            return await this.requestManager.get<BackendConfig>('/api/extension/config');
        } catch (error) {
            console.warn('Failed to get feature configs from backend:', error);
            return null;
        }
    }

    // Get specific feature configuration
    async getFeatureConfig(featureName: string): Promise<FeatureConfig | null> {
        try {
            return await this.requestManager.get<FeatureConfig>(`/api/extension/config/${featureName}`);
        } catch (error) {
            console.warn(`Failed to get config for feature ${featureName}:`, error);
            return null;
        }
    }

    // Update specific feature configuration
    async updateFeatureConfig(featureName: string, config: FeatureConfig): Promise<boolean> {
        try {
            const response = await this.requestManager.put<{ success: boolean }>(
                `/api/extension/config/${featureName}`,
                config
            );
            return response?.success || false;
        } catch (error) {
            console.warn(`Failed to update config for feature ${featureName}:`, error);
            return false;
        }
    }

    // Sync all feature configurations
    async syncFeatureConfigs(configs: Record<string, FeatureConfig>): Promise<boolean> {
        try {
            const response = await this.requestManager.post<{ success: boolean }>(
                '/api/extension/config/sync',
                { features: configs }
            );
            return response?.success || false;
        } catch (error) {
            console.warn('Failed to sync feature configs:', error);
            return false;
        }
    }

    // Get extension status from backend
    async getExtensionStatus(): Promise<{ version: string; lastUpdated: string } | null> {
        try {
            return await this.requestManager.get<{ version: string; lastUpdated: string }>('/api/extension/status');
        } catch (error) {
            console.warn('Failed to get extension status:', error);
            return null;
        }
    }

    // Get backend health status
    async getBackendHealth(): Promise<{ status: string; timestamp: string } | null> {
        try {
            return await this.requestManager.get<{ status: string; timestamp: string }>('/api/health');
        } catch (error) {
            console.warn('Failed to get backend health:', error);
            return null;
        }
    }

    // Check if backend is available
    async isBackendAvailable(): Promise<boolean> {
        return this.requestManager.isBackendAvailable();
    }
}