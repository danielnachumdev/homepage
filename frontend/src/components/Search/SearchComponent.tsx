import React, { useState } from 'react';
import {
    Box,
    TextField,
    Button,
    InputAdornment,
    IconButton,
    Menu,
    MenuItem,
    ListItemIcon,
    ListItemText,
    Typography,
    Paper,
} from '@mui/material';
import {
    Search as SearchIcon,
    OpenInNew as OpenInNewIcon,
    ArrowDropDown as ArrowDropDownIcon,
} from '@mui/icons-material';
import { searchEngineManager, type SearchEngineStrategy } from './SearchEngineStrategy';
import styles from './SearchComponent.module.css';

interface SearchComponentProps {
    onSearch?: (query: string, engine: SearchEngineStrategy) => void;
    onSearchNewTab?: (query: string, engine: SearchEngineStrategy) => void;
}

export const SearchComponent: React.FC<SearchComponentProps> = ({
    onSearch,
    onSearchNewTab,
}) => {
    const [query, setQuery] = useState('');
    const [selectedEngine, setSelectedEngine] = useState<SearchEngineStrategy>(
        searchEngineManager.getDefaultStrategy()
    );
    const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
    const [isFocused, setIsFocused] = useState(false);

    const availableEngines = searchEngineManager.getAllStrategies();

    const handleSearch = () => {
        if (query.trim()) {
            if (onSearch) {
                onSearch(query.trim(), selectedEngine);
            } else {
                // Default behavior: open in current tab
                const searchUrl = selectedEngine.buildSearchUrl(query.trim());
                window.location.href = searchUrl;
            }
        }
    };

    const handleSearchNewTab = () => {
        if (query.trim()) {
            if (onSearchNewTab) {
                onSearchNewTab(query.trim(), selectedEngine);
            } else {
                // Default behavior: open in new tab
                const searchUrl = selectedEngine.buildSearchUrl(query.trim());
                window.open(searchUrl, '_blank');
            }
        }
    };

    const handleKeyPress = (event: React.KeyboardEvent) => {
        if (event.key === 'Enter') {
            handleSearch();
        }
    };

    const handleEngineSelect = (engine: SearchEngineStrategy) => {
        setSelectedEngine(engine);
        setAnchorEl(null);
    };

    const handleMenuOpen = (event: React.MouseEvent<HTMLElement>) => {
        setAnchorEl(event.currentTarget);
    };

    const handleMenuClose = () => {
        setAnchorEl(null);
    };

    return (
        <Box className={styles.searchContainer}>
            <Paper elevation={isFocused ? 8 : 2} className={styles.searchBox}>
                <TextField
                    fullWidth
                    placeholder={`Search with ${selectedEngine.name}...`}
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    onKeyPress={handleKeyPress}
                    onFocus={() => setIsFocused(true)}
                    onBlur={() => setIsFocused(false)}
                    InputProps={{
                        startAdornment: (
                            <InputAdornment position="start">
                                <SearchIcon className={styles.searchIcon} />
                            </InputAdornment>
                        ),
                        endAdornment: (
                            <InputAdornment position="end">
                                <Box className={styles.endAdornment}>
                                    <img
                                        src={selectedEngine.logo}
                                        alt={selectedEngine.name}
                                        className={styles.engineLogo}
                                        onError={(e) => {
                                            // Fallback to a default icon if the favicon fails to load
                                            e.currentTarget.style.display = 'none';
                                        }}
                                    />
                                    <IconButton
                                        size="small"
                                        onClick={handleMenuOpen}
                                        className={styles.engineSelector}
                                    >
                                        <ArrowDropDownIcon />
                                    </IconButton>
                                </Box>
                            </InputAdornment>
                        ),
                    }}
                    className={styles.searchInput}
                />
            </Paper>

            <Box className={styles.searchButtons}>
                <Button
                    variant="contained"
                    startIcon={<SearchIcon />}
                    onClick={handleSearch}
                    disabled={!query.trim()}
                    className={styles.searchButton}
                >
                    Search
                </Button>
                <Button
                    variant="outlined"
                    startIcon={<OpenInNewIcon />}
                    onClick={handleSearchNewTab}
                    disabled={!query.trim()}
                    className={styles.searchButton}
                >
                    Search - New Tab
                </Button>
            </Box>

            <Menu
                anchorEl={anchorEl}
                open={Boolean(anchorEl)}
                onClose={handleMenuClose}
                className={styles.engineMenu}
            >
                {availableEngines.map((engine) => (
                    <MenuItem
                        key={engine.name}
                        onClick={() => handleEngineSelect(engine)}
                        selected={engine.name === selectedEngine.name}
                    >
                        <ListItemIcon>
                            <img
                                src={engine.logo}
                                alt={engine.name}
                                className={styles.menuEngineLogo}
                                onError={(e) => {
                                    e.currentTarget.style.display = 'none';
                                }}
                            />
                        </ListItemIcon>
                        <ListItemText>
                            <Typography variant="body2">{engine.name}</Typography>
                        </ListItemText>
                    </MenuItem>
                ))}
            </Menu>
        </Box>
    );
};
