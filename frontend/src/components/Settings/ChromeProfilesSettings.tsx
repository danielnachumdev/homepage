import React, { useState, useEffect } from 'react';
import {
    Box,
    Typography,
    Alert,
    CircularProgress
} from '@mui/material';
import { settingsService } from '../../services';
import { useChromeProfiles } from '../../hooks';
import { useComponentLogger } from '../../hooks/useLogger';
import { ProfileCard } from './ProfileCard';
import styles from './ChromeProfilesSettings.module.css';

interface ChromeProfileSettingsProps {
    onSettingChange?: (settingId: string, newValue: any) => void;
    onProfilesRefresh?: () => void;
}

export const ChromeProfilesSettings: React.FC<ChromeProfileSettingsProps> = ({ onSettingChange, onProfilesRefresh }) => {
    const logger = useComponentLogger('ChromeProfilesSettings');
    const { profiles, loading, error, refreshProfiles } = useChromeProfiles();
    const [profileSettings, setProfileSettings] = useState<{
        [key: string]: {
            displayName: string;
            icon: string;
            enabled: boolean;
        };
    }>({});

    // Initialize profile settings when profiles change
    useEffect(() => {
        if (profiles.length > 0) {
            const initialSettings: { [key: string]: { displayName: string; icon: string; enabled: boolean } } = {};
            profiles.forEach(profile => {
                initialSettings[profile.id] = {
                    displayName: profile.name,
                    icon: profile.icon || '👤',
                    enabled: profile.enabled !== false // Use profile enabled status
                };
            });
            setProfileSettings(initialSettings);
        }
    }, [profiles]);

    const handleProfileUpdate = async (profileId: string, updates: {
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

        // Update setting in backend
        try {
            await settingsService.updateChromeProfileSetting(
                profileId,
                updates.displayName,
                updates.icon,
                updates.enabled
            );

            // Refresh profiles to reflect changes
            await refreshProfiles();
            if (onProfilesRefresh) {
                onProfilesRefresh();
            }
        } catch (error) {
            logger.error('Failed to update profile setting', { error, profileId, updates });
        }
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
                    onClick={refreshProfiles}
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
