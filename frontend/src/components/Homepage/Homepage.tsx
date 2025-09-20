import { Box, Container, Typography } from '@mui/material';
import { SearchComponent } from '../Search';
import { LinkCard } from '../shared';
import { useChromeProfiles } from '../../hooks';
import type { SearchEngineStrategy } from '../Search/SearchEngineStrategy';
import type { ChromeProfile } from '../../hooks/useChromeProfiles';
import { createLinkItem } from '../../types/linkCard';
import { commonLinksData } from '../shared/LinkCard/commonLinksData';
import styles from './Homepage.module.css';

interface HomepageProps {
  // Add props as needed for the new design
}

// Generate LinkItems with auto-generated IDs for each row
const commonLinksRows = commonLinksData.map(row => row.map(createLinkItem));

export function Homepage({ }: HomepageProps) {
  const { profiles: chromeProfiles, openUrlInProfile } = useChromeProfiles();

  const handleSearch = (query: string, engine: SearchEngineStrategy) => {
    const searchUrl = engine.buildSearchUrl(query);
    window.location.href = searchUrl;
  };

  const handleSearchNewTab = (query: string, engine: SearchEngineStrategy) => {
    const searchUrl = engine.buildSearchUrl(query);
    window.open(searchUrl, '_blank');
  };

  const handleOpenInProfile = async (url: string, profile: ChromeProfile) => {
    try {
      const response = await openUrlInProfile({
        url,
        profile_id: profile.id,
      });

      if (response.success) {
        console.log(`Successfully opened ${url} in profile: ${profile.name}`);
      } else {
        console.error('Failed to open URL in profile:', response.message);
      }
    } catch (err) {
      console.error('Error opening URL in profile:', err);
    }
  };

  const SearchSection = (
    <Box className={styles.searchSection}>
      <SearchComponent
        onSearch={handleSearch}
        onSearchNewTab={handleSearchNewTab}
      />
    </Box>
  );

  const CommonLinksSection = (
    <Box className={styles.commonLinksSection}>
      <Typography variant="h4" component="h2" className={styles.sectionTitle}>
        Quick Access
      </Typography>
      <Typography variant="body1" className={styles.sectionDescription}>
        Your most frequently used links
      </Typography>

      <Box className={styles.linksGrid}>
        {commonLinksRows.map((row, rowIndex) => (
          <Box key={rowIndex} className={styles.linksRow}>
            {row.map((link) => (
              <Box key={link.id} className={styles.linkItem}>
                <LinkCard
                  {...link}
                  chromeProfiles={chromeProfiles}
                  onOpenInProfile={handleOpenInProfile}
                />
              </Box>
            ))}
          </Box>
        ))}
      </Box>
    </Box>
  );

  return (
    <Container maxWidth="xl" className={styles.container}>
      {SearchSection}
      {CommonLinksSection}
    </Container>
  );
}
