# Homepage Companion Extension

A complementary Chrome extension for your homepage fullstack webapp that adds additional functionality and features.

## Current Features

### New Tab Redirect
- Automatically redirects new tabs to your homepage (http://localhost:3000)
- Toggleable via the extension popup
- Configurable homepage URL

## Architecture

The extension uses a simple, direct approach with inline feature definitions:

```
extension/
├── popup/                      # Extension popup UI
│   ├── popup.html             # Popup interface
│   └── popup.ts               # Popup functionality
├── background.ts               # Background script with inline features
├── manifest.json              # Extension manifest
└── scripts/                   # Content scripts (if needed)
```

## Adding New Features

To add a new feature:

1. **Add the feature class** directly in `background.ts`:
```typescript
class YourFeature {
    private config = {
        enabled: true,
        // Add your config properties
    };
    
    async initialize(): Promise<void> {
        // Load config from storage
        const result = await chrome.storage.sync.get(['yourFeature']);
        if (result.yourFeature) {
            this.config = { ...this.config, ...result.yourFeature };
        }
        
        // Set up event listeners
        this.setupEventListeners();
    }
    
    private setupEventListeners(): void {
        // Add your event listeners here
    }
    
    async setEnabled(enabled: boolean): Promise<void> {
        this.config.enabled = enabled;
        await this.saveConfig();
    }
    
    private async saveConfig(): Promise<void> {
        await chrome.storage.sync.set({ yourFeature: this.config });
    }
}

// Initialize the feature
const yourFeature = new YourFeature();
yourFeature.initialize();
```

2. **Add UI controls** in `popup/popup.html` and `popup/popup.ts` as needed.

3. **Update storage keys** to avoid conflicts between features.

## Development

```bash
# Install dependencies
npm install

# Compile TypeScript
npm run compile

# Build extension
npm run build
```

The built extension will be available in the `unpacked/` directory for testing.

## Future Feature Ideas

- **Quick Actions**: Add quick action buttons for common homepage tasks
- **Notifications**: Show notifications for important homepage events
- **Data Sync**: Sync data between the extension and homepage
- **Shortcuts**: Keyboard shortcuts for homepage functionality
- **Context Menu**: Right-click context menu integration
- **Tab Management**: Enhanced tab management features
- **Bookmarks**: Quick bookmark management
- **Notes**: Quick note-taking functionality
