import React, { useCallback } from 'react';
import { CustomStatusBadge } from './StatusBadge';
import { useSpeedTest } from '../../hooks/useSpeedTest';
import styles from './SpeedTestWidget.module.css';

interface SpeedTestWidgetProps {
    intervalSeconds?: number;
    className?: string;
    autoStart?: boolean;
}

export const SpeedTestWidget: React.FC<SpeedTestWidgetProps> = ({
    intervalSeconds = 1,
    className = '',
    autoStart = true
}) => {
    const {
        result,
        isLoading,
        isRunning,
        error,
        loadingMessage,
        isDownloadLoading,
        isUploadLoading,
        isPingLoading,
        toggleTesting
    } = useSpeedTest({ intervalSeconds, autoStart });

    const formatSpeed = useCallback((speedMbps?: number): [string, string] => {
        if (!speedMbps) return ['--', ''];

        if (speedMbps >= 1000) {
            return [(speedMbps / 1000).toFixed(1), 'GB/s'];
        } else if (speedMbps >= 1) {
            return [speedMbps.toFixed(1), 'MB/s'];
        } else {
            return [(speedMbps * 1000).toFixed(0), 'KB/s'];
        }
    }, []);

    const formatPing = useCallback((pingMs?: number): string => {
        if (!pingMs) return '-- ms';
        return `${pingMs.toFixed(0)} ms`;
    }, []);

    const getStatusColor = (): 'primary' | 'success' | 'warning' | 'error' | 'info' => {
        if (error) return 'error';
        if (isLoading) return 'warning';
        if (isRunning) return 'success';
        return 'info';
    };

    const getStatusIcon = (): string => {
        if (error) return '❌';
        if (isLoading) return '⏳';
        if (isRunning) return '🔄';
        return '🌐';
    };

    const renderLoadingIcon = () => (
        <span className={styles.loadingIcon}>⏳</span>
    );

    return (
        <CustomStatusBadge
            color={getStatusColor()}
            className={`${styles.speedTestWidget} ${className}`}
            onClick={toggleTesting}
            title={`Click to ${isRunning ? 'stop' : 'start'} continuous speed testing`}
        >
            <span className={styles.statusBadgeIcon}>{getStatusIcon()}</span>
            <div className={styles.statusBadgeContent}>
                {error ? (
                    <div className={styles.errorContent}>
                        <div className={styles.statusBadgeLabel}>Speed Test</div>
                        <div className={styles.statusBadgeValue}>Error</div>
                    </div>
                ) : isLoading ? (
                    <div className={styles.loadingContent}>
                        <div className={styles.statusBadgeLabel}>Speed Test</div>
                        <div className={styles.statusBadgeValue}>
                            {loadingMessage || 'Testing...'}
                        </div>
                    </div>
                ) : result ? (
                    <div className={styles.speedContent}>
                        <div className={styles.speedRow}>
                            <span className={styles.speedLabel}>Down</span>
                            <span className={styles.speedValue}>
                                {isDownloadLoading && renderLoadingIcon()}
                                {formatSpeed(result.download_speed_mbps)[0]} {formatSpeed(result.download_speed_mbps)[1]}
                            </span>
                        </div>
                        <div className={styles.speedRow}>
                            <span className={styles.speedLabel}>Up</span>
                            <span className={styles.speedValue}>
                                {isUploadLoading && renderLoadingIcon()}
                                {formatSpeed(result.upload_speed_mbps)[0]} {formatSpeed(result.upload_speed_mbps)[1]}
                            </span>
                        </div>
                        <div className={styles.pingRow}>
                            <span className={styles.pingLabel}>PING</span>
                            <span className={styles.pingValue}>
                                {isPingLoading && renderLoadingIcon()}
                                {formatPing(result.ping_ms)}
                            </span>
                        </div>
                    </div>
                ) : (
                    <div className={styles.noDataContent}>
                        <div className={styles.statusBadgeLabel}>Speed Test</div>
                        <div className={styles.statusBadgeValue}>Click to start</div>
                    </div>
                )}
            </div>
        </CustomStatusBadge>
    );
};