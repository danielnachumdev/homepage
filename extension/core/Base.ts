// Base Feature Class for Homepage Companion Extension
// Provides common functionality for all features

import { Feature, FeatureConfig } from './types';
import { ConfigManager } from './ConfigManager';

export abstract class BaseFeature implements Feature {
    public readonly name: string;
    public readonly version: string;
    public readonly defaultConfig: FeatureConfig;

    protected configManager: ConfigManager;
    protected currentConfig: FeatureConfig;

    constructor(
        name: string,
        version: string,
        defaultConfig: FeatureConfig,
        configManager: ConfigManager
    ) {
        this.name = name;
        this.version = version;
        this.defaultConfig = defaultConfig;
        this.configManager = configManager;
        this.currentConfig = { ...defaultConfig };
    }

    async initialize(): Promise<void> {
        try {
            // Load configuration
            this.currentConfig = await this.configManager.loadConfig(this.name);

            // Register default config if not already registered
            this.configManager.registerDefaultConfig(this.name, this.defaultConfig);

            // Initialize feature-specific logic
            await this.onInitialize();

            console.log(`Feature ${this.name} initialized with config:`, this.currentConfig);
        } catch (error) {
            console.error(`Failed to initialize feature ${this.name}:`, error);
            throw error;
        }
    }

    async destroy(): Promise<void> {
        try {
            await this.onDestroy();
            console.log(`Feature ${this.name} destroyed`);
        } catch (error) {
            console.error(`Failed to destroy feature ${this.name}:`, error);
            throw error;
        }
    }

    getConfig(): FeatureConfig {
        return { ...this.currentConfig };
    }

    async setConfig(config: Partial<FeatureConfig>): Promise<void> {
        const newConfig = { ...this.currentConfig, ...config };
        await this.configManager.saveConfig(this.name, newConfig);
        this.currentConfig = newConfig;

        // Notify feature of config update
        if (this.onConfigUpdate) {
            await this.onConfigUpdate(this.currentConfig);
        }
    }

    isEnabled(): boolean {
        return this.currentConfig.enabled;
    }

    async setEnabled(enabled: boolean): Promise<void> {
        await this.setConfig({ enabled });
    }

    // Abstract methods to be implemented by concrete features
    protected abstract onInitialize(): Promise<void>;
    protected abstract onDestroy(): Promise<void>;

    // Optional methods that can be overridden
    onConfigUpdate?(config: FeatureConfig): Promise<void>;
    onBackendConfigUpdate?(config: FeatureConfig): Promise<void>;
}
