# Homepage Companion Extension

A complementary Chrome extension for your homepage fullstack webapp that adds additional functionality and features.

## Current Features

### New Tab Redirect
- Automatically redirects new tabs to your homepage (http://localhost:3000)
- Toggleable via the extension popup
- Configurable homepage URL

## Architecture

The extension follows the Open-Closed Principle with a modular, extensible architecture:

```
extension/
├── core/                       # Core framework components (reusable across project)
│   ├── types.ts               # Type definitions and interfaces
│   ├── Base.ts                # Base feature class
│   ├── FeatureRegistry.ts     # Feature management
│   ├── ConfigManager.ts       # Configuration management
│   ├── RequestManager.ts      # Generic HTTP client
│   └── ExtensionManager.ts    # Main orchestrator
├── gateways/                   # Low-level API abstractions
│   └── ExtensionGateway.ts    # Backend API operations (get, post, put, delete)
├── services/                   # Complex business operations
│   └── ExtensionService.ts    # Business logic using gateway operations
├── features/                   # Individual feature implementations
│   └── NewTabRedirect.ts
├── popup/                      # Extension popup UI (functional only)
│   ├── popup.html             # Popup interface
│   └── popup.ts               # Popup functionality
├── background.ts               # Background script
├── manifest.json              # Extension manifest
└── scripts/                   # Content scripts (if needed)
```

## Adding New Features

To add a new feature following the Open-Closed Principle:

1. **Create a new feature file** in `features/YourFeature.ts`:
```typescript
import { BaseFeature } from '../core/Base';
import { FeatureConfig } from '../core/types';

export interface YourFeatureConfig extends FeatureConfig {
    enabled: boolean;
    customSetting: string;
    // Add your specific config properties
}

export class YourFeature extends BaseFeature {
    constructor(configManager: ConfigManager) {
        const defaultConfig: YourFeatureConfig = {
            enabled: true,
            customSetting: 'default-value'
        };
        
        super('yourFeature', '1.0.0', defaultConfig, configManager);
    }
    
    protected async onInitialize(): Promise<void> {
        // Initialize your feature logic
        this.setupEventListeners();
    }
    
    protected async onDestroy(): Promise<void> {
        // Clean up resources
    }
    
    private setupEventListeners(): void {
        // Add your event listeners here
    }
}
```

2. **Register the feature** in `core/ExtensionManager.ts`:
```typescript
// In the registerFeatures() method
const yourFeature = new YourFeature(this.configManager);
this.featureRegistry.register(yourFeature);
```

3. **Configuration is handled automatically** - no need to manage storage or backend sync manually.

## Key Benefits

- **Open-Closed Principle**: Easy to add new features without modifying existing code
- **Gateway/Service Pattern**: Clean separation between low-level API operations and complex business logic
- **Backend Integration**: Automatic configuration sync with your homepage backend
- **Fallback Support**: Default configurations when backend is unavailable
- **Centralized Management**: All features managed through the registry
- **Type Safety**: Full TypeScript support with proper interfaces
- **Highly Decoupled**: Gateway abstracts 3rd-party API, Service creates business operations

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
