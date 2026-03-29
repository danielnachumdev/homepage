export interface LinkData {
    title: string;
    icon: string | string[]; // URL, icon name, or array of fallback URLs
    description?: string; // Optional description
    url: string;
    chromeProfileEnabled?: boolean; // Defaults to false
    chromeProfiles?: string[]; // Available Chrome profiles for this link
    /** When set, card splits: main link on the left, sublinks stacked (scroll if more than 3). */
    sublinks?: LinkSubItem[];
}

/**
 * Same shape as LinkData for reuse (e.g. spread a full link or build a minimal object).
 * Only `title`, `url`, and `icon` are required; everything else matches LinkData but optional.
 */
export type LinkSubItem = Required<Pick<LinkData, 'title' | 'url' | 'icon'>> &
    Partial<Omit<LinkData, 'title' | 'url' | 'icon'>>;

export interface LinkCardProps {
    link: LinkData;
    onLinkClick: (link: LinkData) => void;
    onChromeProfileClick?: (link: LinkData, profile: string) => void;
    onSublinkClick?: (parent: LinkData, sub: LinkSubItem) => void;
}

export interface LinksSectionProps {
    links: LinkData[];
    onLinkClick: (link: LinkData) => void;
    onChromeProfileClick?: (link: LinkData, profile: string) => void;
    onSublinkClick?: (parent: LinkData, sub: LinkSubItem) => void;
}
