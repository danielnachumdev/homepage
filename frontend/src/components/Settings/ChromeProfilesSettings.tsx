import React, { useState, useEffect } from 'react';
import {
    Box,
    Typography,
    Alert,
    CircularProgress
} from '@mui/material';
import { chromeService } from '../../services/chrome.service';
import type { ChromeProfile } from '../../services/chrome.service';
import { ProfileCard } from './ProfileCard';
import styles from './ChromeProfilesSettings.module.css';

interface ChromeProfileSettingsProps {
    onSettingChange?: (settingId: string, newValue: any) => void;
}

export const ChromeProfilesSettings: React.FC<ChromeProfileSettingsProps> = ({ onSettingChange }) => {
    const [profiles, setProfiles] = useState<ChromeProfile[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [profileSettings, setProfileSettings] = useState<{
        [key: string]: {
            displayName: string;
            icon: string;
            enabled: boolean;
        };
    }>({});

    // Load Chrome profiles on component mount
    useEffect(() => {
        loadChromeProfiles();
    }, []);

    const loadChromeProfiles = async () => {
        try {
            setLoading(true);
            setError(null);
            const response = await chromeService.getChromeProfiles();

            if (response.success && response.profiles) {
                setProfiles(response.profiles);
                // Initialize profile settings with current profile data
                const initialSettings: { [key: string]: { displayName: string; icon: string; enabled: boolean } } = {};
                response.profiles.forEach(profile => {
                    initialSettings[profile.id] = {
                        displayName: profile.name,
                        icon: profile.icon || '👤',
                        enabled: profile.is_visible !== false // Use profile visibility, default to true if not specified
                    };
                });
                setProfileSettings(initialSettings);
            } else {
                setError('Failed to load Chrome profiles');
            }
        } catch (err) {
            setError('Error loading Chrome profiles');
            console.error('Error loading Chrome profiles:', err);
        } finally {
            setLoading(false);
        }
    };

    const handleProfileUpdate = (profileId: string, updates: {
        displayName: string;
        icon: string;
        enabled: boolean;
    }) => {
        setProfileSettings(prev => ({
            ...prev,
            [profileId]: updates
        }));

        // Notify parent component of setting change
        if (onSettingChange) {
            onSettingChange(`chrome-profile-${profileId}`, updates);
        }

        // TODO: Call backend API to update profile
        // await chromeService.updateProfile(profileId, updates);
    };

    if (loading) {
        return (
            <Box className={styles.loadingContainer}>
                <CircularProgress />
                <Typography variant="body1" sx={{ mt: 2, color: 'rgba(255, 255, 255, 0.7)' }}>
                    Loading Chrome profiles...
                </Typography>
            </Box>
        );
    }

    if (error) {
        return (
            <Box className={styles.errorContainer}>
                <Alert severity="error" sx={{ mb: 2 }}>
                    {error}
                </Alert>
                <Typography
                    variant="body2"
                    sx={{
                        color: 'rgba(255, 255, 255, 0.8)',
                        cursor: 'pointer',
                        textDecoration: 'underline',
                        '&:hover': { color: 'white' }
                    }}
                    onClick={loadChromeProfiles}
                >
                    Click here to retry
                </Typography>
            </Box>
        );
    }

    if (profiles.length === 0) {
        return (
            <Box className={styles.emptyContainer}>
                <Typography variant="body1" sx={{ color: 'rgba(255, 255, 255, 0.7)' }}>
                    No Chrome profiles found
                </Typography>
            </Box>
        );
    }

    return (
        <Box className={styles.container}>
            <Typography variant="body2" sx={{ color: 'rgba(255, 255, 255, 0.7)', mb: 3 }}>
                Customize your Chrome profiles. All settings are automatically saved to the backend after you stop typing. Disabled profiles will not be included in the homepage.
            </Typography>

            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, width: '100%' }}>
                {profiles.map((profile) => {
                    const currentSettings = profileSettings[profile.id];
                    if (!currentSettings) return null;

                    return (
                        <Box key={profile.id}>
                            <ProfileCard
                                profile={profile}
                                onProfileUpdate={handleProfileUpdate}
                            />
                        </Box>
                    );
                })}
            </Box>
        </Box>
    );
};
