import React from 'react';
import { IconButton, Tooltip } from '@mui/material';
import { Settings } from '@mui/icons-material';
import styles from './Header.module.css';

interface SettingsIconProps {
    onOpen: () => void;
}

export const SettingsIcon: React.FC<SettingsIconProps> = ({ onOpen }) => {
    return (
        <Tooltip title="Settings" placement="bottom">
            <IconButton
                onClick={onOpen}
                className={styles.settingsIcon}
                size="medium"
                sx={{
                    color: 'rgba(255, 255, 255, 0.8)',
                    '&:hover': {
                        color: 'white',
                        backgroundColor: 'rgba(255, 255, 255, 0.1)',
                    },
                }}
            >
                <Settings />
            </IconButton>
        </Tooltip>
    );
};
