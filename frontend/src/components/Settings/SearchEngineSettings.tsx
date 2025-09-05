import React, { useState, useEffect } from 'react';
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
import { searchEngineManager, type SearchEngineStrategy } from '../Search/SearchEngineStrategy';
import styles from './SearchEngineSettings.module.css';

const SEARCH_ENGINE_KEY = 'selectedSearchEngine';

export const SearchEngineSettings: React.FC = () => {
    const [selectedEngine, setSelectedEngine] = useState<string>('google');
    const [availableEngines, setAvailableEngines] = useState<SearchEngineStrategy[]>([]);

    useEffect(() => {
        // Load available search engines
        const engines = searchEngineManager.getAllStrategies();
        setAvailableEngines(engines);

        // Load saved preference
        const savedEngine = localStorage.getItem(SEARCH_ENGINE_KEY);
        if (savedEngine && engines.find(engine => engine.name.toLowerCase() === savedEngine)) {
            setSelectedEngine(savedEngine);
        }
    }, []);

    const handleEngineChange = (event: any) => {
        const newEngine = event.target.value;
        setSelectedEngine(newEngine);
        localStorage.setItem(SEARCH_ENGINE_KEY, newEngine);
    };

    const getCurrentEngine = (): SearchEngineStrategy => {
        return searchEngineManager.getStrategy(selectedEngine);
    };

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
                            value={selectedEngine}
                            onChange={handleEngineChange}
                            label="Default Search Engine"
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
                                {engine.name.toLowerCase() === selectedEngine && (
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
