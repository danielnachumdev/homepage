import React from 'react';
import styles from './StatusBadge.module.css';

export interface StatusBadgeProps {
    children: React.ReactNode;
    color?: 'primary' | 'success' | 'warning' | 'error' | 'info';
    className?: string;
    onClick?: () => void;
    title?: string;
}

export const StatusBadge: React.FC<StatusBadgeProps> = ({
    children,
    color = 'primary',
    className = '',
    onClick,
    title
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

    const baseClasses = `${styles.statusBadge} ${getColorClass()}`;
    const finalClasses = className ? `${baseClasses} ${className}` : baseClasses;

    return (
        <div
            className={finalClasses}
            onClick={onClick}
            title={title}
            style={{ cursor: onClick ? 'pointer' : 'default' }}
        >
            {children}
        </div>
    );
};

// Pre-built badge components for common use cases
export const SimpleStatusBadge: React.FC<{
    label: string;
    value: string | number;
    color?: StatusBadgeProps['color'];
    icon?: string;
}> = ({ label, value, color, icon }) => (
    <StatusBadge color={color}>
        {icon && <span className={styles.statusBadgeIcon}>{icon}</span>}
        <div className={styles.statusBadgeContent}>
            <div className={styles.statusBadgeLabel}>{label}</div>
            <div className={styles.statusBadgeValue}>{value}</div>
        </div>
    </StatusBadge>
);

export const TrendStatusBadge: React.FC<{
    label: string;
    value: string | number;
    trend: 'up' | 'down' | 'stable';
    trendValue: string;
    color?: StatusBadgeProps['color'];
    icon?: string;
}> = ({ label, value, trend, trendValue, color, icon }) => (
    <StatusBadge color={color}>
        {icon && <span className={styles.statusBadgeIcon}>{icon}</span>}
        <div className={styles.statusBadgeContent}>
            <div className={styles.statusBadgeLabel}>{label}</div>
            <div className={styles.statusBadgeValue}>{value}</div>
            <div className={`${styles.statusBadgeTrend} ${styles[`trend${trend.charAt(0).toUpperCase() + trend.slice(1)}`]}`}>
                <span className={styles.trendIcon}>
                    {trend === 'up' ? '↗' : trend === 'down' ? '↘' : '→'}
                </span>
                <span className={styles.trendValue}>{trendValue}</span>
            </div>
        </div>
    </StatusBadge>
);

export const CustomStatusBadge: React.FC<{
    children: React.ReactNode;
    color?: StatusBadgeProps['color'];
    className?: string;
    onClick?: () => void;
    title?: string;
}> = ({ children, color, className, onClick, title }) => (
    <StatusBadge color={color} className={className} onClick={onClick} title={title}>
        {children}
    </StatusBadge>
);
