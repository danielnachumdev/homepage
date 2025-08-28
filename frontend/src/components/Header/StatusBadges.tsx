import React, { useState, useEffect } from 'react';
import { StatusBadge } from './StatusBadge';
import type { StatusBadgeProps } from './StatusBadge';
import styles from './StatusBadges.module.css';

// Mock data for demonstration - in a real app, this would come from your backend
const mockStatusData: StatusBadgeProps[] = [
    {
        label: 'Active Users',
        value: '1,247',
        icon: '👥',
        color: 'success',
        trend: 'up',
        trendValue: '+12%'
    },
    {
        label: 'System Load',
        value: '67%',
        icon: '⚡',
        color: 'warning',
        trend: 'stable',
        trendValue: '0%'
    },
    {
        label: 'Memory Usage',
        value: '2.1GB',
        icon: '💾',
        color: 'info',
        trend: 'down',
        trendValue: '-5%'
    },
    {
        label: 'Network',
        value: '45 Mbps',
        icon: '🌐',
        color: 'primary',
        trend: 'up',
        trendValue: '+8%'
    }
];

export const StatusBadges: React.FC = () => {
    const [statusData, setStatusData] = useState<StatusBadgeProps[]>(mockStatusData);

    // Simulate real-time updates
    useEffect(() => {
        const interval = setInterval(() => {
            setStatusData(prevData =>
                prevData.map(badge => ({
                    ...badge,
                    // Simulate changing values
                    value: badge.label === 'Active Users'
                        ? `${Math.floor(Math.random() * 500) + 1000}`
                        : badge.value,
                    // Simulate changing trends
                    trend: Math.random() > 0.7 ?
                        (Math.random() > 0.5 ? 'up' : 'down') : 'stable' as const,
                    trendValue: Math.random() > 0.7 ?
                        `${Math.random() > 0.5 ? '+' : '-'}${Math.floor(Math.random() * 20) + 1}%`
                        : badge.trendValue
                }))
            );
        }, 10000); // Update every 10 seconds

        return () => clearInterval(interval);
    }, []);

    return (
        <div className={styles.statusBadges}>
            {statusData.map((badge, index) => (
                <StatusBadge
                    key={`${badge.label}-${index}`}
                    {...badge}
                />
            ))}
        </div>
    );
};
