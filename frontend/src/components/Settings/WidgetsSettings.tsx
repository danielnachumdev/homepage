import React, { useState } from 'react';
import {
    Box,
    Typography,
    Switch,
    FormControlLabel,
    Card,
    CardContent,
    Divider,
    Alert,
    CircularProgress,
} from '@mui/material';
import { useSpeedTestSettings } from '../../hooks/useSpeedTestSettings';
import styles from './WidgetsSettings.module.css';

interface WidgetsSettingsProps {
    onProfilesRefresh?: () => void;
}

export const WidgetsSettings: React.FC<WidgetsSettingsProps> = () => {
    const { enabled, setEnabled, loading, error } = useSpeedTestSettings();
    const [updating, setUpdating] = useState(false);

    const handleSpeedTestToggle = async (event: React.ChangeEvent<HTMLInputElement>) => {
        const newEnabled = event.target.checked;
        setUpdating(true);

        try {
            await setEnabled(newEnabled);
        } catch (err) {
            console.error('Failed to update speed test setting:', err);
        } finally {
            setUpdating(false);
        }
    };

    const SpeedTestSection = (
        <Card className={styles.settingCard}>
            <CardContent>
                <Box className={styles.settingHeader}>
                    <Box className={styles.settingInfo}>
                        <Typography variant="h6" className={styles.settingTitle}>
                            Internet Speed Test
                        </Typography>
                        <Typography variant="body2" className={styles.settingDescription}>
                            Enable or disable the internet speed test widget in the header.
                            When enabled, the widget will automatically start testing your connection speed.
                        </Typography>
                    </Box>
                    <Box className={styles.settingControl}>
                        {updating ? (
                            <CircularProgress size={24} />
                        ) : (
                            <FormControlLabel
                                control={
                                    <Switch
                                        checked={enabled}
                                        onChange={handleSpeedTestToggle}
                                        disabled={updating}
                                        color="primary"
                                    />
                                }
                                label={enabled ? 'Enabled' : 'Disabled'}
                                labelPlacement="start"
                            />
                        )}
                    </Box>
                </Box>
            </CardContent>
        </Card>
    );

    const ErrorAlert = error && (
        <Alert severity="error" className={styles.errorAlert}>
            {error}
        </Alert>
    );

    const LoadingIndicator = loading && (
        <Box className={styles.loadingContainer}>
            <CircularProgress />
            <Typography variant="body2">Loading settings...</Typography>
        </Box>
    );

    return (
        <Box className={styles.widgetsSettings}>
            {ErrorAlert}
            {LoadingIndicator}

            <Box className={styles.settingsSection}>
                <Typography variant="h6" className={styles.sectionTitle}>
                    Widget Settings
                </Typography>
                <Typography variant="body2" className={styles.sectionDescription}>
                    Configure which widgets are displayed in the application interface.
                </Typography>

                <Divider className={styles.sectionDivider} />

                {SpeedTestSection}
            </Box>
        </Box>
    );
};
