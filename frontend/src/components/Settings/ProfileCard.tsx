import React, { useState, useCallback } from 'react';
import {
    Box,
    Typography,
    TextField,
    Switch,
    FormControlLabel,
    Card,
    CardContent,
    Snackbar,
    Alert
} from '@mui/material';
import type { ChromeProfile } from '../../services/chrome.service';
import { settingsService } from '../../services';
import styles from './ProfileCard.module.css';

interface ProfileCardProps {
    profile: ChromeProfile;
    onProfileUpdate: (profileId: string, updates: {
        displayName: string;
        icon: string;
        enabled: boolean;
    }) => void;
}

export const ProfileCard: React.FC<ProfileCardProps> = ({ profile, onProfileUpdate }) => {
    const [displayName, setDisplayName] = useState(profile.name);
    const [icon, setIcon] = useState(profile.icon || '👤');
    const [enabled, setEnabled] = useState(profile.is_visible !== false); // Use profile visibility, default to true if not specified
    const [isSaving, setIsSaving] = useState(false);
    const [saveStatus, setSaveStatus] = useState<'success' | 'error' | null>(null);
    const [saveMessage, setSaveMessage] = useState('');

    // Debounced save function
    const debouncedSave = useCallback(
        (() => {
            let timeoutId: ReturnType<typeof setTimeout>;
            return (updates: { displayName: string; icon: string; enabled: boolean }) => {
                clearTimeout(timeoutId);
                timeoutId = setTimeout(async () => {
                    await saveToBackend(updates);
                }, 500); // 500ms delay
            };
        })(),
        []
    );

    const saveToBackend = async (updates: { displayName: string; icon: string; enabled: boolean }) => {
        try {
            setIsSaving(true);
            const response = await settingsService.updateChromeProfileSetting(
                profile.id,
                updates.displayName,
                updates.icon,
                updates.enabled
            );

            if (response.success) {
                setSaveStatus('success');
                setSaveMessage('Settings saved successfully');
            } else {
                setSaveStatus('error');
                setSaveMessage(response.message || 'Failed to save settings');
            }
        } catch (error) {
            setSaveStatus('error');
            setSaveMessage('Error saving settings');
            console.error('Error saving profile settings:', error);
        } finally {
            setIsSaving(false);
        }
    };

    const handleDisplayNameChange = (newValue: string) => {
        setDisplayName(newValue);
        const updates = {
            displayName: newValue,
            icon,
            enabled
        };

        // Notify parent component immediately for UI updates
        onProfileUpdate(profile.id, updates);

        // Debounced save to backend
        debouncedSave(updates);
    };

    const handleIconChange = (newValue: string) => {
        setIcon(newValue);
        const updates = {
            displayName,
            icon: newValue,
            enabled
        };

        // Notify parent component immediately for UI updates
        onProfileUpdate(profile.id, updates);

        // Debounced save to backend
        debouncedSave(updates);
    };

    const handleEnabledChange = (newValue: boolean) => {
        setEnabled(newValue);
        const updates = {
            displayName,
            icon,
            enabled: newValue
        };

        // Notify parent component immediately for UI updates
        onProfileUpdate(profile.id, updates);

        // Debounced save to backend
        debouncedSave(updates);
    };

    const handleCloseSnackbar = () => {
        setSaveStatus(null);
        setSaveMessage('');
    };

    return (
        <>
            <Card className={styles.profileCard}>
                <CardContent className={styles.cardContent}>
                    <Box className={styles.profileHeader}>
                        <Box className={styles.profileTitleSection}>
                            <Box className={styles.profileIcon}>
                                {icon}
                            </Box>
                            <Typography variant="h6" className={styles.profileName}>
                                {displayName}
                            </Typography>
                        </Box>
                        <FormControlLabel
                            control={
                                <Switch
                                    checked={enabled}
                                    onChange={(e) => handleEnabledChange(e.target.checked)}
                                    color="primary"
                                    sx={{
                                        '& .MuiSwitch-switchBase.Mui-checked': {
                                            color: '#4caf50',
                                        },
                                        '& .MuiSwitch-switchBase.Mui-checked + .MuiSwitch-track': {
                                            backgroundColor: '#4caf50',
                                        },
                                    }}
                                />
                            }
                            label={
                                <Typography variant="body2" sx={{ color: 'rgba(255, 255, 255, 0.8)' }}>
                                    {enabled ? 'Enabled' : 'Disabled'}
                                </Typography>
                            }
                            labelPlacement="start"
                        />
                    </Box>

                    <Box className={styles.profileInfo}>
                        <Typography variant="body2" className={styles.profilePath}>
                            <strong>Path:</strong> {profile.path || 'No path specified'}
                        </Typography>
                        <Typography variant="body2" className={styles.profileId}>
                            <strong>ID:</strong> {profile.id}
                        </Typography>
                    </Box>

                    <Box className={styles.editableFields}>
                        <Box className={styles.fieldRow}>
                            <TextField
                                label="Display Name"
                                value={displayName}
                                onChange={(e) => handleDisplayNameChange(e.target.value)}
                                size="small"
                                sx={{
                                    flex: 1,
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
                                label="Icon"
                                value={icon}
                                onChange={(e) => handleIconChange(e.target.value)}
                                size="small"
                                sx={{
                                    width: '120px',
                                    ml: 2,
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
                        </Box>

                        {isSaving && (
                            <Typography variant="caption" sx={{ color: 'rgba(255, 255, 255, 0.6)', mt: 1 }}>
                                Saving...
                            </Typography>
                        )}
                    </Box>
                </CardContent>
            </Card>

            <Snackbar
                open={saveStatus !== null}
                autoHideDuration={3000}
                onClose={handleCloseSnackbar}
                anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
            >
                <Alert
                    onClose={handleCloseSnackbar}
                    severity={saveStatus || 'info'}
                    sx={{ width: '100%' }}
                >
                    {saveMessage}
                </Alert>
            </Snackbar>
        </>
    );
};
