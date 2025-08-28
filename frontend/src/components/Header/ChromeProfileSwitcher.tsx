import React, { useState, useEffect } from 'react';
import {
    Box,
    Button,
    Menu,
    MenuItem,
    Typography,
    Chip,
    CircularProgress,
    Alert,
} from '@mui/material';
import { KeyboardArrowDown } from '@mui/icons-material';
import { chromeService, type ChromeProfile } from '../../services';

interface ChromeProfileSwitcherProps {
    className?: string;
}

export function ChromeProfileSwitcher({ className }: ChromeProfileSwitcherProps) {
    const [profiles, setProfiles] = useState<ChromeProfile[]>([]);
    const [activeProfile, setActiveProfile] = useState<ChromeProfile | null>(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);

    // Load Chrome profiles on component mount
    useEffect(() => {
        loadChromeProfiles();
    }, []);

    const loadChromeProfiles = async () => {
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
    };

    const handleProfileMenuOpen = (event: React.MouseEvent<HTMLElement>) => {
        setAnchorEl(event.currentTarget);
    };

    const handleProfileMenuClose = () => {
        setAnchorEl(null);
    };

    const handleProfileSelect = async (profile: ChromeProfile) => {
        if (profile.id === activeProfile?.id) {
            handleProfileMenuClose();
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

        handleProfileMenuClose();
    };

    if (loading) {
        return (
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <CircularProgress size={16} sx={{ color: 'white' }} />
                <Typography variant="body2" sx={{ color: 'rgba(255, 255, 255, 0.8)' }}>
                    Loading profiles...
                </Typography>
            </Box>
        );
    }

    if (error) {
        return (
            <Alert severity="warning" sx={{ py: 0, backgroundColor: 'rgba(255, 193, 7, 0.1)', border: '1px solid rgba(255, 193, 7, 0.3)' }}>
                <Typography variant="body2" sx={{ color: 'rgba(255, 255, 255, 0.9)' }}>
                    {error}
                    <Button
                        size="small"
                        onClick={loadChromeProfiles}
                        sx={{ ml: 1, color: 'rgba(255, 255, 255, 0.8)' }}
                    >
                        Retry
                    </Button>
                </Typography>
            </Alert>
        );
    }

    if (profiles.length === 0) {
        return (
            <Alert severity="info" sx={{ py: 0, backgroundColor: 'rgba(33, 150, 243, 0.1)', border: '1px solid rgba(33, 150, 243, 0.3)' }}>
                <Typography variant="body2" sx={{ color: 'rgba(255, 255, 255, 0.9)' }}>
                    No Chrome profiles detected
                    <Button
                        size="small"
                        onClick={loadChromeProfiles}
                        sx={{ ml: 1, color: 'rgba(255, 255, 255, 0.8)' }}
                    >
                        Retry
                    </Button>
                </Typography>
            </Alert>
        );
    }

    return (
        <Box>
            <Button
                variant="outlined"
                size="small"
                onClick={handleProfileMenuOpen}
                startIcon={
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                        <span>{activeProfile?.icon || '👤'}</span>
                        {activeProfile?.is_active && (
                            <Chip
                                label="Active"
                                size="small"
                                color="primary"
                                sx={{ height: 16, fontSize: '0.7rem' }}
                            />
                        )}
                    </Box>
                }
                endIcon={<KeyboardArrowDown />}
                sx={{
                    minWidth: 'auto',
                    px: 1.5,
                    py: 0.5,
                    textTransform: 'none',
                    borderColor: 'rgba(255, 255, 255, 0.3)',
                    color: 'white',
                    backgroundColor: 'rgba(255, 255, 255, 0.1)',
                    backdropFilter: 'blur(10px)',
                    '&:hover': {
                        borderColor: 'rgba(255, 255, 255, 0.6)',
                        backgroundColor: 'rgba(255, 255, 255, 0.15)',
                    },
                    '& .MuiButton-startIcon': {
                        color: 'white',
                    },
                    '& .MuiButton-endIcon': {
                        color: 'rgba(255, 255, 255, 0.7)',
                    }
                }}
            >
                <Typography variant="body2" noWrap sx={{ color: 'white', fontWeight: 500 }}>
                    {activeProfile?.name || 'Select Profile'}
                </Typography>
            </Button>

            <Menu
                anchorEl={anchorEl}
                open={Boolean(anchorEl)}
                onClose={handleProfileMenuClose}
                PaperProps={{
                    sx: {
                        minWidth: 200,
                        mt: 1,
                    }
                }}
            >
                <MenuItem disabled>
                    <Typography variant="subtitle2" color="text.secondary">
                        Switch to profile:
                    </Typography>
                </MenuItem>
                {profiles.map(profile => (
                    <MenuItem
                        key={profile.id}
                        onClick={() => handleProfileSelect(profile)}
                        selected={profile.id === activeProfile?.id}
                        sx={{
                            display: 'flex',
                            alignItems: 'center',
                            gap: 1,
                            py: 1,
                        }}
                    >
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, flexGrow: 1 }}>
                            <span>{profile.icon || '👤'}</span>
                            <Typography variant="body2">
                                {profile.name}
                            </Typography>
                        </Box>
                        {profile.is_active && (
                            <Chip
                                label="Active"
                                size="small"
                                color="primary"
                                sx={{ height: 16, fontSize: '0.7rem' }}
                            />
                        )}
                    </MenuItem>
                ))}
            </Menu>
        </Box>
    );
}
