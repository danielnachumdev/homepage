// Background script for Homepage Companion extension
// Using the new modular architecture with Open-Closed Principle

// Import all core components (inline to avoid ES6 import issues)
// Note: In a real implementation, these would be bundled together

// Extension Manager (inline implementation)
class ExtensionManager {
    private isInitialized: boolean = false;
    
    async initialize(): Promise<void> {
        if (this.isInitialized) {
            console.warn('Extension manager is already initialized');
            return;
        }
        
        try {
            console.log('Initializing Homepage Companion Extension...');
            
            // Initialize the new tab redirect feature
            const newTabRedirectFeature = new NewTabRedirectFeature();
            await newTabRedirectFeature.initialize();
            
            this.isInitialized = true;
            console.log('Extension manager initialized successfully');
            
        } catch (error) {
            console.error('Failed to initialize extension manager:', error);
            throw error;
        }
    }
}

// New Tab Redirect Feature (simplified inline version)
class NewTabRedirectFeature {
    private config = {
        enabled: true,
        homepageUrl: 'http://localhost:3000',
        redirectDelay: 100
    };
    
    async initialize(): Promise<void> {
        try {
            // Load configuration from storage
            const result = await chrome.storage.sync.get(['feature_newTabRedirect']);
            if (result.feature_newTabRedirect) {
                this.config = { ...this.config, ...result.feature_newTabRedirect };
            }
            
            this.setupEventListeners();
            console.log('New Tab Redirect feature initialized with config:', this.config);
        } catch (error) {
            console.error('Error initializing new tab redirect feature:', error);
            throw error;
        }
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
                }, this.config.redirectDelay);
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
            console.log(`Redirected tab ${tabId} to ${this.config.homepageUrl}`);
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
            await chrome.storage.sync.set({ feature_newTabRedirect: this.config });
        } catch (error) {
            console.error('Error saving new tab redirect config:', error);
        }
    }
}

// Initialize the extension
const extensionManager = new ExtensionManager();
extensionManager.initialize().catch(error => {
    console.error('Error initializing extension:', error);
});
