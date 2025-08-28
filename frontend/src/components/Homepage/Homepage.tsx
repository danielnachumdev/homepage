import React, { useState, useEffect } from 'react';
import {
  Box,
  Container,
  Card,
  CardContent,
  Typography,
  IconButton,
  Collapse,
  Button,
  TextField,
  InputAdornment,
  Alert,
  CircularProgress,
  Chip,
} from '@mui/material';
import {
  ExpandMore,
  ExpandLess,
  MoreVert,
  Search,
  Link as LinkIcon,
  Tag,
} from '@mui/icons-material';
import type { Section, LinkItem } from '../../types/homepage';
import { chromeService } from '../../services';
import type { ChromeProfile } from '../../services';
import { useChromeProfiles } from '../../hooks';
import { ProfileMenu } from '../shared';
import styles from './Homepage.module.css';

interface HomepageProps {
  data?: {
    sections: Section[];
  };
}

// Demo sections data for demonstration
const demoSections: Section[] = [
  {
    id: 'work',
    title: 'Work & Productivity',
    description: 'Essential tools for daily work',
    links: [
      {
        id: 'gmail',
        title: 'Gmail',
        url: 'https://mail.google.com',
        description: 'Email and communication',
        category: 'communication',
        tags: ['email', 'google'],
      },
      {
        id: 'calendar',
        title: 'Google Calendar',
        url: 'https://calendar.google.com',
        description: 'Schedule management',
        category: 'productivity',
        tags: ['calendar', 'google'],
      },
      {
        id: 'drive',
        title: 'Google Drive',
        url: 'https://drive.google.com',
        description: 'File storage and sharing',
        category: 'storage',
        tags: ['files', 'google'],
      },
    ],
    isCollapsible: true,
    isCollapsed: false,
  },
  {
    id: 'development',
    title: 'Development Tools',
    description: 'Coding and development resources',
    links: [
      {
        id: 'github',
        title: 'GitHub',
        url: 'https://github.com',
        description: 'Code repository and collaboration',
        category: 'coding',
        tags: ['git', 'code'],
      },
      {
        id: 'stackoverflow',
        title: 'Stack Overflow',
        url: 'https://stackoverflow.com',
        description: 'Programming Q&A',
        category: 'coding',
        tags: ['help', 'programming'],
      },
    ],
    isCollapsible: true,
    isCollapsed: false,
  },
  {
    id: 'entertainment',
    title: 'Entertainment',
    description: 'Fun and relaxation',
    links: [
      {
        id: 'youtube',
        title: 'YouTube',
        url: 'https://youtube.com',
        description: 'Video streaming',
        category: 'videos',
        tags: ['videos', 'streaming'],
      },
      {
        id: 'spotify',
        title: 'Spotify',
        url: 'https://open.spotify.com',
        description: 'Music streaming',
        category: 'music',
        tags: ['music', 'streaming'],
      },
    ],
    isCollapsible: true,
    isCollapsed: false,
  },
];

export function Homepage({ data }: HomepageProps) {
  const [sections, setSections] = useState<Section[]>(data?.sections || demoSections);
  const [searchTerm, setSearchTerm] = useState('');
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const [selectedLink, setSelectedLink] = useState<LinkItem | null>(null);

  // Use the useChromeProfiles hook
  const { profiles: chromeProfiles, loading, error, loadChromeProfiles } = useChromeProfiles();

  // Load Chrome profiles on component mount
  useEffect(() => {
    loadChromeProfiles();
  }, [loadChromeProfiles]);

  const handleSectionToggle = (sectionId: string) => {
    setSections(prev =>
      prev.map(section =>
        section.id === sectionId
          ? { ...section, isCollapsed: !section.isCollapsed }
          : section
      )
    );
  };

  const handleProfileMenuOpen = (event: React.MouseEvent<HTMLElement>, link: LinkItem) => {
    setAnchorEl(event.currentTarget);
    setSelectedLink(link);
  };

  const handleProfileMenuClose = () => {
    setAnchorEl(null);
    setSelectedLink(null);
  };

  const handleProfileSelect = async (profile: ChromeProfile) => {
    if (selectedLink) {
      try {
        const response = await chromeService.openUrlInProfile({
          url: selectedLink.url,
          profile_id: profile.id,
        });

        if (response.success) {
          console.log(`Successfully opened ${selectedLink.url} in profile: ${profile.name}`);
        } else {
          console.error('Failed to open URL in profile:', response.message);
        }
      } catch (err) {
        console.error('Error opening URL in profile:', err);
      }
    }
    handleProfileMenuClose();
  };

  const filteredSections = sections.map(section => ({
    ...section,
    links: section.links.filter(link =>
      link.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
      link.description?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      link.tags?.some(tag => tag.toLowerCase().includes(searchTerm.toLowerCase()))
    ),
  })).filter(section => section.links.length > 0);

  const SectionHeader = ({ section }: { section: Section }) => (
    <Box className={styles.sectionHeader}>
      <Typography variant="h5" component="h2" className={styles.sectionTitle}>
        {section.title}
      </Typography>
      {section.isCollapsible && (
        <IconButton
          onClick={() => handleSectionToggle(section.id)}
          size="small"
        >
          {section.isCollapsed ? <ExpandMore /> : <ExpandLess />}
        </IconButton>
      )}
    </Box>
  );

  const LinkCard = ({ link }: { link: LinkItem }) => (
    <Card className={styles.linkCard}>
      <CardContent className={styles.linkCardContent}>
        <Box className={styles.linkHeader}>
          <Box className={styles.linkInfo}>
            <Typography variant="h6" component="h3" className={styles.linkTitle}>
              {link.title}
            </Typography>
            {link.description && (
              <Typography variant="body2" className={styles.linkDescription}>
                {link.description}
              </Typography>
            )}
            <Box className={styles.linkTags}>
              {link.tags?.map(tag => (
                <Chip
                  key={tag}
                  label={tag}
                  size="small"
                  variant="outlined"
                  icon={<Tag />}
                />
              ))}
            </Box>
          </Box>
          <IconButton
            size="small"
            onClick={(e) => handleProfileMenuOpen(e, link)}
            className={styles.linkMenuButton}
            disabled={chromeProfiles.length === 0}
          >
            <MoreVert />
          </IconButton>
        </Box>
        <Button
          variant="contained"
          size="small"
          startIcon={<LinkIcon />}
          onClick={() => window.open(link.url, '_blank')}
          className={styles.linkButton}
        >
          Open Link
        </Button>
      </CardContent>
    </Card>
  );

  const SearchBar = (
    <Box className={styles.searchSection}>
      <TextField
        fullWidth
        placeholder="Search links, descriptions, or tags..."
        value={searchTerm}
        onChange={(e) => setSearchTerm(e.target.value)}
        InputProps={{
          startAdornment: (
            <InputAdornment position="start">
              <Search />
            </InputAdornment>
          ),
        }}
        className={styles.searchField}
      />
    </Box>
  );

  const ChromeProfilesStatus = (
    <Box className={styles.chromeProfilesStatus}>
      {loading && (
        <Box className={styles.loadingContainer}>
          <CircularProgress size={16} />
          <Typography variant="body2">Loading Chrome profiles...</Typography>
        </Box>
      )}
      {error && (
        <Alert severity="warning" className={styles.errorAlert}>
          {error}
        </Alert>
      )}
      {chromeProfiles.length > 0 && (
        <Box className={styles.profilesInfo}>
          <Typography variant="body2" color="text.secondary">
            Chrome profiles available: {chromeProfiles.length}
          </Typography>
          <Button size="small" onClick={loadChromeProfiles}>
            Refresh
          </Button>
        </Box>
      )}
    </Box>
  );

  return (
    <Container maxWidth="xl" className={styles.container}>
      {SearchBar}
      {ChromeProfilesStatus}

      <Box className={styles.mainContent}>
        <Box className={styles.sectionsContainer}>
          {filteredSections.map(section => (
            <Box key={section.id}>
              <Card className={styles.sectionCard}>
                <SectionHeader section={section} />

                <Collapse in={!section.isCollapsed}>
                  <Box className={styles.linksGrid}>
                    {section.links.map(link => (
                      <Box key={link.id}>
                        <LinkCard link={link} />
                      </Box>
                    ))}
                  </Box>
                </Collapse>
              </Card>
            </Box>
          ))}
        </Box>
      </Box>

      <ProfileMenu
        anchorEl={anchorEl}
        open={Boolean(anchorEl)}
        onClose={handleProfileMenuClose}
        profiles={chromeProfiles}
        onProfileSelect={handleProfileSelect}
        title="Open with profile:"
      />
    </Container>
  );
}
