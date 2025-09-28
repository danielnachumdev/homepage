import { getLogger } from '../logger';

export interface PerformanceMetrics {
    renderCount: number;
    lastRenderTime: number;
    apiCallCount: number;
    lastApiCallTime: number;
    componentName: string;
}

class PerformanceMonitor {
    private static instance: PerformanceMonitor;
    private metrics: Map<string, PerformanceMetrics> = new Map();
    private logger = getLogger('PerformanceMonitor');

    static getInstance(): PerformanceMonitor {
        if (!PerformanceMonitor.instance) {
            PerformanceMonitor.instance = new PerformanceMonitor();
        }
        return PerformanceMonitor.instance;
    }

    trackRender(componentName: string): void {
        const now = Date.now();
        const existing = this.metrics.get(componentName);

        if (existing) {
            existing.renderCount += 1;
            existing.lastRenderTime = now;

            // Log if component is re-rendering frequently
            if (existing.renderCount > 5) {
                this.logger.warning(`[PERF] ${componentName} has re-rendered ${existing.renderCount} times`, {
                    renderCount: existing.renderCount,
                    timeSinceLastRender: now - existing.lastRenderTime,
                    componentName
                });
            } else {
                this.logger.debug(`[PERF] ${componentName} rendered`, {
                    renderCount: existing.renderCount,
                    componentName
                });
            }
        } else {
            this.metrics.set(componentName, {
                renderCount: 1,
                lastRenderTime: now,
                apiCallCount: 0,
                lastApiCallTime: 0,
                componentName
            });
            this.logger.debug(`[PERF] ${componentName} first render`, { componentName });
        }
    }

    trackApiCall(componentName: string, endpoint: string): void {
        const now = Date.now();
        const existing = this.metrics.get(componentName);

        if (existing) {
            existing.apiCallCount += 1;
            existing.lastApiCallTime = now;

            this.logger.debug(`[PERF] ${componentName} API call`, {
                endpoint,
                apiCallCount: existing.apiCallCount,
                componentName
            });
        } else {
            this.metrics.set(componentName, {
                renderCount: 0,
                lastRenderTime: 0,
                apiCallCount: 1,
                lastApiCallTime: now,
                componentName
            });
        }
    }

    getMetrics(componentName?: string): PerformanceMetrics | Map<string, PerformanceMetrics> {
        if (componentName) {
            return this.metrics.get(componentName) || {
                renderCount: 0,
                lastRenderTime: 0,
                apiCallCount: 0,
                lastApiCallTime: 0,
                componentName
            };
        }
        return new Map(this.metrics);
    }

    resetMetrics(componentName?: string): void {
        if (componentName) {
            this.metrics.delete(componentName);
        } else {
            this.metrics.clear();
        }
    }

    logSummary(): void {
        this.logger.info('[PERF] Performance Summary', {
            metrics: Array.from(this.metrics.entries()).map(([name, metrics]) => ({
                component: name,
                renders: metrics.renderCount,
                apiCalls: metrics.apiCallCount
            }))
        });
    }
}

export const performanceMonitor = PerformanceMonitor.getInstance();
