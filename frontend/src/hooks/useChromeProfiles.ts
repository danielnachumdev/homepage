import { useState, useEffect, useCallback, useMemo } from 'react';
import { chromeService, type ChromeProfile } from '../services';
import { useSettings } from './useSettings';

interface UseChromeProfilesReturn {
    // Chrome profiles specific data
    profiles: ChromeProfile[];
    activeProfile: ChromeProfile | null;
    switchProfile: (profile: ChromeProfile) => Promise<void>;

    // Chrome profiles specific loading/error states
    profilesLoading: boolean;
    profilesError: string | null;
    loadChromeProfiles: () => Promise<void>;
    refreshProfiles: () => Promise<void>; // Alias for loadChromeProfiles for backward compatibility

    // Inherited from useSettings
    loading: boolean;
    error: string | null;
    refresh: () => Promise<void>;
}

export function useChromeProfiles(): UseChromeProfilesReturn {
    const { settings, loading: settingsLoading, error: settingsError, refresh } = useSettings();
    const [activeProfile, setActiveProfile] = useState<ChromeProfile | null>(null);
    const [profilesLoading, setProfilesLoading] = useState(false);
    const [profilesError, setProfilesError] = useState<string | null>(null);
    // Convert settings data to ChromeProfile format - memoized for performance
    const profiles: ChromeProfile[] = useMemo(() =>
        settings.chromeProfiles.profiles.map(profileSetting => ({
            id: profileSetting.profileId,
            name: profileSetting.displayName,
            icon: profileSetting.icon,
            is_active: false, // This will be determined by backend data
            enabled: profileSetting.enabled,
        })),
        [settings.chromeProfiles.profiles]
    );

    const loadChromeProfiles = useCallback(async () => {
        try {
            setProfilesLoading(true);
            setProfilesError(null);

            // Get the current profiles from settings (not from the memoized profiles)
            const currentProfiles = settings.chromeProfiles.profiles.map(profileSetting => ({
                id: profileSetting.profileId,
                name: profileSetting.displayName,
                icon: profileSetting.icon,
                is_active: false, // This will be determined by backend data
                enabled: profileSetting.enabled,
            }));

            // Then get the actual Chrome profiles from backend to get active status
            const response = await chromeService.getChromeProfiles();
            if (response.success) {
                // Merge backend data with settings data
                const enrichedProfiles = currentProfiles.map(profileSetting => {
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
                setProfilesError(response.message || 'Failed to load Chrome profiles');
            }
        } catch (err) {
            setProfilesError('Failed to connect to backend for Chrome profiles');
            console.error('Error loading Chrome profiles:', err);
        } finally {
            setProfilesLoading(false);
        }
    }, [settings.chromeProfiles.profiles]); // Removed refresh to prevent circular dependency

    // Separate function for refreshing profiles that includes settings refresh
    const refreshProfiles = useCallback(async () => {
        try {
            setProfilesLoading(true);
            setProfilesError(null);

            // First refresh the unified settings to get latest profile configurations
            await refresh();

            // Then load Chrome profiles with the fresh settings
            await loadChromeProfiles();
        } catch (err) {
            setProfilesError('Failed to refresh profiles');
            console.error('Error refreshing profiles:', err);
        } finally {
            setProfilesLoading(false);
        }
    }, [refresh, loadChromeProfiles]);

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
                setProfilesError(`Failed to switch profile: ${response.message}`);
            }
        } catch (err) {
            console.error('Error switching profile:', err);
            setProfilesError('Failed to communicate with backend');
        }
    }, [activeProfile?.id]);

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
        // Chrome profiles specific data
        profiles,
        activeProfile,
        switchProfile,

        // Chrome profiles specific loading/error states
        profilesLoading,
        profilesError,
        loadChromeProfiles,
        refreshProfiles, // Separate function that includes settings refresh

        // Inherited from useSettings
        loading: settingsLoading,
        error: settingsError,
        refresh,
    };
}
