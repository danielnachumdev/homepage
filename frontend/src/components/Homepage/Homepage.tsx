import { Box, Container } from '@mui/material';
import { SearchComponent } from '../Search';
import { AppHookDebugger } from '../shared';
import { LinksSection } from '../Links';
import { links } from '../../data/links';
import { useComponentLogger } from '../../hooks/useLogger';
import type { SearchEngineStrategy } from '../Search/SearchEngineStrategy';
import type { LinkData } from '../../types/link';
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

  const SearchSection = (
    <Box className={styles.searchSection}>
      <SearchComponent
        onSearch={handleSearch}
        onSearchNewTab={handleSearchNewTab}
      />
    </Box>
  );

  logger.debug('SearchSection created');

  const LinksSectionComponent = (
    <Box className={styles.linksSection}>
      <LinksSection
        links={links}
        onLinkClick={handleLinkClick}
        onChromeProfileClick={handleChromeProfileClick}
      />
    </Box>
  );

  logger.debug('LinksSectionComponent created');

  logger.debug('Rendering component');

  return (
    <Box className={styles.homepageContainer}>
      <Container maxWidth="xl" className={styles.searchContainer}>
        {SearchSection}
      </Container>

      {LinksSectionComponent}

      <AppHookDebugger
        defaultVisible={false}
        defaultExpanded={false}
        title="App Hook Debugger"
        position="bottom-right"
      />
    </Box>
  );
}
