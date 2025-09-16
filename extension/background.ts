// Background script for Homepage Companion extension
// Note: We'll define the feature manager inline to avoid ES6 import issues in service workers

// New Tab Redirect Feature (inline to avoid import issues)
class NewTabRedirectFeature {
    private config = {
        enabled: true,
        homepageUrl: 'http://localhost:3000'
    };

    async initialize(): Promise<void> {
        try {
            const result = await chrome.storage.sync.get(['newTabRedirect']);
            if (result.newTabRedirect) {
                this.config = { ...this.config, ...result.newTabRedirect };
            }
        } catch (error) {
            console.error('Error loading new tab redirect config:', error);
        }

        this.setupEventListeners();
    }

    private setupEventListeners(): void {
        // Listen for tab updates to detect new tabs
        chrome.tabs.onUpdated.addListener(async (tabId, changeInfo, tab) => {
            if (changeInfo.status !== 'complete') return;

            if (this.isNewTabPage(tab.url) && this.config.enabled) {
                await this.redirectTab(tabId);
            }
        });

        // Listen for tab creation to catch new tabs immediately
        chrome.tabs.onCreated.addListener(async (tab) => {
            if (this.config.enabled && tab.url === 'chrome://newtab/') {
                setTimeout(async () => {
                    await this.redirectTab(tab.id!);
                }, 100);
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
            await chrome.tabs.update(tabId, { url: this.config.homepageUrl });
        } catch (error) {
            console.error('Error redirecting tab:', error);
        }
    }

    async setEnabled(enabled: boolean): Promise<void> {
        this.config.enabled = enabled;
        await this.saveConfig();
    }

    async setHomepageUrl(url: string): Promise<void> {
        this.config.homepageUrl = url;
        await this.saveConfig();
    }

    getConfig() {
        return { ...this.config };
    }

    private async saveConfig(): Promise<void> {
        try {
            await chrome.storage.sync.set({ newTabRedirect: this.config });
        } catch (error) {
            console.error('Error saving new tab redirect config:', error);
        }
    }
}

// Initialize the new tab redirect feature
const newTabRedirectFeature = new NewTabRedirectFeature();
newTabRedirectFeature.initialize().catch(error => {
    console.error('Error initializing new tab redirect feature:', error);
});
