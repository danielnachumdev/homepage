import { Box } from '@mui/material';
import { LinkCard } from '../LinkCard/LinkCard';
import { useScreenSize } from '../../../hooks/useScreenSize';
import { useLinkCardSize } from '../../../hooks/useLinkCardSize';
import type { LinkItem } from '../../../types/linkCard';
import type { ChromeProfile } from '../../../hooks/useChromeProfiles';
import smallStyles from './LinkCardGrid.small.module.css';
import mediumStyles from './LinkCardGrid.medium.module.css';
import largeStyles from './LinkCardGrid.large.module.css';

export interface LinkCardGridProps {
    links: LinkItem[][];
    chromeProfiles?: ChromeProfile[];
    onOpenInProfile?: (url: string, profile: ChromeProfile) => Promise<void>;
}

export function LinkCardGrid({
    links,
    chromeProfiles = [],
    onOpenInProfile,
}: LinkCardGridProps) {
    const { isMobile, isTablet, isDesktop } = useScreenSize();
    const cardSize = useLinkCardSize();

    // Determine which styles to use based on screen size
    const getStyles = () => {
        if (isMobile) return smallStyles;
        if (isTablet) return mediumStyles;
        if (isDesktop) return largeStyles;
        return mediumStyles;
    };

    const styles = getStyles();

    return (
        <Box className={styles.linkCardGrid}>
            {links.map((row, rowIndex) => (
                <Box key={rowIndex} className={styles.linksRow}>
                    {row.map((link) => (
                        <Box key={link.id} className={styles.linkItem}>
                            <LinkCard
                                {...link}
                                chromeProfiles={chromeProfiles}
                                onOpenInProfile={onOpenInProfile}
                                size={cardSize}
                            />
                        </Box>
                    ))}
                </Box>
            ))}
        </Box>
    );
}
