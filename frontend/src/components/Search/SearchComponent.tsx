import React, { useState, useRef, useEffect } from 'react';
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
    ButtonGroup,
} from '@mui/material';
import {
    Search as SearchIcon,
    OpenInNew as OpenInNewIcon,
    ArrowDropDown as ArrowDropDownIcon,
} from '@mui/icons-material';
import type { SearchEngineStrategy } from './SearchEngineStrategy';
import { useSearchEngine, useFocus } from '../../hooks';
import styles from './SearchComponent.module.css';

interface SearchComponentProps {
    onSearch?: (query: string, engine: SearchEngineStrategy) => void;
    onSearchNewTab?: (query: string, engine: SearchEngineStrategy) => void;
}

type SearchMode = 'current' | 'newTab';

export const SearchComponent: React.FC<SearchComponentProps> = ({
    onSearch,
    onSearchNewTab,
}) => {
    const { selectedEngine, availableEngines, setSelectedEngine } = useSearchEngine();
    const focus = useFocus();
    const [query, setQuery] = useState('');
    const [engineMenuAnchor, setEngineMenuAnchor] = useState<null | HTMLElement>(null);
    const [modeMenuAnchor, setModeMenuAnchor] = useState<null | HTMLElement>(null);
    const [searchMode, setSearchMode] = useState<SearchMode>('newTab');
    const [isFocused, setIsFocused] = useState(false);
    const searchInputRef = useRef<HTMLInputElement>(null);
    const hasInitiallyFocused = useRef(false);

    // Auto-focus the search input when component mounts
    useEffect(() => {
        if (!hasInitiallyFocused.current) {
            // Use setTimeout to ensure the DOM is fully rendered
            const focusTimeout = setTimeout(() => {
                focus(searchInputRef.current);
                hasInitiallyFocused.current = true;
            }, 100);

            return () => clearTimeout(focusTimeout);
        }
    }, []); // Empty dependency array - only run once on mount

    // Re-focus when selectedEngine changes (in case it affects input readiness)
    useEffect(() => {
        if (searchInputRef.current && !isFocused && hasInitiallyFocused.current) {
            const focusTimeout = setTimeout(() => {
                focus(searchInputRef.current);
            }, 50);

            return () => clearTimeout(focusTimeout);
        }
    }, [selectedEngine, isFocused]); // Removed focus from dependencies

    // Global keyboard listener to focus search input on any keypress
    useEffect(() => {
        const handleGlobalKeyPress = (event: KeyboardEvent) => {
            // Only focus if the event target is not already an input, textarea, or contenteditable
            const target = event.target as HTMLElement;
            const isInputElement = target.tagName === 'INPUT' ||
                target.tagName === 'TEXTAREA' ||
                target.contentEditable === 'true';

            if (!isInputElement && searchInputRef.current && !isFocused) {
                focus(searchInputRef.current);
            }
        };

        document.addEventListener('keydown', handleGlobalKeyPress);
        return () => document.removeEventListener('keydown', handleGlobalKeyPress);
    }, [isFocused]); // Removed focus from dependencies

    const handleSearch = () => {
        if (query.trim()) {
            if (searchMode === 'newTab') {
                if (onSearchNewTab) {
                    onSearchNewTab(query.trim(), selectedEngine);
                } else {
                    // Default behavior: open in new tab
                    const searchUrl = selectedEngine.buildSearchUrl(query.trim());
                    window.open(searchUrl, '_blank');
                }
            } else {
                if (onSearch) {
                    onSearch(query.trim(), selectedEngine);
                } else {
                    // Default behavior: open in current tab
                    const searchUrl = selectedEngine.buildSearchUrl(query.trim());
                    window.location.href = searchUrl;
                }
            }
        }
    };

    const handleKeyPress = (event: React.KeyboardEvent) => {
        if (event.key === 'Enter') {
            handleSearch();
        }
    };

    const handleEngineSelect = async (engine: SearchEngineStrategy) => {
        await setSelectedEngine(engine.name.toLowerCase());
        setEngineMenuAnchor(null);
    };

    const handleEngineMenuOpen = (event: React.MouseEvent<HTMLElement>) => {
        setEngineMenuAnchor(event.currentTarget);
    };

    const handleEngineMenuClose = () => {
        setEngineMenuAnchor(null);
    };

    const handleModeSelect = (mode: SearchMode) => {
        setSearchMode(mode);
        setModeMenuAnchor(null);
    };

    const handleModeMenuOpen = (event: React.MouseEvent<HTMLElement>) => {
        setModeMenuAnchor(event.currentTarget);
    };

    const handleModeMenuClose = () => {
        setModeMenuAnchor(null);
    };

    const handleContainerClick = () => {
        // Focus the input when clicking anywhere in the search container
        focus(searchInputRef.current);
    };

    const getSearchButtonText = () => {
        return searchMode === 'newTab' ? 'New Tab' : 'Search';
    };

    const getSearchButtonIcon = () => {
        return searchMode === 'newTab' ? <OpenInNewIcon /> : <SearchIcon />;
    };

    return (
        <Box className={styles.searchContainer} onClick={handleContainerClick}>
            <Box className={styles.searchRow}>
                <Paper elevation={isFocused ? 8 : 2} className={styles.searchBox}>
                    <TextField
                        ref={searchInputRef}
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
                                            onClick={handleEngineMenuOpen}
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

                <ButtonGroup className={styles.searchButtonGroup}>
                    <Button
                        variant="contained"
                        startIcon={getSearchButtonIcon()}
                        onClick={handleSearch}
                        disabled={!query.trim()}
                        className={styles.searchButton}
                    >
                        {getSearchButtonText()}
                    </Button>
                    <Button
                        size="small"
                        onClick={handleModeMenuOpen}
                        className={styles.modeSelector}
                    >
                        <ArrowDropDownIcon />
                    </Button>
                </ButtonGroup>
            </Box>

            <Menu
                anchorEl={engineMenuAnchor}
                open={Boolean(engineMenuAnchor)}
                onClose={handleEngineMenuClose}
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

            <Menu
                anchorEl={modeMenuAnchor}
                open={Boolean(modeMenuAnchor)}
                onClose={handleModeMenuClose}
                className={styles.modeMenu}
            >
                <MenuItem
                    onClick={() => handleModeSelect('current')}
                    selected={searchMode === 'current'}
                >
                    <ListItemIcon>
                        <SearchIcon />
                    </ListItemIcon>
                    <ListItemText>
                        <Typography variant="body2">Search (Current Tab)</Typography>
                    </ListItemText>
                </MenuItem>
                <MenuItem
                    onClick={() => handleModeSelect('newTab')}
                    selected={searchMode === 'newTab'}
                >
                    <ListItemIcon>
                        <OpenInNewIcon />
                    </ListItemIcon>
                    <ListItemText>
                        <Typography variant="body2">Search (New Tab)</Typography>
                    </ListItemText>
                </MenuItem>
            </Menu>
        </Box>
    );
};
