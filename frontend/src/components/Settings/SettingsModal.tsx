import React from 'react';
import { Dialog, DialogContent, useMediaQuery, useTheme } from '@mui/material';
import { Settings } from './Settings';
import styles from './SettingsModal.module.css';

interface SettingsModalProps {
    open: boolean;
    onClose: () => void;
}

export const SettingsModal: React.FC<SettingsModalProps> = ({ open, onClose }) => {
    const theme = useTheme();
    const isSmallScreen = useMediaQuery(theme.breakpoints.down('md'));

    const handleClose = (_event: React.MouseEvent, reason: string) => {
        if (reason === 'backdropClick' || reason === 'escapeKeyDown') {
            onClose();
        }
    };

    return (
        <Dialog
            open={open}
            onClose={handleClose}
            maxWidth={false}
            fullScreen={isSmallScreen}
            fullWidth={!isSmallScreen}
            PaperProps={{
                className: styles.modalPaper,
                sx: {
                    maxWidth: isSmallScreen ? '100%' : '90vw',
                    maxHeight: isSmallScreen ? '100%' : '90vh',
                    width: isSmallScreen ? '100%' : '90vw',
                    height: isSmallScreen ? '100%' : '90vh',
                },
            }}
            BackdropProps={{
                className: styles.modalBackdrop,
            }}
        >
            <DialogContent className={styles.modalContent}>
                <Settings onClose={onClose} />
            </DialogContent>
        </Dialog>
    );
};
