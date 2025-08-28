import React from 'react';
import { BackendStatus } from './BackendStatus';
import { StatusBadges } from './StatusBadges';
import './Header.css';

export const Header: React.FC = () => {
    // Local sub-component for the homepage title
    const HomepageTitle = (
        <div className="header-title">
            <h1>Homepage</h1>
        </div>
    );

    return (
        <header className="header">
            <div className="header-content">
                <div className="header-status-wrapper">
                    <BackendStatus />
                </div>
                <div className="header-top-row">
                    {HomepageTitle}
                </div>

                <div className="header-bottom-row">
                    <StatusBadges />
                </div>
            </div>
        </header>
    );
};
