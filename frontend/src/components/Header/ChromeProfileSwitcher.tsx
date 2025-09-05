import React, { useState } from 'react';
import {
    Box,
    Button,
    Typography,
    Chip,
    CircularProgress,
    Alert,
} from '@mui/material';
import { KeyboardArrowDown } from '@mui/icons-material';
import { useChromeProfiles } from '../../hooks';
import { type ChromeProfile } from '../../services';
import { ProfileMenu } from '../shared';
import styles from './ChromeProfileSwitcher.module.css';

export function ChromeProfileSwitcher() {
    const { profiles, activeProfile, profilesLoading, profilesError, loadChromeProfiles, switchProfile } = useChromeProfiles();
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

    if (profilesLoading) {
        return (
            <Box className={styles.loadingContainer}>
                <CircularProgress size={16} sx={{ color: 'white' }} />
                <Typography variant="body2" className={styles.loadingText}>
                    Loading profiles...
                </Typography>
            </Box>
        );
    }

    if (profilesError) {
        return (
            <Alert severity="warning" className={styles.errorAlert}>
                <Typography variant="body2" className={styles.errorText}>
                    {profilesError}
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

            <ProfileMenu
                anchorEl={anchorEl}
                open={Boolean(anchorEl)}
                onClose={handleProfileMenuClose}
                profiles={profiles}
                onProfileSelect={handleProfileSelect}
                title="Switch to profile:"
                selectedProfileId={activeProfile?.id}
                showActiveIndicator={true}
            />
        </Box>
    );
}
