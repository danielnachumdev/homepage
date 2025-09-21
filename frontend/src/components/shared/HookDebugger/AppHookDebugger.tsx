import { useEffect, useRef } from 'react';
import { HookDebuggerPanel } from './HookDebuggerPanel';
import { useHookDebugger, createDebugInfo } from '../../../hooks/useHookDebugger';
import { useScreenSize } from '../../../hooks/useScreenSize';
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
    const hooksRegistered = useRef(false);

    // Get all the hooks
    const screenSize = useScreenSize();
    const settings = useSettings();
    const backendStatus = useBackendStatus();
    const { profiles: chromeProfiles, openUrlInProfile } = useChromeProfiles();

    // Register hooks for debugging - only run once on mount
    useEffect(() => {
        if (hooksRegistered.current) {
            return; // Already registered, don't run again
        }


        // Register all hooks at once to avoid multiple effect runs
        const hooksToRegister = [
            createDebugInfo(
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
            ),
            createDebugInfo(
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
            ),
            createDebugInfo(
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
            ),
            createDebugInfo(
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
            )
        ];

        // Register all hooks
        hooksToRegister.forEach(hookInfo => {
            hookDebugger.addHook(hookInfo);
        });

        hooksRegistered.current = true;
    }, []); // Empty dependency array - only run once on mount

    // Update hook states when they change
    useEffect(() => {
        hookDebugger.updateHookState('chrome-profiles', { profiles: chromeProfiles, openUrlInProfile });
    }, [chromeProfiles, openUrlInProfile]);

    useEffect(() => {
        hookDebugger.updateHookState('screen-size', screenSize);
    }, [screenSize]);

    useEffect(() => {
        hookDebugger.updateHookState('settings', settings);
    }, [settings.settings, settings.loading, settings.error]);

    useEffect(() => {
        hookDebugger.updateHookState('backend-status', backendStatus);
    }, [backendStatus]);

    return (
        <HookDebuggerPanel
            hooks={hookDebugger.hooks}
            defaultVisible={defaultVisible}
            defaultExpanded={defaultExpanded}
            title={title}
            position={position}
        />
    );
}
