import React, { useState, useRef, useCallback, useEffect } from 'react';
import {
    Box,
    Typography,
    TextField,
    List,
    ListItem,
    ListItemButton,
    ListItemText,
    Divider,
    IconButton,
    useTheme,
    useMediaQuery
} from '@mui/material';
import { Close as CloseIcon, Search as SearchIcon } from '@mui/icons-material';
import type { SettingsCategory } from './types';
import { settingsData } from './settingsData';
import styles from './Settings.module.css';

interface SettingsProps {
    onClose: () => void;
}

export const Settings: React.FC<SettingsProps> = ({ onClose }) => {
    const theme = useTheme();
    const isSmallScreen = useMediaQuery(theme.breakpoints.down('md'));

    const [searchTerm, setSearchTerm] = useState('');
    const [activeCategory, setActiveCategory] = useState<string>('');
    const [filteredCategories, setFilteredCategories] = useState<SettingsCategory[]>(settingsData);

    const categoryRefs = useRef<{ [key: string]: HTMLDivElement | null }>({});
    const scrollContainerRef = useRef<HTMLDivElement>(null);

    // Filter categories based on search term
    useEffect(() => {
        if (!searchTerm.trim()) {
            setFilteredCategories(settingsData);
            return;
        }

        const filtered = settingsData.map(category => ({
            ...category,
            settings: category.settings.filter(setting =>
                setting.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                setting.description.toLowerCase().includes(searchTerm.toLowerCase())
            )
        })).filter(category => category.settings.length > 0);

        setFilteredCategories(filtered);
    }, [searchTerm]);

    // Handle category click and scroll
    const handleCategoryClick = useCallback((categoryId: string) => {
        setActiveCategory(categoryId);
        const element = categoryRefs.current[categoryId];
        if (element && scrollContainerRef.current) {
            element.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    }, []);

    // Handle scroll to detect active category
    const handleScroll = useCallback(() => {
        if (!scrollContainerRef.current) return;

        let newActiveCategory = '';
        let minDistance = Infinity;

        Object.entries(categoryRefs.current).forEach(([categoryId, element]) => {
            if (element) {
                const rect = element.getBoundingClientRect();
                const containerRect = scrollContainerRef.current!.getBoundingClientRect();
                const distance = Math.abs(rect.top - containerRect.top);

                if (distance < minDistance) {
                    minDistance = distance;
                    newActiveCategory = categoryId;
                }
            }
        });

        if (newActiveCategory !== activeCategory) {
            setActiveCategory(newActiveCategory);
        }
    }, [activeCategory]);

    // Set initial active category
    useEffect(() => {
        if (filteredCategories.length > 0) {
            setActiveCategory(filteredCategories[0].id);
        }
    }, [filteredCategories]);

    // Local sub-component for the header
    const SettingsHeader = (
        <Box className={styles.settingsHeader}>
            <Typography variant="h4" component="h1" className={styles.settingsTitle}>
                Settings
            </Typography>
            <IconButton
                onClick={onClose}
                className={styles.closeButton}
                size="large"
                sx={{
                    color: 'rgba(255, 255, 255, 0.8)',
                    '&:hover': {
                        color: 'white',
                        backgroundColor: 'rgba(255, 255, 255, 0.1)',
                    },
                }}
            >
                <CloseIcon />
            </IconButton>
        </Box>
    );

    // Local sub-component for the search bar
    const SearchBar = (
        <Box className={styles.searchContainer}>
            <TextField
                fullWidth
                placeholder="Search settings..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                InputProps={{
                    startAdornment: <SearchIcon sx={{ color: 'rgba(255, 255, 255, 0.6)', mr: 1 }} />,
                }}
                sx={{
                    '& .MuiOutlinedInput-root': {
                        color: 'white',
                        '& fieldset': {
                            borderColor: 'rgba(255, 255, 255, 0.3)',
                        },
                        '&:hover fieldset': {
                            borderColor: 'rgba(255, 255, 255, 0.5)',
                        },
                        '&.Mui-focused fieldset': {
                            borderColor: 'rgba(255, 255, 255, 0.8)',
                        },
                    },
                    '& .MuiInputBase-input::placeholder': {
                        color: 'rgba(255, 255, 255, 0.6)',
                        opacity: 1,
                    },
                }}
            />
        </Box>
    );

    // Local sub-component for the category navigation
    const CategoryNavigation = (
        <Box className={styles.categoryNavigation}>
            <Typography variant="h6" className={styles.navigationTitle}>
                Categories
            </Typography>
            <List className={styles.categoryList}>
                {filteredCategories.map((category) => (
                    <ListItem key={category.id} disablePadding>
                        <ListItemButton
                            onClick={() => handleCategoryClick(category.id)}
                            className={`${styles.categoryButton} ${activeCategory === category.id ? styles.activeCategory : ''
                                }`}
                            sx={{
                                borderRadius: 1,
                                mx: 1,
                                mb: 0.5,
                            }}
                        >
                            <ListItemText
                                primary={category.name}
                                primaryTypographyProps={{
                                    className: styles.categoryText,
                                }}
                            />
                        </ListItemButton>
                    </ListItem>
                ))}
            </List>
        </Box>
    );

    // Local sub-component for the settings content
    const SettingsContent = (
        <Box className={styles.settingsContent}>
            <div
                ref={scrollContainerRef}
                className={styles.scrollContainer}
                onScroll={handleScroll}
            >
                {filteredCategories.map((category) => (
                    <div
                        key={category.id}
                        ref={(el) => {
                            categoryRefs.current[category.id] = el;
                        }}
                        className={styles.categorySection}
                    >
                        <Typography
                            variant="h5"
                            component="h2"
                            className={styles.categoryTitle}
                            sx={{
                                color: 'white',
                                mb: 2,
                                pb: 1,
                                borderBottom: '2px solid rgba(255, 255, 255, 0.2)',
                            }}
                        >
                            {category.name}
                        </Typography>

                        <Box className={styles.settingsList}>
                            {category.settings.map((setting, index) => (
                                <Box key={index} className={styles.settingItem}>
                                    <Typography variant="h6" className={styles.settingName}>
                                        {setting.name}
                                    </Typography>
                                    <Typography variant="body2" className={styles.settingDescription}>
                                        {setting.description}
                                    </Typography>
                                    {/* Placeholder for actual setting controls */}
                                    <Box className={styles.settingControl}>
                                        <Typography variant="caption" sx={{ color: 'rgba(255, 255, 255, 0.6)' }}>
                                            Setting control placeholder
                                        </Typography>
                                    </Box>
                                </Box>
                            ))}
                        </Box>

                        {category.id !== filteredCategories[filteredCategories.length - 1].id && (
                            <Divider sx={{ my: 3, borderColor: 'rgba(255, 255, 255, 0.1)' }} />
                        )}
                    </div>
                ))}
            </div>
        </Box>
    );

    return (
        <Box className={styles.settingsContainer}>
            {SettingsHeader}
            {SearchBar}

            <Box className={styles.settingsLayout}>
                {!isSmallScreen && CategoryNavigation}
                {SettingsContent}
            </Box>
        </Box>
    );
};
