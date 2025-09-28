import React, { useState, useRef } from 'react';
import { BackendStatus } from './BackendStatus';
import { StatusBadges } from './StatusBadges';
import { Clock } from './Clock';
import { ChromeProfileSwitcher } from './ChromeProfileSwitcher';
import { SettingsIcon } from './SettingsIcon';
import { SettingsModal } from '../Settings';
import { useComponentLogger } from '../../hooks/useLogger';
import styles from './Header.module.css';

export const Header: React.FC = () => {
    const [settingsOpen, setSettingsOpen] = useState(false);
    const renderCountRef = useRef(0);
    renderCountRef.current += 1;
    const logger = useComponentLogger('Header');
    logger.debug(`Header component rendered - count: ${renderCountRef.current}`);

    // Local sub-component for the homepage title
    const HomepageTitle = (
        <div className={styles.headerTitle}>
            <h1>Homepage</h1>
        </div>
    );

    // Local sub-component for the Chrome profile switcher
    const ChromeProfileSection = (
        <div className={styles.chromeProfileSection}>
            <ChromeProfileSwitcher />
        </div>
    );

    // Local sub-component for the settings icon
    const SettingsSection = (
        <div className={styles.settingsIcon}>
            <SettingsIcon onOpen={() => setSettingsOpen(true)} />
        </div>
    );

    return (
        <header className={styles.header}>
            <div className={styles.headerContent}>
                <div className={styles.headerStatusWrapper}>
                    <BackendStatus />
                    <Clock />
                </div>
                <div className={styles.headerTopRow}>
                    {ChromeProfileSection}
                    {HomepageTitle}
                    {SettingsSection}
                </div>

                <div className={styles.headerBottomRow}>
                    <StatusBadges />
                </div>
            </div>

            <SettingsModal
                open={settingsOpen}
                onClose={() => setSettingsOpen(false)}
            />
        </header>
    );
};
