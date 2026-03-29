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
    MoreVert as MoreVertIcon,
    Link as LinkIcon
} from '@mui/icons-material';
import type { LinkCardProps, LinkSubItem } from '../../../types/link';
import styles from './LinkCard.module.css';

function SubLinkRow({
    sub,
    onActivate
}: {
    sub: LinkSubItem;
    onActivate: () => void;
}) {
    const [iconIndex, setIconIndex] = useState(0);
    const src = Array.isArray(sub.icon) ? sub.icon[iconIndex] ?? sub.icon[0] : sub.icon;
    const hasMoreIcons = Array.isArray(sub.icon) && iconIndex < sub.icon.length - 1;

    const handleKeyDown = (e: React.KeyboardEvent) => {
        if (e.key === 'Enter' || e.key === ' ') {
            e.preventDefault();
            onActivate();
        }
    };

    const row = (
        <Box
            className={styles.sublinkRow}
            onClick={(e) => {
                e.stopPropagation();
                onActivate();
            }}
            onKeyDown={handleKeyDown}
            role="button"
            tabIndex={0}
            aria-label={sub.description ? `${sub.title}: ${sub.description}` : sub.title}
        >
            <Avatar
                src={src}
                alt=""
                className={styles.sublinkIcon}
                variant="rounded"
                onError={() => {
                    if (hasMoreIcons) setIconIndex((i) => i + 1);
                }}
            >
                {!hasMoreIcons && <LinkIcon sx={{ fontSize: 18 }} />}
            </Avatar>
            <Typography variant="body2" component="span" className={styles.sublinkTitle} noWrap>
                {sub.title}
            </Typography>
        </Box>
    );

    if (sub.description) {
        return (
            <Tooltip title={sub.description} placement="left" arrow>
                {row}
            </Tooltip>
        );
    }
    return row;
}

export function LinkCard({ link, onLinkClick, onChromeProfileClick, onSublinkClick }: LinkCardProps) {
    const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
    const [isHovered, setIsHovered] = useState(false);
    const [currentIconIndex, setCurrentIconIndex] = useState(0);

    const sublinks = link.sublinks?.length ? link.sublinks : null;

    const getCurrentIcon = () => {
        if (Array.isArray(link.icon)) {
            return link.icon[currentIconIndex] || link.icon[0];
        }
        return link.icon;
    };

    const hasMoreIcons = Array.isArray(link.icon) && currentIconIndex < link.icon.length - 1;

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

    const truncateDescription = (text: string | undefined, maxLength: number = 60) => {
        if (!text) return '';
        if (text.length <= maxLength) return text;
        return text.substring(0, maxLength) + '...';
    };

    const handleIconError = () => {
        if (hasMoreIcons) {
            setCurrentIconIndex((prev) => prev + 1);
        }
    };

    const handleSublinkActivate = (sub: LinkSubItem) => {
        onSublinkClick?.(link, sub);
    };

    const MainColumn = (
        <>
            <Box className={styles.cardHeader}>
                <Box className={styles.titleSection}>
                    <Avatar
                        src={getCurrentIcon()}
                        alt={link.title}
                        className={styles.icon}
                        variant="rounded"
                        onError={handleIconError}
                    >
                        {!hasMoreIcons && <LinkIcon />}
                    </Avatar>
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

            {link.description && (
                <Tooltip title={link.description} placement="top" arrow>
                    <Typography
                        variant="body2"
                        className={sublinks ? styles.descriptionCompact : styles.description}
                    >
                        {truncateDescription(link.description, sublinks ? 48 : 60)}
                    </Typography>
                </Tooltip>
            )}
        </>
    );

    return (
        <>
            <Card
                className={`${styles.card} ${sublinks ? styles.cardWithSublinks : ''} ${isHovered ? styles.cardHovered : ''}`}
                onClick={sublinks ? undefined : handleCardClick}
                onMouseEnter={() => setIsHovered(true)}
                onMouseLeave={() => setIsHovered(false)}
                elevation={isHovered ? 4 : 1}
            >
                <MuiCardContent
                    className={sublinks ? `${styles.cardContent} ${styles.cardContentSplit}` : styles.cardContent}
                >
                    {sublinks ? (
                        <Box className={styles.splitRow}>
                            <Box className={styles.mainHalf} onClick={handleCardClick}>
                                {MainColumn}
                            </Box>
                            <Box className={styles.sublinksHalf}>
                                <Box className={styles.sublinksScroll}>
                                    {sublinks.map((sub, i) => (
                                        <SubLinkRow
                                            key={`${sub.title}-${i}`}
                                            sub={sub}
                                            onActivate={() => handleSublinkActivate(sub)}
                                        />
                                    ))}
                                </Box>
                            </Box>
                        </Box>
                    ) : (
                        <Box onClick={handleCardClick} className={styles.singleColumn}>
                            {MainColumn}
                        </Box>
                    )}
                </MuiCardContent>
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
                    <Box className={styles.menuHeader}>
                        <Typography variant="caption" className={styles.menuHeaderText}>
                            Choose browser profile to open link
                        </Typography>
                    </Box>
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
