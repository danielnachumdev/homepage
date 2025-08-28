import React, { useState } from 'react';
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
import { useChromeProfiles } from '../../hooks';
import { type ChromeProfile } from '../../services';
import styles from './ChromeProfileSwitcher.module.css';

interface ChromeProfileSwitcherProps {
    className?: string;
}

export function ChromeProfileSwitcher({ className }: ChromeProfileSwitcherProps) {
    const { profiles, activeProfile, loading, error, loadChromeProfiles, switchProfile } = useChromeProfiles();
    const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);

    const handleProfileMenuOpen = (event: React.MouseEvent<HTMLElement>) => {
        setAnchorEl(event.currentTarget);
    };

    const handleProfileMenuClose = () => {
        setAnchorEl(null);
    };

    const handleProfileSelect = async (profile: ChromeProfile) => {
        await switchProfile(profile);
        handleProfileMenuClose();
    };

    if (loading) {
        return (
            <Box className={styles.loadingContainer}>
                <CircularProgress size={16} sx={{ color: 'white' }} />
                <Typography variant="body2" className={styles.loadingText}>
                    Loading profiles...
                </Typography>
            </Box>
        );
    }

    if (error) {
        return (
            <Alert severity="warning" className={styles.errorAlert}>
                <Typography variant="body2" className={styles.errorText}>
                    {error}
                    <Button
                        size="small"
                        onClick={loadChromeProfiles}
                        className={styles.retryButton}
                    >
                        Retry
                    </Button>
                </Typography>
            </Alert>
        );
    }

    if (profiles.length === 0) {
        return (
            <Alert severity="info" className={styles.infoAlert}>
                <Typography variant="body2" className={styles.infoText}>
                    No Chrome profiles detected
                    <Button
                        size="small"
                        onClick={loadChromeProfiles}
                        className={styles.retryButton}
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
                    <Box className={styles.profileButtonStartIconContainer}>
                        <span>{activeProfile?.icon || '👤'}</span>
                        {activeProfile?.is_active && (
                            <Chip
                                label="Active"
                                size="small"
                                color="primary"
                                className={styles.activeChip}
                            />
                        )}
                    </Box>
                }
                endIcon={<KeyboardArrowDown />}
                className={styles.profileButton}
            >
                <Typography variant="body2" noWrap className={styles.profileButtonText}>
                    {activeProfile?.name || 'Select Profile'}
                </Typography>
            </Button>

            <Menu
                anchorEl={anchorEl}
                open={Boolean(anchorEl)}
                onClose={handleProfileMenuClose}
                PaperProps={{
                    className: styles.profileMenuPaper
                }}
            >
                <MenuItem disabled className={styles.profileMenuHeaderItem}>
                    <Typography variant="subtitle2" className={styles.profileMenuHeaderTextOverride}>
                        Switch to profile:
                    </Typography>
                </MenuItem>
                {profiles.map(profile => (
                    <MenuItem
                        key={profile.id}
                        onClick={() => handleProfileSelect(profile)}
                        selected={profile.id === activeProfile?.id}
                        disabled={profile.is_active}
                        className={`${styles.profileMenuItemBase} ${profile.is_active
                            ? styles.profileMenuItemActiveOverride
                            : styles.profileMenuItemInactiveOverride
                            } ${profile.id === activeProfile?.id
                                ? styles.profileMenuItemSelectedOverride
                                : ''
                            } ${profile.is_active
                                ? styles.profileMenuItemDisabledOverride
                                : ''
                            }`}
                    >
                        <Box className={styles.profileMenuItem}>
                            <span className={profile.is_active ? styles.profileIconActiveOverride : styles.profileIconOverride}>
                                {profile.icon || '👤'}
                            </span>
                            <Typography
                                variant="body2"
                                className={profile.is_active ? styles.profileNameActiveOverride : styles.profileNameOverride}
                            >
                                {profile.name}
                            </Typography>
                        </Box>
                        {profile.is_active && (
                            <Chip
                                label="Active"
                                size="small"
                                color="primary"
                                className={styles.activeChipOverride}
                            />
                        )}
                    </MenuItem>
                ))}
            </Menu>
        </Box>
    );
}
