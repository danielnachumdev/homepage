import { useRef, useEffect } from 'react';
import { getLogger } from '../lib/logger';
import { performanceMonitor, type PerformanceMetrics } from '../lib/performance/PerformanceMonitor';

export interface UsePerformanceTrackingReturn {
    trackApiCall: (endpoint: string) => void;
    renderCount: number;
    apiCallCount: number;
}

// React hook for tracking component performance
export function usePerformanceTracking(componentName: string): UsePerformanceTrackingReturn {
    const renderCountRef = useRef(0);
    const apiCallCountRef = useRef(0);

    // Track render
    renderCountRef.current += 1;
    performanceMonitor.trackRender(componentName);

    // Track API calls
    const trackApiCall = (endpoint: string) => {
        apiCallCountRef.current += 1;
        performanceMonitor.trackApiCall(componentName, endpoint);
    };

    // Log performance summary on unmount
    useEffect(() => {
        return () => {
            const metrics = performanceMonitor.getMetrics(componentName) as PerformanceMetrics;
            if (metrics.renderCount > 10 || metrics.apiCallCount > 5) {
                const logger = getLogger('PerformanceMonitor');
                logger.warning(`[PERF] ${componentName} performance summary`, {
                    totalRenders: metrics.renderCount,
                    totalApiCalls: metrics.apiCallCount,
                    componentName
                });
            }
        };
    }, [componentName]);

    return { trackApiCall, renderCount: renderCountRef.current, apiCallCount: apiCallCountRef.current };
}
