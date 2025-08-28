import React, { useState, useEffect } from 'react';
import {
  Box,
  Container,
  Grid,
  Card,
  CardContent,
  Typography,
  IconButton,
  Menu,
  MenuItem,
  Chip,
  Collapse,
  Button,
  TextField,
  InputAdornment,
  Alert,
  CircularProgress,
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
import { chromeApiService } from '../../lib/api/chrome';
import type { ChromeProfile } from '../../lib/api/chrome';

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
  const [chromeProfiles, setChromeProfiles] = useState<ChromeProfile[]>([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const [selectedLink, setSelectedLink] = useState<LinkItem | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Load Chrome profiles on component mount
  useEffect(() => {
    loadChromeProfiles();
  }, []);

  const loadChromeProfiles = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await chromeApiService.getChromeProfiles();
      if (response.success) {
        setChromeProfiles(response.profiles);
      } else {
        setError(response.message || 'Failed to load Chrome profiles');
      }
    } catch (err) {
      setError('Failed to connect to backend for Chrome profiles');
      console.error('Error loading Chrome profiles:', err);
    } finally {
      setLoading(false);
    }
  };

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
        const response = await chromeApiService.openUrlInProfile({
          url: selectedLink.url,
          profile_id: profile.id,
        });

        if (response.success) {
          console.log(`Successfully opened ${selectedLink.url} in profile: ${profile.name}`);
        } else {
          console.error('Failed to open URL in profile:', response.message);
          setError(`Failed to open URL in profile: ${response.message}`);
        }
      } catch (err) {
        console.error('Error opening URL in profile:', err);
        setError('Failed to communicate with backend');
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
    <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
      <Typography variant="h5" component="h2" sx={{ flexGrow: 1 }}>
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
    <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <CardContent sx={{ flexGrow: 1, p: 2 }}>
        <Box sx={{ display: 'flex', alignItems: 'flex-start', mb: 1 }}>
          <Box sx={{ flexGrow: 1 }}>
            <Typography variant="h6" component="h3" gutterBottom>
              {link.title}
            </Typography>
            {link.description && (
              <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                {link.description}
              </Typography>
            )}
            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5, mb: 1 }}>
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
            sx={{ ml: 1 }}
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
          fullWidth
        >
          Open Link
        </Button>
      </CardContent>
    </Card>
  );

  const SearchBar = (
    <Box sx={{ mb: 4 }}>
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
        sx={{ maxWidth: 600 }}
      />
    </Box>
  );

  const ChromeProfilesStatus = (
    <Box sx={{ mb: 3 }}>
      {loading && (
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <CircularProgress size={16} />
          <Typography variant="body2">Loading Chrome profiles...</Typography>
        </Box>
      )}
      {error && (
        <Alert severity="warning" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}
      {chromeProfiles.length > 0 && (
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
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

  const ProfileMenu = (
    <Menu
      anchorEl={anchorEl}
      open={Boolean(anchorEl)}
      onClose={handleProfileMenuClose}
    >
      <MenuItem disabled>
        <Typography variant="subtitle2">Open with profile:</Typography>
      </MenuItem>
      {chromeProfiles.map(profile => (
        <MenuItem
          key={profile.id}
          onClick={() => handleProfileSelect(profile)}
          selected={profile.is_active}
        >
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <span>{profile.icon || '👤'}</span>
            <Typography>{profile.name}</Typography>
            {profile.is_active && (
              <Chip label="Active" size="small" color="primary" />
            )}
          </Box>
        </MenuItem>
      ))}
    </Menu>
  );

  return (
    <Container maxWidth="xl" sx={{ py: 4 }}>
      {SearchBar}
      {ChromeProfilesStatus}

      <Box sx={{ mt: 4 }}>
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
          {filteredSections.map(section => (
            <Box key={section.id}>
              <Card sx={{ p: 3 }}>
                <SectionHeader section={section} />

                <Collapse in={!section.isCollapsed}>
                  <Box sx={{
                    display: 'grid',
                    gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))',
                    gap: 2
                  }}>
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

      {ProfileMenu}
    </Container>
  );
}
