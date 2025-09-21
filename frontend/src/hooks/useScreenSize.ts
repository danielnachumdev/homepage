import { useState, useEffect } from 'react';
import { useComponentLogger } from './useLogger';

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
    const logger = useComponentLogger('useScreenSize');
    logger.debug('Hook initialized');

    const { debounceMs = 100 } = options;
    const [screenSize, setScreenSize] = useState<ScreenSize>(() => {
        logger.debug('Initializing screen size');
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
        logger.debug('Initial screen size', { width, height });
        return result;
    });

    useEffect(() => {
        let timeoutId: number;

        const handleResize = () => {
            logger.debug('Resize event triggered');
            clearTimeout(timeoutId);
            timeoutId = setTimeout(() => {
                const width = window.innerWidth;
                const height = window.innerHeight;
                logger.debug('Updating screen size', { width, height });

                setScreenSize({
                    width,
                    height,
                    isMobile: width < 768,
                    isTablet: width >= 768 && width < 1024,
                    isDesktop: width >= 1024,
                });
            }, debounceMs);
        };

        logger.debug('Setting up resize listener');
        window.addEventListener('resize', handleResize);
        return () => {
            logger.debug('Cleaning up resize listener');
            window.removeEventListener('resize', handleResize);
            clearTimeout(timeoutId);
        };
    }, [debounceMs]);

    logger.debug('Returning screen size', { width: screenSize.width, height: screenSize.height });
    return screenSize;
}
