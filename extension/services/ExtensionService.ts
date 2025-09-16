// Extension Service for Homepage Companion Extension
// Complex business operations using ExtensionGateway

import { ExtensionGateway } from '../gateways/ExtensionGateway';
import { BackendConfig, FeatureConfig } from '../core/types';

export class ExtensionService {
    private gateway: ExtensionGateway;

    constructor(gateway: ExtensionGateway) {
        this.gateway = gateway;
    }

    // Complex business operations

    // Initialize extension with full configuration sync
    async initializeExtension(): Promise<{ success: boolean; configs: Record<string, FeatureConfig> }> {
        try {
            // Check if backend is available
            const isBackendAvailable = await this.gateway.isBackendAvailable();

            if (!isBackendAvailable) {
                console.warn('Backend not available, using local defaults');
                return { success: false, configs: {} };
            }

            // Get all feature configurations from backend
            const backendConfig = await this.gateway.getFeatureConfigs();

            if (!backendConfig || !backendConfig.features) {
                console.warn('No feature configs received from backend');
                return { success: false, configs: {} };
            }

            return { success: true, configs: backendConfig.features };
        } catch (error) {
            console.error('Failed to initialize extension:', error);
            return { success: false, configs: {} };
        }
    }

    // Subscribe to feature updates (complex operation)
    async subscribeToFeatureUpdates(featureName: string, callback: (config: FeatureConfig) => void): Promise<boolean> {
        try {
            // This would typically set up WebSocket or polling
            // For now, we'll just validate the feature exists
            const config = await this.gateway.getFeatureConfig(featureName);

            if (!config) {
                console.warn(`Feature ${featureName} not found on backend`);
                return false;
            }

            // In a real implementation, this would set up the subscription
            console.log(`Subscribed to updates for feature: ${featureName}`);
            return true;
        } catch (error) {
            console.error(`Failed to subscribe to feature updates for ${featureName}:`, error);
            return false;
        }
    }

    // Register new feature with backend (complex operation)
    async registerFeature(featureName: string, defaultConfig: FeatureConfig): Promise<boolean> {
        try {
            // First check if feature already exists
            const existingConfig = await this.gateway.getFeatureConfig(featureName);

            if (existingConfig) {
                console.log(`Feature ${featureName} already exists, updating instead`);
                return await this.gateway.updateFeatureConfig(featureName, defaultConfig);
            }

            // Register new feature
            const success = await this.gateway.updateFeatureConfig(featureName, defaultConfig);

            if (success) {
                console.log(`Successfully registered feature: ${featureName}`);
            }

            return success;
        } catch (error) {
            console.error(`Failed to register feature ${featureName}:`, error);
            return false;
        }
    }

    // Sync all local configurations with backend (complex operation)
    async syncAllConfigurations(localConfigs: Record<string, FeatureConfig>): Promise<{ success: boolean; syncedCount: number }> {
        try {
            // Check backend availability
            const isBackendAvailable = await this.gateway.isBackendAvailable();

            if (!isBackendAvailable) {
                console.warn('Backend not available, cannot sync configurations');
                return { success: false, syncedCount: 0 };
            }

            // Sync all configurations at once
            const success = await this.gateway.syncFeatureConfigs(localConfigs);

            if (success) {
                const syncedCount = Object.keys(localConfigs).length;
                console.log(`Successfully synced ${syncedCount} configurations with backend`);
                return { success: true, syncedCount };
            }

            return { success: false, syncedCount: 0 };
        } catch (error) {
            console.error('Failed to sync all configurations:', error);
            return { success: false, syncedCount: 0 };
        }
    }

    // Get extension health status (complex operation)
    async getExtensionHealthStatus(): Promise<{
        backendAvailable: boolean;
        backendHealth: { status: string; timestamp: string } | null;
        extensionStatus: { version: string; lastUpdated: string } | null;
    }> {
        try {
            // Check multiple health indicators in parallel
            const [backendAvailable, backendHealth, extensionStatus] = await Promise.all([
                this.gateway.isBackendAvailable(),
                this.gateway.getBackendHealth(),
                this.gateway.getExtensionStatus()
            ]);

            return {
                backendAvailable,
                backendHealth,
                extensionStatus
            };
        } catch (error) {
            console.error('Failed to get extension health status:', error);
            return {
                backendAvailable: false,
                backendHealth: null,
                extensionStatus: null
            };
        }
    }

    // Bulk update multiple features (complex operation)
    async bulkUpdateFeatures(updates: Array<{ featureName: string; config: FeatureConfig }>): Promise<{
        success: boolean;
        results: Array<{ featureName: string; success: boolean }>
    }> {
        try {
            const results: Array<{ featureName: string; success: boolean }> = [];

            // Update each feature individually
            for (const update of updates) {
                const success = await this.gateway.updateFeatureConfig(update.featureName, update.config);
                results.push({ featureName: update.featureName, success });
            }

            const allSuccessful = results.every(result => result.success);

            return {
                success: allSuccessful,
                results
            };
        } catch (error) {
            console.error('Failed to bulk update features:', error);
            return {
                success: false,
                results: []
            };
        }
    }
}
