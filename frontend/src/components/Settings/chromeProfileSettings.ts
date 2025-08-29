import { chromeService } from '../../services/chrome.service';
import type { ChromeProfileSetting } from './types';

export async function generateChromeProfileSettings(): Promise<ChromeProfileSetting[]> {
    try {
        const response = await chromeService.getChromeProfiles();

        if (!response.success || !response.profiles) {
            console.warn('Failed to fetch Chrome profiles for settings');
            return [];
        }

        return response.profiles.map(profile => ({
            id: `chrome-profile-${profile.id}`,
            name: `Profile: ${profile.name}`,
            description: `Customize display name and icon for Chrome profile "${profile.name}"`,
            type: 'chrome-profile' as const,
            value: {
                displayName: profile.name,
                icon: profile.icon || '👤'
            },
            profileId: profile.id,
            originalName: profile.name
        }));
    } catch (error) {
        console.error('Error generating Chrome profile settings:', error);
        return [];
    }
}

export async function updateChromeProfileSetting(
    setting: ChromeProfileSetting,
    newValue: { displayName: string; icon: string }
): Promise<boolean> {
    try {
        // Here you would typically call an API to update the profile
        // For now, we'll just return success
        console.log(`Updating Chrome profile ${setting.profileId}:`, newValue);

        // TODO: Implement actual API call to update profile
        // await chromeService.updateProfile(setting.profileId, newValue);

        return true;
    } catch (error) {
        console.error('Error updating Chrome profile setting:', error);
        return false;
    }
}
