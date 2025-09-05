import React, { useState } from 'react';
import {
    Box,
    Typography,
    FormControl,
    InputLabel,
    Select,
    MenuItem,
    FormHelperText,
    Card,
    CardContent,
    List,
    ListItem,
    ListItemIcon,
    ListItemText,
    Chip,
} from '@mui/material';
import type { SearchEngineStrategy } from '../Search/SearchEngineStrategy';
import { useSearchEngine } from '../../hooks/useSearchEngine';
import styles from './SearchEngineSettings.module.css';

interface SearchEngineSettingsProps {
    onProfilesRefresh?: () => void;
}

export const SearchEngineSettings: React.FC<SearchEngineSettingsProps> = () => {
    const { selectedEngine, availableEngines, setSelectedEngine, loading, error } = useSearchEngine();
    const [updating, setUpdating] = useState(false);

    const handleEngineChange = async (event: any) => {
        const newEngine = event.target.value;
        setUpdating(true);

        try {
            await setSelectedEngine(newEngine);
        } catch (error) {
            console.error('Failed to save search engine setting:', error);
        } finally {
            setUpdating(false);
        }
    };

    const getCurrentEngine = (): SearchEngineStrategy => {
        return selectedEngine;
    };

    if (loading) {
        return (
            <Box className={styles.container}>
                <Typography variant="body1" sx={{ color: 'rgba(255, 255, 255, 0.7)' }}>
                    Loading search engine settings...
                </Typography>
            </Box>
        );
    }

    if (error) {
        return (
            <Box className={styles.container}>
                <Typography variant="body1" sx={{ color: 'rgba(255, 255, 255, 0.7)' }}>
                    Error: {error}
                </Typography>
            </Box>
        );
    }

    return (
        <Box className={styles.container}>
            <Typography variant="h6" className={styles.title}>
                Search Engine Settings
            </Typography>

            <Typography variant="body2" className={styles.description}>
                Choose your preferred search engine for internet searches. This will be used as the default
                search engine in the search component on the homepage.
            </Typography>

            <Card className={styles.settingsCard}>
                <CardContent>
                    <FormControl fullWidth className={styles.formControl}>
                        <InputLabel id="search-engine-label">Default Search Engine</InputLabel>
                        <Select
                            labelId="search-engine-label"
                            value={selectedEngine.name.toLowerCase()}
                            onChange={handleEngineChange}
                            label="Default Search Engine"
                            disabled={updating}
                        >
                            {availableEngines.map((engine) => (
                                <MenuItem key={engine.name.toLowerCase()} value={engine.name.toLowerCase()}>
                                    <Box className={styles.menuItem}>
                                        <img
                                            src={engine.logo}
                                            alt={engine.name}
                                            className={styles.engineLogo}
                                            onError={(e) => {
                                                e.currentTarget.style.display = 'none';
                                            }}
                                        />
                                        <Typography variant="body1" className={styles.engineName}>
                                            {engine.name}
                                        </Typography>
                                    </Box>
                                </MenuItem>
                            ))}
                        </Select>
                        <FormHelperText>
                            This search engine will be used by default for all searches
                        </FormHelperText>
                    </FormControl>
                </CardContent>
            </Card>

            <Card className={styles.previewCard}>
                <CardContent>
                    <Typography variant="h6" className={styles.previewTitle}>
                        Preview
                    </Typography>
                    <Typography variant="body2" className={styles.previewDescription}>
                        Current search engine: <strong>{getCurrentEngine().name}</strong>
                    </Typography>

                    <Box className={styles.engineInfo}>
                        <img
                            src={getCurrentEngine().logo}
                            alt={getCurrentEngine().name}
                            className={styles.previewLogo}
                            onError={(e) => {
                                e.currentTarget.style.display = 'none';
                            }}
                        />
                        <Box className={styles.engineDetails}>
                            <Typography variant="body1" className={styles.engineName}>
                                {getCurrentEngine().name}
                            </Typography>
                            <Typography variant="body2" className={styles.engineUrl}>
                                {getCurrentEngine().buildSearchUrl('example query')}
                            </Typography>
                        </Box>
                    </Box>
                </CardContent>
            </Card>

            <Card className={styles.availableEnginesCard}>
                <CardContent>
                    <Typography variant="h6" className={styles.availableTitle}>
                        Available Search Engines
                    </Typography>
                    <List className={styles.enginesList}>
                        {availableEngines.map((engine) => (
                            <ListItem key={engine.name} className={styles.engineListItem}>
                                <ListItemIcon>
                                    <img
                                        src={engine.logo}
                                        alt={engine.name}
                                        className={styles.listEngineLogo}
                                        onError={(e) => {
                                            e.currentTarget.style.display = 'none';
                                        }}
                                    />
                                </ListItemIcon>
                                <ListItemText
                                    primary={engine.name}
                                    secondary={`Search URL: ${engine.buildSearchUrl('query')}`}
                                />
                                {engine.name.toLowerCase() === selectedEngine.name.toLowerCase() && (
                                    <Chip
                                        label="Selected"
                                        color="primary"
                                        size="small"
                                        className={styles.selectedChip}
                                    />
                                )}
                            </ListItem>
                        ))}
                    </List>
                </CardContent>
            </Card>
        </Box>
    );
};
