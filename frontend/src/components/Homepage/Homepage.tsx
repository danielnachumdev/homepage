import { Box, Container, Typography } from '@mui/material';
import { SearchComponent } from '../Search';
import { LinkCard } from '../shared';
import { useChromeProfiles } from '../../hooks';
import type { SearchEngineStrategy } from '../Search/SearchEngineStrategy';
import type { ChromeProfile } from '../../hooks/useChromeProfiles';
import type { LinkData } from '../../types/linkCard';
import { createLinkItem } from '../../types/linkCard';
import styles from './Homepage.module.css';

interface HomepageProps {
  // Add props as needed for the new design
}

// Common links data (without IDs - they will be auto-generated)
const commonLinksData: LinkData[] = [
  {
    title: 'YouTube Subscriptions',
    url: 'https://www.youtube.com/feed/subscriptions',
    description: 'View your YouTube subscriptions and latest videos',
    icon: 'https://www.youtube.com/favicon.ico',
    category: 'Entertainment',
  },
  {
    title: 'YouTube Studio',
    url: 'https://studio.youtube.com/channel/UCauGG97chgNr-BwoQpKTytg',
    description: 'Manage your YouTube channel and content',
    icon: 'https://www.youtube.com/favicon.ico',
    category: 'Content Creation',
  },
  {
    title: 'GitHub Repositories',
    url: 'https://github.com/danielnachumdev?tab=repositories',
    description: 'View your GitHub repositories and projects',
    icon: 'https://github.com/favicon.ico',
    category: 'Development',
  },
];

// Generate LinkItems with auto-generated IDs
const commonLinks = commonLinksData.map(createLinkItem);

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
        {commonLinks.map((link) => (
          <Box key={link.id} className={styles.linkItem}>
            <LinkCard
              {...link}
              chromeProfiles={chromeProfiles}
              onOpenInProfile={handleOpenInProfile}
            />
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
