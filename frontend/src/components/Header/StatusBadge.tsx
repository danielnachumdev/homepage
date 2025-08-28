import React from 'react';
import styles from './StatusBadge.module.css';

export interface StatusBadgeProps {
    label: string;
    value: string | number;
    icon?: string;
    color?: 'primary' | 'success' | 'warning' | 'error' | 'info';
    trend?: 'up' | 'down' | 'stable';
    trendValue?: string;
}

export const StatusBadge: React.FC<StatusBadgeProps> = ({
    label,
    value,
    icon,
    color = 'primary',
    trend,
    trendValue
}) => {
    const getColorClass = () => {
        switch (color) {
            case 'success': return styles.statusBadgeSuccess;
            case 'warning': return styles.statusBadgeWarning;
            case 'error': return styles.statusBadgeError;
            case 'info': return styles.statusBadgeInfo;
            default: return styles.statusBadgePrimary;
        }
    };

    const getTrendClass = () => {
        switch (trend) {
            case 'up': return styles.trendUp;
            case 'down': return styles.trendDown;
            case 'stable': return styles.trendStable;
            default: return '';
        }
    };

    return (
        <div className={`${styles.statusBadge} ${getColorClass()}`}>
            {icon && <span className={styles.statusBadgeIcon}>{icon}</span>}

            <div className={styles.statusBadgeContent}>
                <div className={styles.statusBadgeLabel}>{label}</div>
                <div className={styles.statusBadgeValue}>{value}</div>

                {trend && trendValue && (
                    <div className={`${styles.statusBadgeTrend} ${getTrendClass()}`}>
                        <span className={styles.trendIcon}>
                            {trend === 'up' ? '↗' : trend === 'down' ? '↘' : '→'}
                        </span>
                        <span className={styles.trendValue}>{trendValue}</span>
                    </div>
                )}
            </div>
        </div>
    );
};
