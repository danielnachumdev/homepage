import React, { useState, useEffect } from 'react';
import {
    Box,
    Typography,
    TextField,
    IconButton,
    Button,
    Card,
    CardContent,
    Alert,
    CircularProgress
} from '@mui/material';
import { Edit as EditIcon, Save as SaveIcon, Cancel as CancelIcon } from '@mui/icons-material';
import { chromeService } from '../../services/chrome.service';
import type { ChromeProfile } from '../../services/chrome.service';
import styles from './ChromeProfilesSettings.module.css';

interface ChromeProfileSettingsProps {
    onSettingChange?: (settingId: string, newValue: any) => void;
}

export const ChromeProfilesSettings: React.FC<ChromeProfileSettingsProps> = ({ onSettingChange }) => {
    const [profiles, setProfiles] = useState<ChromeProfile[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [editingProfile, setEditingProfile] = useState<string | null>(null);
    const [editValues, setEditValues] = useState<{ [key: string]: { displayName: string; icon: string } }>({});

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
                // Initialize edit values with current profile data
                const initialEditValues: { [key: string]: { displayName: string; icon: string } } = {};
                response.profiles.forEach(profile => {
                    initialEditValues[profile.id] = {
                        displayName: profile.name,
                        icon: profile.icon || '👤'
                    };
                });
                setEditValues(initialEditValues);
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

    const handleEditProfile = (profileId: string) => {
        setEditingProfile(profileId);
    };

    const handleCancelEdit = (profileId: string) => {
        setEditingProfile(null);
        // Reset to original values
        const profile = profiles.find(p => p.id === profileId);
        if (profile) {
            setEditValues(prev => ({
                ...prev,
                [profileId]: {
                    displayName: profile.name,
                    icon: profile.icon || '👤'
                }
            }));
        }
    };

    const handleSaveProfile = async (profileId: string) => {
        try {
            const profile = profiles.find(p => p.id === profileId);
            if (!profile) return;

            const newValues = editValues[profileId];

            // TODO: Call backend API to update profile
            // await chromeService.updateProfile(profileId, newValues);

            // For now, just update local state
            setProfiles(prev => prev.map(p =>
                p.id === profileId
                    ? { ...p, name: newValues.displayName, icon: newValues.icon }
                    : p
            ));

            // Notify parent component of setting change
            if (onSettingChange) {
                onSettingChange(`chrome-profile-${profileId}`, newValues);
            }

            setEditingProfile(null);
        } catch (err) {
            console.error('Error saving profile:', err);
            setError('Failed to save profile changes');
        }
    };

    const handleInputChange = (profileId: string, field: 'displayName' | 'icon', value: string) => {
        setEditValues(prev => ({
            ...prev,
            [profileId]: {
                ...prev[profileId],
                [field]: value
            }
        }));
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
                <Button variant="outlined" onClick={loadChromeProfiles}>
                    Retry
                </Button>
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
                Customize the display names and icons for your Chrome profiles. These changes will be reflected throughout the homepage.
            </Typography>

            <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', sm: 'repeat(2, 1fr)', md: 'repeat(3, 1fr)' }, gap: 3 }}>
                {profiles.map((profile) => {
                    const isEditing = editingProfile === profile.id;
                    const currentValues = editValues[profile.id] || { displayName: profile.name, icon: profile.icon || '👤' };

                    return (
                        <Box key={profile.id}>
                            <Card className={styles.profileCard}>
                                <CardContent>
                                    <Box className={styles.profileHeader}>
                                        <Typography variant="h6" className={styles.profileName}>
                                            {isEditing ? 'Editing Profile' : profile.name}
                                        </Typography>
                                        {!isEditing && (
                                            <IconButton
                                                size="small"
                                                onClick={() => handleEditProfile(profile.id)}
                                                className={styles.editButton}
                                            >
                                                <EditIcon />
                                            </IconButton>
                                        )}
                                    </Box>

                                    {isEditing ? (
                                        <Box className={styles.editForm}>
                                            <TextField
                                                fullWidth
                                                label="Display Name"
                                                value={currentValues.displayName}
                                                onChange={(e) => handleInputChange(profile.id, 'displayName', e.target.value)}
                                                size="small"
                                                sx={{
                                                    mb: 2,
                                                    '& .MuiOutlinedInput-root': {
                                                        color: 'white',
                                                        '& fieldset': {
                                                            borderColor: 'rgba(255, 255, 255, 0.3)',
                                                        },
                                                        '&:hover fieldset': {
                                                            borderColor: 'rgba(255, 255, 255, 0.5)',
                                                        },
                                                        '&.Mui-focused fieldset': {
                                                            borderColor: 'rgba(255, 255, 255, 0.8)',
                                                        },
                                                    },
                                                    '& .MuiInputLabel-root': {
                                                        color: 'rgba(255, 255, 255, 0.7)',
                                                    },
                                                }}
                                            />

                                            <TextField
                                                fullWidth
                                                label="Icon (emoji or text)"
                                                value={currentValues.icon}
                                                onChange={(e) => handleInputChange(profile.id, 'icon', e.target.value)}
                                                size="small"
                                                sx={{
                                                    mb: 2,
                                                    '& .MuiOutlinedInput-root': {
                                                        color: 'white',
                                                        '& fieldset': {
                                                            borderColor: 'rgba(255, 255, 255, 0.3)',
                                                        },
                                                        '&:hover fieldset': {
                                                            borderColor: 'rgba(255, 255, 255, 0.5)',
                                                        },
                                                        '&.Mui-focused fieldset': {
                                                            borderColor: 'rgba(255, 255, 255, 0.8)',
                                                        },
                                                    },
                                                    '& .MuiInputLabel-root': {
                                                        color: 'rgba(255, 255, 255, 0.7)',
                                                    },
                                                }}
                                            />

                                            <Box className={styles.editActions}>
                                                <Button
                                                    size="small"
                                                    variant="contained"
                                                    onClick={() => handleSaveProfile(profile.id)}
                                                    startIcon={<SaveIcon />}
                                                    sx={{ mr: 1 }}
                                                >
                                                    Save
                                                </Button>
                                                <Button
                                                    size="small"
                                                    variant="outlined"
                                                    onClick={() => handleCancelEdit(profile.id)}
                                                    startIcon={<CancelIcon />}
                                                >
                                                    Cancel
                                                </Button>
                                            </Box>
                                        </Box>
                                    ) : (
                                        <Box className={styles.profileDisplay}>
                                            <Box className={styles.profileIcon}>
                                                {profile.icon || '👤'}
                                            </Box>
                                            <Typography variant="body2" className={styles.profileDescription}>
                                                {profile.path || 'No path specified'}
                                            </Typography>
                                        </Box>
                                    )}
                                </CardContent>
                            </Card>
                        </Box>
                    );
                })}
            </Box>
        </Box>
    );
};
