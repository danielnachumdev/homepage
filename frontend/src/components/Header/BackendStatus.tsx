import React from 'react';
import { useBackendStatus } from '../../hooks/useBackendStatus';
import './BackendStatus.css';

export const BackendStatus: React.FC = () => {
    const { isConnected, error } = useBackendStatus();

    const getStatusColor = () => {
        return isConnected ? '#4caf50' : '#f44336';
    };

    const getStatusText = () => {
        if (isConnected) return 'BACKEND';
        if (error) return 'BACKEND';
        return 'BACKEND';
    };

    return (
        <div className="backend-status">
            <div className="status-indicator">
                <div
                    className="status-dot"
                    style={{ backgroundColor: getStatusColor() }}
                    title={`${isConnected ? 'Connected' : 'Disconnected'} - ${error || 'No errors'}`}
                />
                <span className="status-text">{getStatusText()}</span>
            </div>

            {error && (
                <div className="status-error" title={error}>
                    ⚠️
                </div>
            )}
        </div>
    );
};
