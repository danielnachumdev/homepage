import React, { useState, useEffect } from 'react';
import { SimpleStatusBadge, TrendStatusBadge, CustomStatusBadge } from './StatusBadge';
import styles from './StatusBadges.module.css';

export const StatusBadges: React.FC = () => {
    const [currentTime, setCurrentTime] = useState(new Date());
    const [userCount, setUserCount] = useState(1247);

    // Update time every second
    useEffect(() => {
        const interval = setInterval(() => {
            setCurrentTime(new Date());
        }, 1000);

        return () => clearInterval(interval);
    }, []);

    // Simulate user count changes
    useEffect(() => {
        const interval = setInterval(() => {
            setUserCount(prev => prev + Math.floor(Math.random() * 10) - 5);
        }, 5000);

        return () => clearInterval(interval);
    }, []);

    return (
        <div className={styles.statusBadges}>
            {/* Example 1: Simple status badge */}
            <SimpleStatusBadge
                label="Users"
                value={userCount}
                icon="👥"
                color="success"
            />

            {/* Example 2: Trend status badge */}
            <TrendStatusBadge
                label="System"
                value="67%"
                trend="stable"
                trendValue="0%"
                icon="⚡"
                color="warning"
            />

            {/* Example 3: Custom status badge with custom content */}
            <CustomStatusBadge
                color="info"
                title="Current time"
                onClick={() => console.log('Time badge clicked!')}
            >
                <span className={styles.statusBadgeIcon}>🕐</span>
                <div className={styles.statusBadgeContent}>
                    <div className={styles.statusBadgeLabel}>Time</div>
                    <div className={styles.statusBadgeValue}>
                        {currentTime.toLocaleTimeString()}
                    </div>
                </div>
            </CustomStatusBadge>

            {/* Example 4: Another custom badge */}
            <CustomStatusBadge
                color="primary"
                title="Network status"
            >
                <span className={styles.statusBadgeIcon}>🌐</span>
                <div className={styles.statusBadgeContent}>
                    <div className={styles.statusBadgeLabel}>Network</div>
                    <div className={styles.statusBadgeValue}>45 Mbps</div>
                </div>
            </CustomStatusBadge>

            {/* Example 5: Minimal custom badge */}
            <CustomStatusBadge
                color="error"
                title="Error count"
            >
                <div className={styles.statusBadgeContent}>
                    <div className={styles.statusBadgeLabel}>Errors</div>
                    <div className={styles.statusBadgeValue}>0</div>
                </div>
            </CustomStatusBadge>
        </div>
    );
};
