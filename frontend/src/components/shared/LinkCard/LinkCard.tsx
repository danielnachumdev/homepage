import React, { useState } from 'react';
import {
    Card,
    CardContent,
    Typography,
    IconButton,
    Box,
    Menu,
    MenuItem,
    ListItemIcon,
    ListItemText,
    Tooltip,
} from '@mui/material';
import {
    MoreVert,
    Link as LinkIcon,
} from '@mui/icons-material';
import type { ChromeProfile } from '../../../hooks/useChromeProfiles';
import type { LinkItem } from '../../../types/linkCard';
import styles from './LinkCard.module.css';

export interface LinkCardProps extends LinkItem {
    chromeProfiles?: ChromeProfile[];
    onOpenInProfile?: (url: string, profile: ChromeProfile) => Promise<void>;
}

export function LinkCard({
    title,
    url,
    description,
    icon,
    chromeProfiles = [],
    onOpenInProfile,
}: LinkCardProps) {
    const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
    const [isMenuOpen, setIsMenuOpen] = useState(false);

    const handleMenuOpen = (event: React.MouseEvent<HTMLElement>) => {
        event.stopPropagation(); // Prevent card click when clicking menu button
        setAnchorEl(event.currentTarget);
        setIsMenuOpen(true);
    };

    const handleMenuClose = () => {
        setAnchorEl(null);
        setIsMenuOpen(false);
    };

    const handleOpenInNewTab = () => {
        window.open(url, '_blank');
        handleMenuClose();
    };

    const handleOpenInProfile = async (profile: ChromeProfile) => {
        if (onOpenInProfile) {
            try {
                await onOpenInProfile(url, profile);
            } catch (error) {
                console.error('Failed to open URL in profile:', error);
            }
        }
        handleMenuClose();
    };

    const handleDirectOpen = () => {
        window.open(url, '_blank');
    };

    const isDescriptionTruncated = description && description.length > 50;
    const tooltipTitle = isDescriptionTruncated ? description : '';

    return (
        <Tooltip title={tooltipTitle} arrow placement="top">
            <Card className={styles.linkCard} onClick={handleDirectOpen}>
                <CardContent className={styles.linkCardContent}>
                    <Box className={styles.linkHeader}>
                        <Box className={styles.linkInfo}>
                            <Box className={styles.linkTitleRow}>
                                {icon && (
                                    <Box className={styles.linkIcon}>
                                        <img src={icon} alt={`${title} icon`} className={styles.iconImage} />
                                    </Box>
                                )}
                                <Typography variant="h6" component="h3" className={styles.linkTitle}>
                                    {title}
                                </Typography>
                            </Box>

                            {description && (
                                <Typography variant="body2" className={styles.linkDescription}>
                                    {description.length > 50 ? `${description.substring(0, 50)}...` : description}
                                </Typography>
                            )}
                        </Box>

                        <Box className={styles.linkActions}>
                            {chromeProfiles.length > 0 && (
                                <IconButton
                                    size="small"
                                    onClick={handleMenuOpen}
                                    className={styles.menuButton}
                                >
                                    <MoreVert />
                                </IconButton>
                            )}
                        </Box>
                    </Box>

                    <Menu
                        anchorEl={anchorEl}
                        open={isMenuOpen}
                        onClose={handleMenuClose}
                        className={styles.profileMenu}
                    >
                        <MenuItem onClick={handleOpenInNewTab}>
                            <ListItemIcon>
                                <LinkIcon />
                            </ListItemIcon>
                            <ListItemText primary="Open in new tab" />
                        </MenuItem>

                        {chromeProfiles.map((profile) => (
                            <MenuItem
                                key={profile.id}
                                onClick={() => handleOpenInProfile(profile)}
                            >
                                <ListItemIcon>
                                    {profile.icon ? (
                                        <img
                                            src={profile.icon}
                                            alt={`${profile.name} icon`}
                                            className={styles.profileIcon}
                                        />
                                    ) : (
                                        <LinkIcon />
                                    )}
                                </ListItemIcon>
                                <ListItemText primary={`Open in ${profile.name}`} />
                            </MenuItem>
                        ))}
                    </Menu>
                </CardContent>
            </Card>
        </Tooltip>
    );
}
