// New Tab Redirect Feature
// Implements the IFeature interface following Open-Closed Principle

import { BaseFeature } from '../core/Base';
import { FeatureConfig } from '../core/types';

export interface NewTabRedirectConfig extends FeatureConfig {
    enabled: boolean;
    homepageUrl: string;
    redirectDelay: number;
}

export class NewTabRedirectFeature extends BaseFeature {
    constructor(configManager: any) {
        const defaultConfig: NewTabRedirectConfig = {
            enabled: true,
            homepageUrl: 'http://localhost:3000',
            redirectDelay: 100
        };

        super('newTabRedirect', '1.0.0', defaultConfig, configManager);
    }

    protected async onInitialize(): Promise<void> {
        this.setupEventListeners();
        console.log('New Tab Redirect feature initialized');
    }

    protected async onDestroy(): Promise<void> {
        // Clean up event listeners if needed
        console.log('New Tab Redirect feature destroyed');
    }

    async onConfigUpdate(config: NewTabRedirectConfig): Promise<void> {
        console.log('New Tab Redirect config updated:', config);
        // Re-setup event listeners if needed
    }

    private setupEventListeners(): void {
        // Listen for tab updates to detect new tabs
        chrome.tabs.onUpdated.addListener(async (tabId, changeInfo, tab) => {
            if (changeInfo.status !== 'complete') return;

            if (this.isNewTabPage(tab.url) && this.isEnabled()) {
                await this.redirectTab(tabId);
            }
        });

        // Listen for tab creation to catch new tabs immediately
        chrome.tabs.onCreated.addListener(async (tab) => {
            if (this.isEnabled() && tab.url === 'chrome://newtab/') {
                setTimeout(async () => {
                    await this.redirectTab(tab.id!);
                }, this.getConfig().redirectDelay);
            }
        });
    }

    private isNewTabPage(url?: string): boolean {
        if (!url) return false;
        return [
            'chrome://newtab/',
            'chrome-search://local-ntp/local-ntp.html',
            'chrome://new-tab-page/',
            'chrome://new-tab-page-third-party/'
        ].includes(url);
    }

    private async redirectTab(tabId: number): Promise<void> {
        try {
            const config = this.getConfig() as NewTabRedirectConfig;
            await chrome.tabs.update(tabId, { url: config.homepageUrl });
            console.log(`Redirected tab ${tabId} to ${config.homepageUrl}`);
        } catch (error) {
            console.error('Error redirecting tab:', error);
        }
    }

    // Public methods for external access
    async setHomepageUrl(url: string): Promise<void> {
        await this.setConfig({ homepageUrl: url });
    }

    async setRedirectDelay(delay: number): Promise<void> {
        await this.setConfig({ redirectDelay: delay });
    }

    getHomepageUrl(): string {
        return (this.getConfig() as NewTabRedirectConfig).homepageUrl;
    }

    getRedirectDelay(): number {
        return (this.getConfig() as NewTabRedirectConfig).redirectDelay;
    }
}
