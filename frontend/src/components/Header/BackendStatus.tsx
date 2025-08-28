import React from 'react';
import { useBackendStatus } from '../../hooks/useBackendStatus';
import styles from './BackendStatus.module.css';

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
        <div className={styles.backendStatus}>
            <div className={styles.statusIndicator}>
                <div
                    className={styles.statusDot}
                    style={{ backgroundColor: getStatusColor() }}
                    title={`${isConnected ? 'Connected' : 'Disconnected'} - ${error || 'No errors'}`}
                />
                <span className={styles.statusText}>{getStatusText()}</span>
            </div>

            {error && (
                <div className={styles.statusError} title={error}>
                    ⚠️
                </div>
            )}

        </div>
    );
};
