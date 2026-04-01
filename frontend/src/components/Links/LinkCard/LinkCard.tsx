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
import type { LinkCardAddon, LinkCardCompositeAddon, LinkCardLeafAddon, LinkCardProps, LinkSubItem } from '../../../types/link';
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

    const sublinksAddon =
        link.addon?.type === 'sublinks' && link.addon.items.length > 0 ? link.addon : null;
    const isSplitLayout = Boolean(sublinksAddon);

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

    type AddonType = LinkCardAddon['type'];
    type AddonRendererMap = {
        [K in AddonType]: (addon: Extract<LinkCardAddon, { type: K }>) => React.ReactNode;
    };

    const stopCardInteraction = (e: React.SyntheticEvent) => {
        e.stopPropagation();
    };

    const leafAddonRenderers = {
        audioPlayer: (a: Extract<LinkCardLeafAddon, { type: 'audioPlayer' }>, key: string) => (
            <Box
                key={key}
                className={styles.audioContainer}
                onClick={stopCardInteraction}
                onMouseDown={stopCardInteraction}
                onKeyDown={stopCardInteraction}
            >
                <audio className={styles.audio} controls preload="none">
                    <source src={a.streamUrl} type={a.mimeType ?? 'audio/mpeg'} />
                    Your browser does not support the audio element.
                </audio>
            </Box>
        ),
        sublinks: (a: Extract<LinkCardLeafAddon, { type: 'sublinks' }>) => (
            <Box className={styles.sublinksScroll} onClick={stopCardInteraction} onMouseDown={stopCardInteraction}>
                {a.items.map((sub, i) => (
                    <SubLinkRow
                        key={`${sub.title}-${i}`}
                        sub={sub}
                        onActivate={() => handleSublinkActivate(sub)}
                    />
                ))}
            </Box>
        ),
    } as const;

    const renderLeafAddon = (addon: LinkCardLeafAddon, key: string) => {
        switch (addon.type) {
            case 'audioPlayer':
                return leafAddonRenderers.audioPlayer(addon, key);
            case 'sublinks':
                return leafAddonRenderers.sublinks(addon);
            default: {
                const _exhaustive: never = addon;
                return _exhaustive;
            }
        }
    };

    const addonRenderFactory = {
        audioPlayer: (addon: Extract<LinkCardAddon, { type: 'audioPlayer' }>) => renderLeafAddon(addon, addon.type),
        sublinks: (addon: Extract<LinkCardAddon, { type: 'sublinks' }>) => renderLeafAddon(addon, addon.type),
        composite: (addon: LinkCardCompositeAddon) => {
            switch (addon.layout) {
                case 'stack':
                    return (
                        <Box className={styles.addonStack} onClick={stopCardInteraction} onMouseDown={stopCardInteraction}>
                            {addon.addons.map((leaf, i) => renderLeafAddon(leaf, `${leaf.type}-${i}`))}
                        </Box>
                    );
                default: {
                    const _exhaustive: never = addon.layout;
                    return _exhaustive;
                }
            }
        },
    } satisfies AddonRendererMap;

    const renderAddon = (addon: LinkCardAddon | undefined) => {
        if (!addon) return null;
        switch (addon.type) {
            case 'audioPlayer':
                return addonRenderFactory.audioPlayer(addon);
            case 'sublinks':
                return addonRenderFactory.sublinks(addon);
            case 'composite':
                return addonRenderFactory.composite(addon);
            default: {
                const _exhaustive: never = addon;
                return _exhaustive;
            }
        }
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
                        className={isSplitLayout ? styles.descriptionCompact : styles.description}
                    >
                        {truncateDescription(link.description, isSplitLayout ? 48 : 60)}
                    </Typography>
                </Tooltip>
            )}

            {!isSplitLayout && renderAddon(link.addon)}
        </>
    );

    return (
        <>
            <Card
                className={`${styles.card} ${isSplitLayout ? styles.cardWithSublinks : ''} ${isHovered ? styles.cardHovered : ''}`}
                onClick={isSplitLayout ? undefined : handleCardClick}
                onMouseEnter={() => setIsHovered(true)}
                onMouseLeave={() => setIsHovered(false)}
                elevation={isHovered ? 4 : 1}
            >
                <MuiCardContent
                    className={isSplitLayout ? `${styles.cardContent} ${styles.cardContentSplit}` : styles.cardContent}
                >
                    {isSplitLayout ? (
                        <Box className={styles.splitRow}>
                            <Box className={styles.mainHalf} onClick={handleCardClick}>
                                {MainColumn}
                            </Box>
                            <Box className={styles.sublinksHalf}>
                                {sublinksAddon && leafAddonRenderers.sublinks(sublinksAddon)}
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
