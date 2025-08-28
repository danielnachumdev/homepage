import React from 'react';
import { useBackendStatus } from '../../hooks/useBackendStatus';
import './Header.css';

export const Header: React.FC = () => {
    const { isConnected, lastChecked, error } = useBackendStatus();

    const formatLastChecked = (date: Date | null) => {
        if (!date) return 'Never';
        return date.toLocaleTimeString();
    };

    const getStatusColor = () => {
        return isConnected ? '#4caf50' : '#f44336';
    };

    const getStatusText = () => {
        if (isConnected) return 'Connected';
        if (error) return 'Error';
        return 'Disconnected';
    };

    return (
        <header className="header">
            <div className="header-content">
                <div className="header-title">
                    <h1>Homepage</h1>
                </div>

                <div className="header-status">
                    <div className="status-indicator">
                        <div
                            className="status-dot"
                            style={{ backgroundColor: getStatusColor() }}
                            title={`${getStatusText()} - Last checked: ${formatLastChecked(lastChecked)}`}
                        />
                        <span className="status-text">{getStatusText()}</span>
                    </div>

                    {error && (
                        <div className="status-error" title={error}>
                            ⚠️
                        </div>
                    )}

                    <div className="status-time">
                        Last: {formatLastChecked(lastChecked)}
                    </div>
                </div>
            </div>
        </header>
    );
};
