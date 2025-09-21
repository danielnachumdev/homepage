export interface LinkData {
    title: string;
    icon: string | string[]; // URL, icon name, or array of fallback URLs
    description?: string; // Optional description
    url: string;
    chromeProfileEnabled?: boolean; // Defaults to false
    chromeProfiles?: string[]; // Available Chrome profiles for this link
}

export interface LinkCardProps {
    link: LinkData;
    onLinkClick: (link: LinkData) => void;
    onChromeProfileClick?: (link: LinkData, profile: string) => void;
}

export interface LinksSectionProps {
    links: LinkData[];
    onLinkClick: (link: LinkData) => void;
    onChromeProfileClick?: (link: LinkData, profile: string) => void;
}
