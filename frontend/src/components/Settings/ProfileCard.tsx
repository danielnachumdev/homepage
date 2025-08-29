import React, { useState } from 'react';
import {
    Box,
    Typography,
    TextField,
    Switch,
    FormControlLabel,
    Card,
    CardContent
} from '@mui/material';
import type { ChromeProfile } from '../../services/chrome.service';
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
    const [enabled, setEnabled] = useState(true); // Default to enabled

    const handleDisplayNameChange = (newValue: string) => {
        setDisplayName(newValue);
        onProfileUpdate(profile.id, {
            displayName: newValue,
            icon,
            enabled
        });
    };

    const handleIconChange = (newValue: string) => {
        setIcon(newValue);
        onProfileUpdate(profile.id, {
            displayName,
            icon: newValue,
            enabled
        });
    };

    const handleEnabledChange = (newValue: boolean) => {
        setEnabled(newValue);
        onProfileUpdate(profile.id, {
            displayName,
            icon,
            enabled: newValue
        });
    };

    return (
        <Card className={styles.profileCard}>
            <CardContent>
                <Box className={styles.profileHeader}>
                    <Typography variant="h6" className={styles.profileName}>
                        Profile Settings
                    </Typography>
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
                    <Box className={styles.profileIcon}>
                        {icon}
                    </Box>

                    <Typography variant="body2" className={styles.profilePath}>
                        <strong>Path:</strong> {profile.path || 'No path specified'}
                    </Typography>

                    <Typography variant="body2" className={styles.profileId}>
                        <strong>ID:</strong> {profile.id}
                    </Typography>
                </Box>

                <Box className={styles.editableFields}>
                    <TextField
                        fullWidth
                        label="Display Name"
                        value={displayName}
                        onChange={(e) => handleDisplayNameChange(e.target.value)}
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
                        value={icon}
                        onChange={(e) => handleIconChange(e.target.value)}
                        size="small"
                        sx={{
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
            </CardContent>
        </Card>
    );
};
