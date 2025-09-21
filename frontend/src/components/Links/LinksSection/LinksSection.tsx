import { Box, Typography } from '@mui/material';
import { LinkCard } from '../LinkCard/LinkCard';
import type { LinksSectionProps } from '../../../types/link';
import styles from './LinksSection.module.css';

export function LinksSection({ links, onLinkClick, onChromeProfileClick }: LinksSectionProps) {
    const handleLinkClick = (link: any) => {
        window.open(link.url, '_blank');
        onLinkClick(link);
    };

    const handleChromeProfileClick = (link: any, profile: string) => {
        // For now, just open the link in a new tab
        // In the future, this could open with a specific Chrome profile
        console.log(`Opening ${link.title} with Chrome profile: ${profile}`);
        window.open(link.url, '_blank');
        if (onChromeProfileClick) {
            onChromeProfileClick(link, profile);
        }
    };

    const SectionHeader = (
        <Box className={styles.sectionHeader}>
            <Typography variant="h4" component="h2" className={styles.sectionTitle}>
                Quick Links
            </Typography>
        </Box>
    );

    const LinksGrid = (
        <Box className={styles.linksGrid}>
            {links.map((link, index) => (
                <Box key={index} className={styles.gridItem}>
                    <LinkCard
                        link={link}
                        onLinkClick={handleLinkClick}
                        onChromeProfileClick={handleChromeProfileClick}
                    />
                </Box>
            ))}
        </Box>
    );

    return (
        <Box className={styles.linksSection}>
            {SectionHeader}
            {LinksGrid}
        </Box>
    );
}
