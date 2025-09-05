import React from 'react';
import {SpeedTestWidget} from './SpeedTestWidget';
import styles from './StatusBadges.module.css';

export const StatusBadges: React.FC = () => {

    return (
        <div className={styles.statusBadges}>
            <SpeedTestWidget intervalSeconds={1} autoStart={true}/>
        </div>
    );
};
