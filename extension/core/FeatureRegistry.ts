// Feature Registry for Homepage Companion Extension
// Manages all features following Open-Closed Principle

import { FeatureRegistry as FeatureRegistryInterface, Feature } from './types';

export class FeatureRegistry implements FeatureRegistryInterface {
    private features: Map<string, Feature> = new Map();

    register(feature: Feature): void {
        if (this.features.has(feature.name)) {
            console.warn(`Feature ${feature.name} is already registered. Overwriting...`);
        }

        this.features.set(feature.name, feature);
        console.log(`Feature ${feature.name} v${feature.version} registered successfully`);
    }

    unregister(featureName: string): void {
        const feature = this.features.get(featureName);
        if (feature) {
            feature.destroy().catch(error =>
                console.error(`Error destroying feature ${featureName}:`, error)
            );
            this.features.delete(featureName);
            console.log(`Feature ${featureName} unregistered successfully`);
        }
    }

    getFeature(featureName: string): Feature | undefined {
        return this.features.get(featureName);
    }

    getAllFeatures(): Feature[] {
        return Array.from(this.features.values());
    }

    async initializeAll(): Promise<void> {
        const initPromises = Array.from(this.features.values()).map(async (feature) => {
            try {
                await feature.initialize();
                console.log(`Feature ${feature.name} initialized successfully`);
            } catch (error) {
                console.error(`Failed to initialize feature ${feature.name}:`, error);
            }
        });

        await Promise.all(initPromises);
    }

    async destroyAll(): Promise<void> {
        const destroyPromises = Array.from(this.features.values()).map(async (feature) => {
            try {
                await feature.destroy();
                console.log(`Feature ${feature.name} destroyed successfully`);
            } catch (error) {
                console.error(`Failed to destroy feature ${feature.name}:`, error);
            }
        });

        await Promise.all(destroyPromises);
        this.features.clear();
    }

    // Get features by status
    getEnabledFeatures(): Feature[] {
        return this.getAllFeatures().filter(feature => feature.isEnabled());
    }

    getDisabledFeatures(): Feature[] {
        return this.getAllFeatures().filter(feature => !feature.isEnabled());
    }

    // Get feature count
    getFeatureCount(): number {
        return this.features.size;
    }
}
