import type { LinkData } from '../types/link';

export const links: LinkData[] = [
    {
        id: 'github',
        title: 'GitHub',
        icon: 'https://github.com/favicon.ico',
        description: 'Code repository and version control platform',
        url: 'https://github.com',
        chromeProfileEnabled: true,
        chromeProfiles: ['Personal', 'Work', 'Development']
    },
    {
        id: 'stackoverflow',
        title: 'Stack Overflow',
        icon: 'https://stackoverflow.com/favicon.ico',
        description: 'Programming questions and answers community',
        url: 'https://stackoverflow.com',
        chromeProfileEnabled: true,
        chromeProfiles: ['Personal', 'Work']
    },
    {
        id: 'mdn',
        title: 'MDN Web Docs',
        icon: 'https://developer.mozilla.org/favicon.ico',
        description: 'Comprehensive documentation for web technologies',
        url: 'https://developer.mozilla.org',
        chromeProfileEnabled: false
    },
    {
        id: 'npm',
        title: 'npm',
        icon: 'https://www.npmjs.com/favicon.ico',
        description: 'Package manager for JavaScript and Node.js',
        url: 'https://www.npmjs.com',
        chromeProfileEnabled: true,
        chromeProfiles: ['Personal', 'Work', 'Development']
    },
    {
        id: 'figma',
        title: 'Figma',
        icon: 'https://www.figma.com/favicon.ico',
        description: 'Collaborative interface design tool',
        url: 'https://www.figma.com',
        chromeProfileEnabled: true,
        chromeProfiles: ['Work', 'Design']
    },
    {
        id: 'notion',
        title: 'Notion',
        icon: 'https://www.notion.so/favicon.ico',
        description: 'All-in-one workspace for notes, docs, and collaboration',
        url: 'https://www.notion.so',
        chromeProfileEnabled: true,
        chromeProfiles: ['Personal', 'Work']
    },
    {
        id: 'youtube',
        title: 'YouTube',
        icon: 'https://www.youtube.com/favicon.ico',
        description: 'Video sharing and streaming platform',
        url: 'https://www.youtube.com',
        chromeProfileEnabled: false
    },
    {
        id: 'reddit',
        title: 'Reddit',
        icon: 'https://www.reddit.com/favicon.ico',
        description: 'Social news aggregation and discussion website',
        url: 'https://www.reddit.com',
        chromeProfileEnabled: false
    }
];
