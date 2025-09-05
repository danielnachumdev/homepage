import { ChromeProfilesSettings } from './ChromeProfilesSettings';
import { SearchEngineSettings } from './SearchEngineSettings';
import { WidgetsSettings } from './WidgetsSettings';
import type { SettingsCategoryComponent } from './types';

// Registry of all setting categories
export const settingsRegistry: SettingsCategoryComponent[] = [
    {
        id: 'widgets',
        title: 'Widgets',
        description: 'Configure which widgets are displayed in the application',
        component: WidgetsSettings
    },
    {
        id: 'chrome-profiles',
        title: 'Chrome Profiles',
        description: 'Customize display names and icons for your Chrome profiles',
        component: ChromeProfilesSettings
    },
    {
        id: 'search-engine',
        title: 'Search Engine',
        description: 'Configure your preferred search engine for internet searches',
        component: SearchEngineSettings
    }
    // Add more categories here as needed
];

// Helper function to get a category by ID
export function getSettingsCategory(id: string): SettingsCategoryComponent | undefined {
    return settingsRegistry.find(category => category.id === id);
}

// Helper function to get all category titles for the left menu
export function getCategoryTitles(): Array<{ id: string; title: string; description?: string }> {
    return settingsRegistry.map(category => ({
        id: category.id,
        title: category.title,
        description: category.description
    }));
}
