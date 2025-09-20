import { Box, Container } from '@mui/material';
import { SearchComponent } from '../Search';
import { AppHookDebugger } from '../shared';
import type { SearchEngineStrategy } from '../Search/SearchEngineStrategy';
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

  const SearchSection = (
    <Box className={styles.searchSection}>
      <SearchComponent
        onSearch={handleSearch}
        onSearchNewTab={handleSearchNewTab}
      />
    </Box>
  );


  return (
    <Box className={styles.homepageContainer}>
      <Container maxWidth="xl" className={styles.searchContainer}>
        {SearchSection}
      </Container>

      <AppHookDebugger
        defaultVisible={false}
        defaultExpanded={false}
        title="App Hook Debugger"
        position="bottom-right"
      />
    </Box>
  );
}
