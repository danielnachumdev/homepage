// Configuration Manager for Homepage Companion Extension
// Handles loading and saving of feature configurations with backend fallback

import { ConfigManager as ConfigManagerInterface, FeatureConfig, BackendConfig } from './types';
import { ExtensionService } from '../services/ExtensionService';

export class ConfigManager implements ConfigManagerInterface {
    private extensionService: ExtensionService;
    private defaultConfigs: Map<string, FeatureConfig> = new Map();

    constructor(extensionService: ExtensionService) {
        this.extensionService = extensionService;
    }

    // Register default configuration for a feature
    registerDefaultConfig(featureName: string, config: FeatureConfig): void {
        this.defaultConfigs.set(featureName, config);
    }

    async loadConfig(featureName: string): Promise<FeatureConfig> {
        try {
            // First try to load from Chrome storage
            const result = await chrome.storage.sync.get([`feature_${featureName}`]);
            const storedConfig = result[`feature_${featureName}`];

            if (storedConfig) {
                return this.mergeWithDefault(featureName, storedConfig);
            }

            // If no stored config, try to load from backend using service
            const { success, configs } = await this.extensionService.initializeExtension();
            if (success && configs[featureName]) {
                const config = configs[featureName];
                // Save to Chrome storage for offline access
                await this.saveConfig(featureName, config);
                return config;
            }

            // Fallback to default configuration
            return this.getDefaultConfig(featureName);

        } catch (error) {
            console.warn(`Failed to load config for feature ${featureName}:`, error);
            return this.getDefaultConfig(featureName);
        }
    }

    async saveConfig(featureName: string, config: FeatureConfig): Promise<void> {
        try {
            // Save to Chrome storage
            await chrome.storage.sync.set({
                [`feature_${featureName}`]: config
            });

            // Try to sync with backend using service (don't wait for it)
            this.extensionService.bulkUpdateFeatures([{ featureName, config }])
                .then(result => {
                    if (!result.success) {
                        console.warn(`Failed to sync config to backend for ${featureName}`);
                    }
                })
                .catch(error => console.warn(`Failed to sync config to backend for ${featureName}:`, error));

        } catch (error) {
            console.error(`Failed to save config for feature ${featureName}:`, error);
            throw error;
        }
    }

    async loadFromBackend(): Promise<BackendConfig | null> {
        try {
            const { success, configs } = await this.extensionService.initializeExtension();
            if (success) {
                return {
                    features: configs,
                    version: '1.0.0',
                    lastUpdated: new Date().toISOString()
                };
            }
            return null;
        } catch (error) {
            console.warn('Failed to load configs from backend:', error);
            return null;
        }
    }

    getDefaultConfig(featureName: string): FeatureConfig {
        const defaultConfig = this.defaultConfigs.get(featureName);
        if (!defaultConfig) {
            throw new Error(`No default configuration found for feature: ${featureName}`);
        }
        return { ...defaultConfig };
    }

    private mergeWithDefault(featureName: string, config: FeatureConfig): FeatureConfig {
        const defaultConfig = this.getDefaultConfig(featureName);
        return {
            ...defaultConfig,
            ...config
        };
    }

    // Get all registered feature names
    getRegisteredFeatures(): string[] {
        return Array.from(this.defaultConfigs.keys());
    }
}
