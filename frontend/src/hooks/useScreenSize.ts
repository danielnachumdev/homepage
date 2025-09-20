import { useState, useEffect } from 'react';

export interface UseScreenSizeOptions {
    debounceMs?: number;
}

export interface ScreenSize {
    width: number;
    height: number;
    isMobile: boolean;
    isTablet: boolean;
    isDesktop: boolean;
}

export function useScreenSize(options: UseScreenSizeOptions = {}): ScreenSize {
    const { debounceMs = 100 } = options;
    const [screenSize, setScreenSize] = useState<ScreenSize>(() => {
        if (typeof window === 'undefined') {
            return { width: 0, height: 0, isMobile: false, isTablet: false, isDesktop: false };
        }

        const width = window.innerWidth;
        const height = window.innerHeight;
        return {
            width,
            height,
            isMobile: width < 768,
            isTablet: width >= 768 && width < 1024,
            isDesktop: width >= 1024,
        };
    });

    useEffect(() => {
        let timeoutId: number;

        const handleResize = () => {
            clearTimeout(timeoutId);
            timeoutId = setTimeout(() => {
                const width = window.innerWidth;
                const height = window.innerHeight;

                setScreenSize({
                    width,
                    height,
                    isMobile: width < 768,
                    isTablet: width >= 768 && width < 1024,
                    isDesktop: width >= 1024,
                });
            }, debounceMs);
        };

        window.addEventListener('resize', handleResize);
        return () => {
            window.removeEventListener('resize', handleResize);
            clearTimeout(timeoutId);
        };
    }, [debounceMs]);

    return screenSize;
}
