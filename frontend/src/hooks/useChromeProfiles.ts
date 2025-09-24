import { useState, useEffect, useCallback, useMemo } from 'react';
import { useSettings } from './useSettings';
import { api } from '../lib/api';
import { useComponentLogger } from './useLogger';

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
    const logger = useComponentLogger('useChromeProfiles');
    logger.debug('useChromeProfiles hook called');

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
        logger.debug('loadChromeProfiles called');
        try {
            setProfilesLoading(true);
            setProfilesError(null);

            // Get profiles directly from settings - no API call needed
            logger.debug('Processing profiles', {
                count: settings.chromeProfiles.profiles.length
            });
            const currentProfiles = settings.chromeProfiles.profiles.map(profileSetting => ({
                id: profileSetting.profileId,
                name: profileSetting.displayName,
                icon: profileSetting.icon,
                is_active: false, // Active status is not stored in settings, default to false
                enabled: profileSetting.enabled,
            }));

            // Set the first profile as default active (since we don't track active status in settings)
            if (currentProfiles.length > 0) {
                logger.info('Setting active profile', {
                    profileName: currentProfiles[0].name
                });
                setActiveProfile(currentProfiles[0]);
            }
        } catch (err) {
            logger.error('Failed to load Chrome profiles', {
                error: err instanceof Error ? err.message : 'Unknown error',
                stack: err instanceof Error ? err.stack : undefined
            });
            setProfilesError('Failed to load Chrome profiles from settings');
        } finally {
            logger.debug('loadChromeProfiles completed');
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
            logger.error('Error refreshing profiles', { error: err });
        } finally {
            setProfilesLoading(false);
        }
    }, [refresh]); // Remove loadChromeProfiles from dependencies to avoid circular dependency

    const openUrlInProfile = useCallback(async (request: OpenUrlRequest): Promise<OpenUrlResponse> => {
        logger.debug('Opening URL in profile', { url: request.url, profileId: request.profile_id });
        try {
            const response = await api.post('/api/v1/chrome/open-url', request);
            logger.info('URL opened successfully in profile', {
                url: request.url,
                profileId: request.profile_id,
                success: response.data.success
            });
            return response.data;
        } catch (error) {
            logger.error('Failed to open URL in profile', { error, url: request.url, profileId: request.profile_id });
            throw error;
        }
    }, []);

    const switchProfile = useCallback(async (profile: ChromeProfile) => {
        if (profile.id === activeProfile?.id) {
            logger.debug('Profile already active, skipping switch', { profileId: profile.id, profileName: profile.name });
            return;
        }

        logger.debug('Switching to profile', {
            fromProfile: activeProfile?.name || 'none',
            toProfile: profile.name,
            profileId: profile.id
        });

        try {
            // Get current URL and open it in the new profile
            const currentUrl = window.location.href;
            const response = await openUrlInProfile({
                url: currentUrl,
                profile_id: profile.id,
            });

            if (response.success) {
                logger.info('Profile switched successfully', { profileName: profile.name });
                setActiveProfile(profile);
                // Note: Profile state is managed by the unified settings
                // The active state will be updated when settings are refreshed
            } else {
                logger.error('Failed to switch profile', { message: response.message });
                setProfilesError(`Failed to switch profile: ${response.message}`);
            }
        } catch (err) {
            logger.error('Error switching profile', { error: err });
            setProfilesError('Failed to communicate with backend');
        }
    }, [activeProfile?.id, openUrlInProfile]);

    // No need to call loadChromeProfiles - profiles are computed in useMemo

    // Set active profile when profiles are first loaded
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
