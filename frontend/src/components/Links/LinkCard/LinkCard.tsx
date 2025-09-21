import React, { useState } from 'react';
import {
    Card,
    CardContent as MuiCardContent,
    Typography,
    Box,
    IconButton,
    Menu,
    MenuItem,
    Tooltip,
    Avatar
} from '@mui/material';
import {
    MoreVert as MoreVertIcon
} from '@mui/icons-material';
import type { LinkCardProps } from '../../../types/link';
import styles from './LinkCard.module.css';

export function LinkCard({ link, onLinkClick, onChromeProfileClick }: LinkCardProps) {
    const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
    const [isHovered, setIsHovered] = useState(false);

    const handleCardClick = () => {
        onLinkClick(link);
    };

    const handleMenuClick = (event: React.MouseEvent<HTMLElement>) => {
        event.stopPropagation();
        setAnchorEl(event.currentTarget);
    };

    const handleMenuClose = () => {
        setAnchorEl(null);
    };

    const handleProfileClick = (profile: string) => {
        if (onChromeProfileClick) {
            onChromeProfileClick(link, profile);
        }
        handleMenuClose();
    };

    const truncateDescription = (text: string, maxLength: number = 60) => {
        if (text.length <= maxLength) return text;
        return text.substring(0, maxLength) + '...';
    };

    const CardContent = (
        <MuiCardContent className={styles.cardContent}>
            <Box className={styles.cardHeader}>
                <Box className={styles.titleSection}>
                    <Avatar
                        src={link.icon}
                        alt={link.title}
                        className={styles.icon}
                        variant="rounded"
                    />
                    <Typography
                        variant="h6"
                        component="h3"
                        className={styles.title}
                        noWrap
                    >
                        {link.title}
                    </Typography>
                </Box>

                {link.chromeProfileEnabled && link.chromeProfiles && link.chromeProfiles.length > 0 && (
                    <IconButton
                        size="small"
                        onClick={handleMenuClick}
                        className={styles.menuButton}
                        aria-label="Chrome profile options"
                    >
                        <MoreVertIcon fontSize="small" />
                    </IconButton>
                )}
            </Box>

            <Tooltip title={link.description} placement="top" arrow>
                <Typography
                    variant="body2"
                    className={styles.description}
                >
                    {truncateDescription(link.description)}
                </Typography>
            </Tooltip>
        </MuiCardContent>
    );

    return (
        <>
            <Card
                className={`${styles.card} ${isHovered ? styles.cardHovered : ''}`}
                onClick={handleCardClick}
                onMouseEnter={() => setIsHovered(true)}
                onMouseLeave={() => setIsHovered(false)}
                elevation={isHovered ? 4 : 1}
            >
                {CardContent}
            </Card>

            {link.chromeProfileEnabled && link.chromeProfiles && link.chromeProfiles.length > 0 && (
                <Menu
                    anchorEl={anchorEl}
                    open={Boolean(anchorEl)}
                    onClose={handleMenuClose}
                    anchorOrigin={{
                        vertical: 'center',
                        horizontal: 'right',
                    }}
                    transformOrigin={{
                        vertical: 'center',
                        horizontal: 'left',
                    }}
                >
                    {link.chromeProfiles.map((profile) => (
                        <MenuItem
                            key={profile}
                            onClick={() => handleProfileClick(profile)}
                        >
                            {profile}
                        </MenuItem>
                    ))}
                </Menu>
            )}
        </>
    );
}
