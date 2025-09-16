// Extension Manager for Homepage Companion Extension
// Main orchestrator that manages all components

import { RequestManager } from './RequestManager';
import { ExtensionGateway } from '../gateways/ExtensionGateway';
import { ExtensionService } from '../services/ExtensionService';
import { ConfigManager } from './ConfigManager';
import { FeatureRegistry } from './FeatureRegistry';
import { NewTabRedirectFeature } from '../features/NewTabRedirect';

export class ExtensionManager {
    private requestManager: RequestManager;
    private extensionGateway: ExtensionGateway;
    private extensionService: ExtensionService;
    private configManager: ConfigManager;
    private featureRegistry: FeatureRegistry;
    private isInitialized: boolean = false;

    constructor(backendUrl: string = 'http://localhost:3000') {
        this.requestManager = new RequestManager(backendUrl);
        this.extensionGateway = new ExtensionGateway(this.requestManager);
        this.extensionService = new ExtensionService(this.extensionGateway);
        this.configManager = new ConfigManager(this.extensionService);
        this.featureRegistry = new FeatureRegistry();
    }

    async initialize(): Promise<void> {
        if (this.isInitialized) {
            console.warn('Extension manager is already initialized');
            return;
        }

        try {
            console.log('Initializing Homepage Companion Extension...');

            // Check backend availability using service
            const healthStatus = await this.extensionService.getExtensionHealthStatus();
            console.log(`Backend available: ${healthStatus.backendAvailable}`);

            // Register all features
            this.registerFeatures();

            // Initialize all features
            await this.featureRegistry.initializeAll();

            // Set up periodic backend sync
            this.setupBackendSync();

            this.isInitialized = true;
            console.log('Extension manager initialized successfully');

        } catch (error) {
            console.error('Failed to initialize extension manager:', error);
            throw error;
        }
    }

    private registerFeatures(): void {
        // Register New Tab Redirect Feature
        const newTabRedirectFeature = new NewTabRedirectFeature(this.configManager);
        this.featureRegistry.register(newTabRedirectFeature);

        // Add more features here as they are created
        // Example:
        // const quickActionsFeature = new QuickActionsFeature(this.configManager);
        // this.featureRegistry.register(quickActionsFeature);
    }

    private setupBackendSync(): void {
        // Sync with backend every 5 minutes
        setInterval(async () => {
            try {
                const backendConfig = await this.configManager.loadFromBackend();
                if (backendConfig) {
                    await this.updateFeaturesFromBackend(backendConfig);
                }
            } catch (error) {
                console.warn('Failed to sync with backend:', error);
            }
        }, 5 * 60 * 1000); // 5 minutes
    }

    private async updateFeaturesFromBackend(backendConfig: any): Promise<void> {
        for (const [featureName, config] of Object.entries(backendConfig.features)) {
            const feature = this.featureRegistry.getFeature(featureName);
            if (feature && feature.onBackendConfigUpdate) {
                await feature.onBackendConfigUpdate(config as any);
            }
        }
    }

    // Public API methods
    getFeature(featureName: string) {
        return this.featureRegistry.getFeature(featureName);
    }

    getAllFeatures() {
        return this.featureRegistry.getAllFeatures();
    }

    getEnabledFeatures() {
        return this.featureRegistry.getEnabledFeatures();
    }

    async destroy(): Promise<void> {
        if (!this.isInitialized) return;

        try {
            await this.featureRegistry.destroyAll();
            this.isInitialized = false;
            console.log('Extension manager destroyed');
        } catch (error) {
            console.error('Failed to destroy extension manager:', error);
        }
    }

    // Backend communication methods
    async isBackendAvailable(): Promise<boolean> {
        return this.extensionService.getExtensionHealthStatus().then(status => status.backendAvailable);
    }

    async getBackendConfig(): Promise<any> {
        return this.configManager.loadFromBackend();
    }
}
