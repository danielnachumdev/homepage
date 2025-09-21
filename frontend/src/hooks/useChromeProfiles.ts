import { useState, useEffect, useCallback, useMemo } from 'react';
import { useSettings } from './useSettings';
import { api } from '../lib/api';

export interface ChromeProfile {
    id: string;
    name: string;
    icon?: string;
    is_active: boolean;
    is_visible?: boolean;
    path?: string;
    enabled?: boolean;
}

export interface OpenUrlRequest {
    url: string;
    profile_id: string;
}

export interface OpenUrlResponse {
    success: boolean;
    message: string;
    profile_name?: string;
}

interface UseChromeProfilesReturn {
    // Chrome profiles specific data
    profiles: ChromeProfile[];
    activeProfile: ChromeProfile | null;
    switchProfile: (profile: ChromeProfile) => Promise<void>;
    openUrlInProfile: (request: OpenUrlRequest) => Promise<OpenUrlResponse>;

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
    const profiles: ChromeProfile[] = useMemo(() => {
        return settings.chromeProfiles.profiles.map(profileSetting => ({
            id: profileSetting.profileId,
            name: profileSetting.displayName,
            icon: profileSetting.icon,
            is_active: false, // This will be determined by backend data
            enabled: profileSetting.enabled,
        }));
    }, [settings.chromeProfiles.profiles]);

    const loadChromeProfiles = useCallback(async () => {
        try {
            setProfilesLoading(true);
            setProfilesError(null);

            // Get profiles directly from settings - no API call needed
            const currentProfiles = settings.chromeProfiles.profiles.map(profileSetting => ({
                id: profileSetting.profileId,
                name: profileSetting.displayName,
                icon: profileSetting.icon,
                is_active: false, // Active status is not stored in settings, default to false
                enabled: profileSetting.enabled,
            }));

            // Set the first profile as default active (since we don't track active status in settings)
            if (currentProfiles.length > 0) {
                setActiveProfile(currentProfiles[0]);
            }
        } catch (err) {
            setProfilesError('Failed to load Chrome profiles from settings');
            console.error('Error loading Chrome profiles:', err);
        } finally {
            setProfilesLoading(false);
        }
    }, [settings.chromeProfiles.profiles]);

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

    const openUrlInProfile = useCallback(async (request: OpenUrlRequest): Promise<OpenUrlResponse> => {
        try {
            const response = await api.post('/api/v1/chrome/open-url', request);
            return response.data;
        } catch (error) {
            console.error('Failed to open URL in profile:', error);
            throw error;
        }
    }, []);

    const switchProfile = useCallback(async (profile: ChromeProfile) => {
        if (profile.id === activeProfile?.id) {
            return;
        }

        try {
            // Get current URL and open it in the new profile
            const currentUrl = window.location.href;
            const response = await openUrlInProfile({
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
    }, [activeProfile?.id, openUrlInProfile]);

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
        openUrlInProfile,

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
