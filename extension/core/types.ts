// Core types for the Homepage Companion Extension
// Following Open-Closed Principle for maximum extensibility

export interface FeatureConfig {
    enabled: boolean;
    [key: string]: any; // Allow any additional configuration properties
}

export interface BackendConfig {
    features: Record<string, FeatureConfig>;
    version: string;
    lastUpdated: string;
}

export interface RequestManagerConfig {
    baseUrl: string;
    timeout: number;
    retryAttempts: number;
}

// Core Feature Interface - Open-Closed Principle
export interface Feature {
    readonly name: string;
    readonly version: string;
    readonly defaultConfig: FeatureConfig;
    
    // Lifecycle methods
    initialize(): Promise<void>;
    destroy(): Promise<void>;
    
    // Configuration methods
    getConfig(): FeatureConfig;
    setConfig(config: Partial<FeatureConfig>): Promise<void>;
    isEnabled(): boolean;
    setEnabled(enabled: boolean): Promise<void>;
    
    // Feature-specific methods (to be implemented by each feature)
    onConfigUpdate?(config: FeatureConfig): Promise<void>;
    onBackendConfigUpdate?(config: FeatureConfig): Promise<void>;
}

// Feature Registry Interface
export interface FeatureRegistry {
    register(feature: Feature): void;
    unregister(featureName: string): void;
    getFeature(featureName: string): Feature | undefined;
    getAllFeatures(): Feature[];
    initializeAll(): Promise<void>;
    destroyAll(): Promise<void>;
}

// Extension Gateway Interface
export interface ExtensionGateway {
    getFeatureConfigs(): Promise<BackendConfig | null>;
    updateFeatureConfig(featureName: string, config: FeatureConfig): Promise<boolean>;
    syncFeatureConfigs(configs: Record<string, FeatureConfig>): Promise<boolean>;
    getExtensionStatus(): Promise<{ version: string; lastUpdated: string } | null>;
    isBackendAvailable(): Promise<boolean>;
    getBackendHealth(): Promise<{ status: string; timestamp: string } | null>;
}

// Configuration Manager Interface
export interface ConfigManager {
    loadConfig(featureName: string): Promise<FeatureConfig>;
    saveConfig(featureName: string, config: FeatureConfig): Promise<void>;
    loadFromBackend(): Promise<BackendConfig | null>;
    getDefaultConfig(featureName: string): FeatureConfig;
}
