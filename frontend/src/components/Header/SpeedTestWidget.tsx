import React, { useState, useEffect, useCallback } from 'react';
import { CustomStatusBadge } from './StatusBadge';
import { api } from '../../lib/api';
import styles from './SpeedTestWidget.module.css';

interface SpeedTestResult {
    download_speed_mbps: number;
    upload_speed_mbps: number;
    ping_ms: number;
    timestamp: string;
    server_name?: string;
    server_sponsor?: string;
}

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
    const [result, setResult] = useState<SpeedTestResult | null>(null);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [isRunning, setIsRunning] = useState(false);
    const [loadingMessage, setLoadingMessage] = useState<string>('');

    const formatSpeed = useCallback((speedMbps: number): [string, string] => {
        if (speedMbps >= 1000) {
            return [(speedMbps / 1000).toFixed(1), 'GB/s'];
        } else if (speedMbps >= 1) {
            return [speedMbps.toFixed(1), 'MB/s'];
        } else {
            return [(speedMbps * 1000).toFixed(0), 'KB/s'];
        }
    }, []);

    const formatPing = useCallback((pingMs: number): string => {
        return `${pingMs.toFixed(0)} ms`;
    }, []);

    const performSpeedTest = useCallback(async () => {
        try {
            setIsLoading(true);
            setError(null);
            setLoadingMessage('Internet speed test');

            const response = await api.post('/api/v1/speedtest/test', {
                interval_seconds: intervalSeconds
            });

            if (response.data.success && response.data.result) {
                setResult(response.data.result);
            } else {
                throw new Error(response.data.message || 'Speed test failed');
            }
        } catch (err: any) {
            const errorMessage = err?.message || 'Unknown error occurred';
            setError(errorMessage);
            console.error('Speed test error:', err);
        } finally {
            setIsLoading(false);
            setLoadingMessage('');
        }
    }, [intervalSeconds]);

    const startContinuousTesting = useCallback(async () => {
        try {
            setError(null);
            setLoadingMessage('Starting speed test');

            const response = await api.post('/api/v1/speedtest/start', {
                interval_seconds: intervalSeconds
            });

            if (response.data.success) {
                setIsRunning(true);
            } else {
                throw new Error(response.data.message || 'Failed to start continuous testing');
            }
        } catch (err: any) {
            const errorMessage = err?.message || 'Unknown error occurred';
            setError(errorMessage);
            console.error('Start continuous testing error:', err);
        } finally {
            setLoadingMessage('');
        }
    }, [intervalSeconds]);

    const stopContinuousTesting = useCallback(async () => {
        try {
            setError(null);
            setLoadingMessage('Stopping speed test');

            const response = await api.post('/api/v1/speedtest/stop');

            if (response.data.success) {
                setIsRunning(false);
            } else {
                throw new Error(response.data.message || 'Failed to stop continuous testing');
            }
        } catch (err: any) {
            const errorMessage = err?.message || 'Unknown error occurred';
            setError(errorMessage);
            console.error('Stop continuous testing error:', err);
        } finally {
            setLoadingMessage('');
        }
    }, []);

    const getLatestResult = useCallback(async () => {
        try {
            const response = await api.get('/api/v1/speedtest/result');

            if (response.data.success && response.data.result) {
                setResult(response.data.result);
            }
        } catch (err) {
            console.error('Get latest result error:', err);
        }
    }, []);

    // Check status on mount and auto-start if enabled
    useEffect(() => {
        const checkStatus = async () => {
            try {
                const response = await api.get('/api/v1/speedtest/status');
                const data = response.data;
                setIsRunning(data.is_running);
                if (data.has_result) {
                    await getLatestResult();
                }

                // Auto-start if enabled and not already running
                if (autoStart && !data.is_running && !result) {
                    await startContinuousTesting();
                }
            } catch (err) {
                console.error('Status check error:', err);
                // If auto-start is enabled and we get an error, try to start anyway
                if (autoStart && !result) {
                    await startContinuousTesting();
                }
            }
        };

        checkStatus();
    }, [getLatestResult, autoStart, result, startContinuousTesting]);

    // Set up polling for latest results when continuous testing is running
    useEffect(() => {
        if (!isRunning) return;

        const interval = setInterval(() => {
            getLatestResult();
        }, intervalSeconds * 1000);

        return () => clearInterval(interval);
    }, [isRunning, intervalSeconds, getLatestResult]);

    const handleClick = () => {
        if (isRunning) {
            stopContinuousTesting();
        } else {
            startContinuousTesting();
        }
    };

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

    return (
        <CustomStatusBadge
            color={getStatusColor()}
            className={`${styles.speedTestWidget} ${className}`}
            onClick={handleClick}
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
                                {formatSpeed(result.download_speed_mbps)[0]} {formatSpeed(result.download_speed_mbps)[1]}
                            </span>
                        </div>
                        <div className={styles.speedRow}>
                            <span className={styles.speedLabel}>Up</span>
                            <span className={styles.speedValue}>
                                {formatSpeed(result.upload_speed_mbps)[0]} {formatSpeed(result.upload_speed_mbps)[1]}
                            </span>
                        </div>
                        <div className={styles.pingRow}>
                            <span className={styles.pingLabel}>PING</span>
                            <span className={styles.pingValue}>
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
