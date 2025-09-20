import type { LinkData } from '../../../types/linkCard';

// Individual card constants for easier management
export const YOUTUBE_SUBSCRIPTIONS: LinkData = {
    title: 'Subscriptions',
    url: 'https://www.youtube.com/feed/subscriptions',
    description: 'View your YouTube subscriptions and latest videos',
    icon: 'https://www.youtube.com/favicon.ico',
};

export const YOUTUBE_STUDIO: LinkData = {
    title: 'YouTube Studio',
    url: 'https://studio.youtube.com/channel/UCauGG97chgNr-BwoQpKTytg',
    description: 'Manage your YouTube channel and content',
    icon: 'https://www.youtube.com/favicon.ico',
};

export const GITHUB_REPOSITORIES: LinkData = {
    title: 'GitHub Repositories',
    url: 'https://github.com/danielnachumdev?tab=repositories',
    description: 'View your GitHub repositories and projects',
    icon: 'https://github.com/favicon.ico',
};

export const GMAIL: LinkData = {
    title: 'Gmail',
    url: 'https://mail.google.com',
    description: 'Access your Gmail inbox',
    icon: 'https://mail.google.com/favicon.ico',
};

export const GOOGLE_DRIVE: LinkData = {
    title: 'Google Drive',
    url: 'https://drive.google.com',
    description: 'Access your Google Drive files',
    icon: 'https://drive.google.com/favicon.ico',
};

export const GOOGLE_CALENDAR: LinkData = {
    title: 'Calendar',
    url: 'https://calendar.google.com',
    description: 'View your Google Calendar',
    icon: 'https://calendar.google.com/favicon.ico',
};

// 2D array structure using card constants for easier management
export const commonLinksData: LinkData[][] = [
    // Row 1
    [
        YOUTUBE_SUBSCRIPTIONS,
        YOUTUBE_STUDIO,
        GITHUB_REPOSITORIES,
        GITHUB_REPOSITORIES,
        GITHUB_REPOSITORIES,
        GITHUB_REPOSITORIES,
        GITHUB_REPOSITORIES,
        GITHUB_REPOSITORIES,
    ],
    // Row 2
    [
        GMAIL,
        GOOGLE_DRIVE,
        GOOGLE_CALENDAR,
    ],
];
