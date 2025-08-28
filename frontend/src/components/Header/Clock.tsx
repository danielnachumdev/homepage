import React, { useState, useEffect } from 'react';
import styles from './Clock.module.css';

export const Clock: React.FC = () => {
    const [currentTime, setCurrentTime] = useState(new Date());

    useEffect(() => {
        const interval = setInterval(() => {
            setCurrentTime(new Date());
        }, 1000);

        return () => clearInterval(interval);
    }, []);

    const formatTime = (date: Date) => {
        return date.toLocaleTimeString('en-GB', {
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit',
            hour12: false
        });
    };

    const formatDate = (date: Date) => {
        return date.toLocaleDateString('en-GB', {
            day: '2-digit',
            month: '2-digit',
            year: 'numeric'
        });
    };

    return (
        <div className={styles.clock}>
            <div className={styles.time}>{formatTime(currentTime)}</div>
            <div className={styles.date}>{formatDate(currentTime)}</div>
        </div>
    );
};
