import { useState, useEffect, useCallback } from 'react';
import { chromeService, type ChromeProfile } from '../services';
import { useSettings } from '../contexts/SettingsContext';

interface UseChromeProfilesReturn {
    profiles: ChromeProfile[];
    activeProfile: ChromeProfile | null;
    loading: boolean;
    error: string | null;
    loadChromeProfiles: () => Promise<void>;
    switchProfile: (profile: ChromeProfile) => Promise<void>;
    refreshProfiles: () => Promise<void>;
}

export function useChromeProfiles(): UseChromeProfilesReturn {
    const { settings, loading: settingsLoading, error: settingsError, refreshSettings } = useSettings();
    const [activeProfile, setActiveProfile] = useState<ChromeProfile | null>(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    // Convert settings data to ChromeProfile format
    const profiles: ChromeProfile[] = settings.chromeProfiles.profiles.map(profileSetting => ({
        id: profileSetting.profileId,
        name: profileSetting.displayName,
        icon: profileSetting.icon,
        is_active: false, // This will be determined by backend data
        enabled: profileSetting.enabled,
    }));

    const loadChromeProfiles = useCallback(async () => {
        try {
            setLoading(true);
            setError(null);

            // First refresh the unified settings
            await refreshSettings();

            // Then get the actual Chrome profiles from backend to get active status
            const response = await chromeService.getChromeProfiles();
            if (response.success) {
                // Merge backend data with settings data
                const enrichedProfiles = profiles.map(profileSetting => {
                    const backendProfile = response.profiles.find(p => p.id === profileSetting.id);
                    return {
                        ...profileSetting,
                        is_active: backendProfile?.is_active || false,
                    };
                });

                // Set the first active profile as default
                const active = enrichedProfiles.find(p => p.is_active) || enrichedProfiles[0];
                setActiveProfile(active);
            } else {
                setError(response.message || 'Failed to load Chrome profiles');
            }
        } catch (err) {
            setError('Failed to connect to backend for Chrome profiles');
            console.error('Error loading Chrome profiles:', err);
        } finally {
            setLoading(false);
        }
    }, [profiles, refreshSettings]);

    const switchProfile = useCallback(async (profile: ChromeProfile) => {
        if (profile.id === activeProfile?.id) {
            return;
        }

        try {
            // Get current URL and open it in the new profile
            const currentUrl = window.location.href;
            const response = await chromeService.openUrlInProfile({
                url: currentUrl,
                profile_id: profile.id,
            });

            if (response.success) {
                console.log(`Switched to profile: ${profile.name}`);
                setActiveProfile(profile);
                // Note: Profile state is managed by the unified settings
                // The active state will be updated when settings are refreshed
            } else {
                console.error('Failed to switch profile:', response.message);
                setError(`Failed to switch profile: ${response.message}`);
            }
        } catch (err) {
            console.error('Error switching profile:', err);
            setError('Failed to communicate with backend');
        }
    }, [activeProfile?.id]);

    const refreshProfiles = useCallback(async () => {
        await loadChromeProfiles();
    }, [loadChromeProfiles]);

    // Load Chrome profiles on hook initialization
    useEffect(() => {
        loadChromeProfiles();
    }, [loadChromeProfiles]);

    // Update active profile when profiles change
    useEffect(() => {
        if (profiles.length > 0 && !activeProfile) {
            const active = profiles.find(p => p.is_active) || profiles[0];
            setActiveProfile(active);
        }
    }, [profiles, activeProfile]);

    return {
        profiles,
        activeProfile,
        loading: loading || settingsLoading,
        error: error || settingsError,
        loadChromeProfiles,
        switchProfile,
        refreshProfiles,
    };
}
