/**
 * Base interface for link data without ID (used for input/creation)
 */
export interface LinkData {
    title: string;
    url: string;
    description?: string;
    icon?: string;
}

/**
 * Complete link item with auto-generated ID (used for display/state)
 */
export interface LinkItem extends LinkData {
    id: string;
}

/**
 * Factory function to create a LinkItem from LinkData with auto-generated ID
 */
export function createLinkItem(data: LinkData): LinkItem {
    return {
        id: generateLinkId(data),
        ...data,
    };
}

/**
 * Generate a unique ID for a link based on its properties
 */
function generateLinkId(data: LinkData): string {
    // Create a URL-friendly ID from the title
    const baseId = data.title
        .toLowerCase()
        .replace(/[^a-z0-9\s-]/g, '') // Remove special characters except spaces and hyphens
        .replace(/\s+/g, '-') // Replace spaces with hyphens
        .replace(/-+/g, '-') // Replace multiple hyphens with single hyphen
        .replace(/^-|-$/g, ''); // Remove leading/trailing hyphens

    // Add a hash of the URL to ensure uniqueness
    const urlHash = data.url
        .split('')
        .reduce((hash, char) => {
            const code = char.charCodeAt(0);
            hash = ((hash << 5) - hash) + code;
            return hash & hash; // Convert to 32-bit integer
        }, 0)
        .toString(36)
        .slice(-4);

    return `${baseId}-${urlHash}`;
}

/**
 * Type guard to check if an object is a valid LinkData
 */
export function isLinkData(obj: any): obj is LinkData {
    return (
        typeof obj === 'object' &&
        obj !== null &&
        typeof obj.title === 'string' &&
        typeof obj.url === 'string' &&
        (obj.description === undefined || typeof obj.description === 'string') &&
        (obj.icon === undefined || typeof obj.icon === 'string')
    );
}

/**
 * Type guard to check if an object is a valid LinkItem
 */
export function isLinkItem(obj: any): obj is LinkItem {
    return (
        isLinkData(obj) &&
        'id' in obj &&
        typeof obj.id === 'string' &&
        obj.id.length > 0
    );
}

/**
 * Utility type for creating link collections
 */
export type LinkCollection = LinkItem[];

/**
 * Utility type for creating link data collections (before ID generation)
 */
export type LinkDataCollection = LinkData[];
