export interface LinkData {
    id: string;
    title: string;
    icon: string; // URL or icon name
    description: string;
    url: string;
    chromeProfileEnabled?: boolean;
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
