import { useState, useEffect, useCallback } from 'react';
import { chromeService, type ChromeProfile } from '../services';

interface UseChromeProfilesReturn {
    profiles: ChromeProfile[];
    activeProfile: ChromeProfile | null;
    loading: boolean;
    error: string | null;
    loadChromeProfiles: () => Promise<void>;
    switchProfile: (profile: ChromeProfile) => Promise<void>;
}

export function useChromeProfiles(): UseChromeProfilesReturn {
    const [profiles, setProfiles] = useState<ChromeProfile[]>([]);
    const [activeProfile, setActiveProfile] = useState<ChromeProfile | null>(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const loadChromeProfiles = useCallback(async () => {
        try {
            setLoading(true);
            setError(null);
            const response = await chromeService.getChromeProfiles();
            if (response.success) {
                setProfiles(response.profiles);
                // Set the first active profile as default
                const active = response.profiles.find(p => p.is_active) || response.profiles[0];
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
    }, []);

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
                // Update the profiles list to reflect the new active state
                setProfiles(prev => prev.map(p => ({
                    ...p,
                    is_active: p.id === profile.id
                })));
            } else {
                console.error('Failed to switch profile:', response.message);
                setError(`Failed to switch profile: ${response.message}`);
            }
        } catch (err) {
            console.error('Error switching profile:', err);
            setError('Failed to communicate with backend');
        }
    }, [activeProfile?.id]);

    // Load Chrome profiles on hook initialization
    useEffect(() => {
        loadChromeProfiles();
    }, [loadChromeProfiles]);

    return {
        profiles,
        activeProfile,
        loading,
        error,
        loadChromeProfiles,
        switchProfile,
    };
}
