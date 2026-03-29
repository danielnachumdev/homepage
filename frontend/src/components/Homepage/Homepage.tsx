import { Box, Container } from '@mui/material';
import { SearchComponent } from '../Search';
import { LinksSection } from '../Links';
import { links } from '../../data/links';
import { useComponentLogger } from '../../hooks/useLogger';
import type { SearchEngineStrategy } from '../Search/SearchEngineStrategy';
import type { LinkData, LinkSubItem } from '../../types/link';
import styles from './Homepage.module.css';

interface HomepageProps {
  // Add props as needed for the new design
}

export function Homepage({ }: HomepageProps) {
  const logger = useComponentLogger('Homepage');

  logger.debug('Component render started');

  const handleSearch = (query: string, engine: SearchEngineStrategy) => {
    logger.info('Search triggered', {
      query,
      engine: engine.name,
      timestamp: new Date().toISOString()
    });
    const searchUrl = engine.buildSearchUrl(query);
    window.location.href = searchUrl;
  };

  const handleSearchNewTab = (query: string, engine: SearchEngineStrategy) => {
    logger.info('Search in new tab triggered', {
      query,
      engine: engine.name,
      timestamp: new Date().toISOString()
    });
    const searchUrl = engine.buildSearchUrl(query);
    window.open(searchUrl, '_blank');
  };

  const handleLinkClick = (link: LinkData) => {
    logger.info('Link clicked', {
      title: link.title,
      url: link.url,
      timestamp: new Date().toISOString()
    });
  };

  const handleChromeProfileClick = (link: LinkData, profile: string) => {
    logger.info('Chrome profile clicked', {
      title: link.title,
      profile,
      url: link.url,
      timestamp: new Date().toISOString()
    });
  };

  const handleSublinkClick = (parent: LinkData, sub: LinkSubItem) => {
    logger.info('Sublink clicked', {
      parentTitle: parent.title,
      title: sub.title,
      url: sub.url,
      timestamp: new Date().toISOString()
    });
  };

  const SearchSection = (
    <Box className={styles.searchSection}>
      <SearchComponent
        onSearch={handleSearch}
        onSearchNewTab={handleSearchNewTab}
      />
    </Box>
  );

  const LinksSectionComponent = (
    <Box className={styles.linksSection}>
      <LinksSection
        links={links}
        onLinkClick={handleLinkClick}
        onChromeProfileClick={handleChromeProfileClick}
        onSublinkClick={handleSublinkClick}
      />
    </Box>
  );

  return (
    <Box className={styles.homepageContainer}>
      <Container maxWidth="xl" className={styles.searchContainer}>
        {SearchSection}
      </Container>

      {LinksSectionComponent}

    </Box>
  );
}
