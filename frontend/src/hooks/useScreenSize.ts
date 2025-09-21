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
    console.log(`[PERF] useScreenSize: Hook initialized at ${new Date().toISOString()}`);

    const { debounceMs = 100 } = options;
    const [screenSize, setScreenSize] = useState<ScreenSize>(() => {
        console.log(`[PERF] useScreenSize: Initializing screen size at ${new Date().toISOString()}`);
        if (typeof window === 'undefined') {
            return { width: 0, height: 0, isMobile: false, isTablet: false, isDesktop: false };
        }

        const width = window.innerWidth;
        const height = window.innerHeight;
        const result = {
            width,
            height,
            isMobile: width < 768,
            isTablet: width >= 768 && width < 1024,
            isDesktop: width >= 1024,
        };
        console.log(`[PERF] useScreenSize: Initial screen size: ${width}x${height} at ${new Date().toISOString()}`);
        return result;
    });

    useEffect(() => {
        let timeoutId: number;

        const handleResize = () => {
            console.log(`[PERF] useScreenSize: Resize event triggered at ${new Date().toISOString()}`);
            clearTimeout(timeoutId);
            timeoutId = setTimeout(() => {
                const width = window.innerWidth;
                const height = window.innerHeight;
                console.log(`[PERF] useScreenSize: Updating screen size to ${width}x${height} at ${new Date().toISOString()}`);

                setScreenSize({
                    width,
                    height,
                    isMobile: width < 768,
                    isTablet: width >= 768 && width < 1024,
                    isDesktop: width >= 1024,
                });
            }, debounceMs);
        };

        console.log(`[PERF] useScreenSize: Setting up resize listener at ${new Date().toISOString()}`);
        window.addEventListener('resize', handleResize);
        return () => {
            console.log(`[PERF] useScreenSize: Cleaning up resize listener at ${new Date().toISOString()}`);
            window.removeEventListener('resize', handleResize);
            clearTimeout(timeoutId);
        };
    }, [debounceMs]);

    console.log(`[PERF] useScreenSize: Returning screen size ${screenSize.width}x${screenSize.height} at ${new Date().toISOString()}`);
    return screenSize;
}
