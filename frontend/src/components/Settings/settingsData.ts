import type { SettingsCategory } from './types';

export const settingsData: SettingsCategory[] = [
    {
        id: 'appearance',
        name: 'Appearance',
        description: 'Customize the look and feel of your homepage',
        settings: [
            {
                name: 'Theme',
                description: 'Choose between light, dark, or auto theme',
                type: 'select',
                value: 'auto',
                options: ['light', 'dark', 'auto']
            },
            {
                name: 'Primary Color',
                description: 'Set the primary color for your homepage',
                type: 'color',
                value: '#1976d2'
            },
            {
                name: 'Background Opacity',
                description: 'Adjust the transparency of background elements',
                type: 'number',
                value: 0.1,
                min: 0,
                max: 1,
                step: 0.1
            },
            {
                name: 'Show Animations',
                description: 'Enable or disable UI animations',
                type: 'boolean',
                value: true
            }
        ]
    },
    {
        id: 'notifications',
        name: 'Notifications',
        description: 'Configure notification preferences',
        settings: [
            {
                name: 'Enable Notifications',
                description: 'Show system notifications',
                type: 'boolean',
                value: true
            },
            {
                name: 'Sound Alerts',
                description: 'Play sound for important notifications',
                type: 'boolean',
                value: false
            },
            {
                name: 'Notification Position',
                description: 'Choose where notifications appear',
                type: 'select',
                value: 'top-right',
                options: ['top-left', 'top-right', 'bottom-left', 'bottom-right']
            }
        ]
    },
    {
        id: 'performance',
        name: 'Performance',
        description: 'Optimize performance settings',
        settings: [
            {
                name: 'Auto-refresh Interval',
                description: 'How often to refresh data (in seconds)',
                type: 'number',
                value: 30,
                min: 5,
                max: 300,
                step: 5
            },
            {
                name: 'Enable Caching',
                description: 'Cache data to improve performance',
                type: 'boolean',
                value: true
            },
            {
                name: 'Lazy Loading',
                description: 'Load components only when needed',
                type: 'boolean',
                value: true
            }
        ]
    },
    {
        id: 'privacy',
        name: 'Privacy & Security',
        description: 'Manage your privacy and security settings',
        settings: [
            {
                name: 'Data Collection',
                description: 'Allow anonymous usage data collection',
                type: 'boolean',
                value: false
            },
            {
                name: 'Session Timeout',
                description: 'Auto-logout after inactivity (minutes)',
                type: 'number',
                value: 60,
                min: 15,
                max: 480,
                step: 15
            },
            {
                name: 'Secure Connection',
                description: 'Require HTTPS connections',
                type: 'boolean',
                value: true
            }
        ]
    },
    {
        id: 'chrome',
        name: 'Chrome Integration',
        description: 'Configure Chrome browser integration',
        settings: [
            {
                name: 'Auto-switch Profiles',
                description: 'Automatically switch Chrome profiles based on context',
                type: 'boolean',
                value: true
            },
            {
                name: 'Profile Sync',
                description: 'Sync Chrome profiles across devices',
                type: 'boolean',
                value: false
            },
            {
                name: 'Default Profile',
                description: 'Set the default Chrome profile to use',
                type: 'select',
                value: 'Default',
                options: ['Default', 'Work', 'Personal', 'Development']
            }
        ]
    },
    {
        id: 'docker',
        name: 'Docker Management',
        description: 'Configure Docker container management',
        settings: [
            {
                name: 'Auto-start Containers',
                description: 'Automatically start containers on system boot',
                type: 'boolean',
                value: false
            },
            {
                name: 'Container Health Checks',
                description: 'Enable health monitoring for containers',
                type: 'boolean',
                value: true
            },
            {
                name: 'Resource Limits',
                description: 'Set default resource limits for containers',
                type: 'select',
                value: 'medium',
                options: ['low', 'medium', 'high', 'unlimited']
            }
        ]
    }
];
