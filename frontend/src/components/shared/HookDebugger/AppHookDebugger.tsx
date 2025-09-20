import { useEffect } from 'react';
import { HookDebuggerPanel } from './HookDebuggerPanel';
import { useHookDebugger, createDebugInfo } from '../../../hooks/useHookDebugger';
import { useScreenSize } from '../../../hooks/useScreenSize';
import { useLinkCardSize } from '../../../hooks/useLinkCardSize';
import { useSettings } from '../../../hooks/useSettings';
import { useBackendStatus } from '../../../hooks/useBackendStatus';
import { useChromeProfiles } from '../../../hooks/useChromeProfiles';

export interface AppHookDebuggerProps {
    /** Whether the debugger is visible by default */
    defaultVisible?: boolean;
    /** Whether the debugger is expanded by default */
    defaultExpanded?: boolean;
    /** Position of the debug panel */
    position?: 'top-right' | 'top-left' | 'bottom-right' | 'bottom-left';
    /** Custom title for the debug panel */
    title?: string;
}

/**
 * Encapsulated component that automatically registers and debugs all app hooks.
 * This component handles all the hook registration logic internally.
 */
export function AppHookDebugger({
    defaultVisible = false,
    defaultExpanded = false,
    position = 'bottom-right',
    title = 'App Hook Debugger',
}: AppHookDebuggerProps) {
    const hookDebugger = useHookDebugger();

    // Get all the hooks
    const screenSize = useScreenSize();
    const linkCardSize = useLinkCardSize();
    const settings = useSettings();
    const backendStatus = useBackendStatus();
    const { profiles: chromeProfiles, openUrlInProfile } = useChromeProfiles();

    // Register hooks for debugging
    useEffect(() => {
        hookDebugger.addHook(createDebugInfo(
            'chrome-profiles',
            'useChromeProfiles',
            { profiles: chromeProfiles, openUrlInProfile },
            {
                description: 'Manages Chrome browser profiles for opening URLs in different contexts. Returns available profiles and a function to open URLs in specific profiles.',
                formatter: (state) => `${state.profiles.length} profiles available`,
                metadata: {
                    profileNames: chromeProfiles.map(p => p.name),
                    hasOpenFunction: typeof openUrlInProfile === 'function'
                }
            }
        ));

        hookDebugger.addHook(createDebugInfo(
            'screen-size',
            'useScreenSize',
            screenSize,
            {
                description: 'Tracks current screen dimensions and provides responsive breakpoint information. Automatically updates on window resize with debouncing.',
                formatter: (state) => `${state.width}x${state.height} (${state.isMobile ? 'Mobile' : state.isTablet ? 'Tablet' : 'Desktop'})`,
                metadata: {
                    breakpoints: {
                        mobile: '< 768px',
                        tablet: '768px - 1024px',
                        desktop: '>= 1024px'
                    }
                }
            }
        ));

        hookDebugger.addHook(createDebugInfo(
            'link-card-size',
            'useLinkCardSize',
            linkCardSize,
            {
                description: 'Determines the appropriate size for link cards based on current screen width. Uses responsive breakpoints to return small, medium, or large size.',
                formatter: (state) => `Size: ${state}`,
                metadata: {
                    breakpoints: {
                        small: '< 768px',
                        medium: '768px - 1200px',
                        large: '>= 1200px'
                    }
                }
            }
        ));

        hookDebugger.addHook(createDebugInfo(
            'settings',
            'useSettings',
            settings,
            {
                description: 'Manages application settings including widgets, search engine preferences, and Chrome profiles. Provides loading state, error handling, and refresh functionality.',
                formatter: (state) => `Loading: ${state.loading}, Error: ${state.error ? 'Yes' : 'No'}`,
                showRefresh: true,
                onRefresh: settings.refresh,
                metadata: {
                    lastUpdated: new Date().toISOString(),
                    settingsCount: Object.keys(settings.settings).length
                }
            }
        ));

        hookDebugger.addHook(createDebugInfo(
            'backend-status',
            'useBackendStatus',
            backendStatus,
            {
                description: 'Monitors the current status of the backend API connection. Tracks connection state, retry attempts, and provides real-time connectivity information.',
                formatter: (state) => `Status: ${state.status}, Connected: ${state.isConnected ? 'Yes' : 'No'}`,
                metadata: {
                    lastChecked: new Date().toISOString(),
                    retryCount: 0
                }
            }
        ));
    }, [hookDebugger, chromeProfiles, openUrlInProfile, screenSize, linkCardSize, settings, backendStatus]);

    // Update hook states when they change
    useEffect(() => {
        hookDebugger.updateHookState('chrome-profiles', { profiles: chromeProfiles, openUrlInProfile });
    }, [hookDebugger, chromeProfiles, openUrlInProfile]);

    useEffect(() => {
        hookDebugger.updateHookState('screen-size', screenSize);
    }, [hookDebugger, screenSize]);

    useEffect(() => {
        hookDebugger.updateHookState('link-card-size', linkCardSize);
    }, [hookDebugger, linkCardSize]);

    useEffect(() => {
        hookDebugger.updateHookState('settings', settings);
    }, [hookDebugger, settings]);

    useEffect(() => {
        hookDebugger.updateHookState('backend-status', backendStatus);
    }, [hookDebugger, backendStatus]);

    return (
        <HookDebuggerPanel
            hooks={hookDebugger.getHooks()}
            defaultVisible={defaultVisible}
            defaultExpanded={defaultExpanded}
            title={title}
            position={position}
        />
    );
}
