import { useScreenSize } from './useScreenSize';

export type LinkCardSize = 'small' | 'medium' | 'large';

export interface UseLinkCardSizeOptions {
    breakpoints?: {
        small: number;
        medium: number;
        large: number;
    };
    defaultSize?: LinkCardSize;
}

const DEFAULT_BREAKPOINTS = {
    small: 768,
    medium: 1200,
    large: 1400,
};

export function useLinkCardSize(options: UseLinkCardSizeOptions = {}): LinkCardSize {
    const { breakpoints = DEFAULT_BREAKPOINTS, defaultSize = 'medium' } = options;
    const { width } = useScreenSize();

    if (width === 0) {
        return defaultSize; // SSR fallback
    }

    if (width >= breakpoints.large) {
        return 'large';
    } else if (width >= breakpoints.medium) {
        return 'medium';
    } else {
        return 'small';
    }
}
