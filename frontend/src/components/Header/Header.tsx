import React from 'react';
import { BackendStatus } from './BackendStatus';
import { StatusBadges } from './StatusBadges';
import { Clock } from './Clock';
import { ChromeProfileSwitcher } from './ChromeProfileSwitcher';
import styles from './Header.module.css';

export const Header: React.FC = () => {
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
                </div>

                <div className={styles.headerBottomRow}>
                    <StatusBadges />
                </div>
            </div>
        </header>
    );
};
