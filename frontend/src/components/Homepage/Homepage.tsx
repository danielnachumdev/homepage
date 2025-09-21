import { Box, Container } from '@mui/material';
import { SearchComponent } from '../Search';
import { AppHookDebugger } from '../shared';
import { LinksSection } from '../Links';
import { links } from '../../data/links';
import type { SearchEngineStrategy } from '../Search/SearchEngineStrategy';
import type { LinkData } from '../../types/link';
import styles from './Homepage.module.css';

interface HomepageProps {
  // Add props as needed for the new design
}

export function Homepage({ }: HomepageProps) {
  const handleSearch = (query: string, engine: SearchEngineStrategy) => {
    const searchUrl = engine.buildSearchUrl(query);
    window.location.href = searchUrl;
  };

  const handleSearchNewTab = (query: string, engine: SearchEngineStrategy) => {
    const searchUrl = engine.buildSearchUrl(query);
    window.open(searchUrl, '_blank');
  };

  const handleLinkClick = (link: LinkData) => {
    console.log('Link clicked:', link.title);
  };

  const handleChromeProfileClick = (link: LinkData, profile: string) => {
    console.log(`Chrome profile clicked: ${link.title} - ${profile}`);
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
      />
    </Box>
  );


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
