import React from 'react';
import './StatusBadge.css';

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
            case 'success': return 'status-badge--success';
            case 'warning': return 'status-badge--warning';
            case 'error': return 'status-badge--error';
            case 'info': return 'status-badge--info';
            default: return 'status-badge--primary';
        }
    };

    const getTrendIcon = () => {
        switch (trend) {
            case 'up': return '↗';
            case 'down': return '↘';
            case 'stable': return '→';
            default: return null;
        }
    };

    const getTrendClass = () => {
        switch (trend) {
            case 'up': return 'trend--up';
            case 'down': return 'trend--down';
            case 'stable': return 'trend--stable';
            default: return '';
        }
    };

    return (
        <div className={`status-badge ${getColorClass()}`}>
            {icon && <span className="status-badge__icon">{icon}</span>}

            <div className="status-badge__content">
                <div className="status-badge__label">{label}</div>
                <div className="status-badge__value">{value}</div>

                {trend && trendValue && (
                    <div className={`status-badge__trend ${getTrendClass()}`}>
                        <span className="trend-icon">{getTrendIcon()}</span>
                        <span className="trend-value">{trendValue}</span>
                    </div>
                )}
            </div>
        </div>
    );
};
