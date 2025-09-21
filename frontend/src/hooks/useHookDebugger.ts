import { useState, useCallback, useRef } from 'react';
import { useComponentLogger } from './useLogger';

export interface HookDebugInfo {
    id: string;
    name: string;
    state: any;
    description?: string;
    formatter?: (state: any) => string;
    showRefresh?: boolean;
    onRefresh?: () => void;
    metadata?: Record<string, any>;
}

export interface UseHookDebuggerReturn {
    /** Add a hook to debug */
    addHook: (hookInfo: HookDebugInfo) => void;
    /** Remove a hook from debugging */
    removeHook: (hookId: string) => void;
    /** Update a hook's state */
    updateHookState: (hookId: string, state: any) => void;
    /** Get all registered hooks */
    getHooks: () => HookDebugInfo[];
    /** All registered hooks (direct state access) */
    hooks: HookDebugInfo[];
    /** Clear all hooks */
    clearHooks: () => void;
    /** Toggle debug panel visibility */
    toggleVisibility: () => void;
    /** Whether debug panel is visible */
    isVisible: boolean;
}

/**
 * Custom hook for managing hook debugging state.
 * Provides utilities to register, update, and manage hooks for debugging.
 */
export function useHookDebugger(): UseHookDebuggerReturn {
    const logger = useComponentLogger('useHookDebugger');
    logger.debug('Hook initialized');

    const [hooks, setHooks] = useState<HookDebugInfo[]>([]);
    const [isVisible, setIsVisible] = useState(false);

    // Use ref to track current hooks for stable getHooks function
    const hooksRef = useRef<HookDebugInfo[]>([]);

    // Update ref whenever hooks change
    hooksRef.current = hooks;

    // Use ref to store stable references to functions
    const addHookRef = useRef((hookInfo: HookDebugInfo) => {
        logger.debug('addHook called', { hookId: hookInfo.id });
        setHooks(prev => {
            const existingIndex = prev.findIndex(hook => hook.id === hookInfo.id);
            if (existingIndex >= 0) {
                logger.debug('Updating existing hook', { hookId: hookInfo.id });
                // Update existing hook
                const updated = [...prev];
                updated[existingIndex] = { ...updated[existingIndex], ...hookInfo };
                return updated;
            } else {
                logger.debug('Adding new hook', { hookId: hookInfo.id });
                // Add new hook
                return [...prev, hookInfo];
            }
        });
    });

    const removeHookRef = useRef((hookId: string) => {
        logger.debug('removeHook called', { hookId });
        setHooks(prev => prev.filter(hook => hook.id !== hookId));
    });

    const updateHookStateRef = useRef((hookId: string, state: any) => {
        logger.debug('updateHookState called', { hookId });
        setHooks(prev =>
            prev.map(hook =>
                hook.id === hookId
                    ? { ...hook, state }
                    : hook
            )
        );
    });

    const clearHooksRef = useRef(() => {
        logger.debug('clearHooks called');
        setHooks([]);
    });

    const toggleVisibilityRef = useRef(() => {
        logger.debug('toggleVisibility called');
        setIsVisible(prev => !prev);
    });

    const addHook = useCallback((hookInfo: HookDebugInfo) => {
        addHookRef.current(hookInfo);
    }, []);

    const removeHook = useCallback((hookId: string) => {
        removeHookRef.current(hookId);
    }, []);

    const updateHookState = useCallback((hookId: string, state: any) => {
        updateHookStateRef.current(hookId, state);
    }, []);

    const getHooks = useCallback(() => hooksRef.current, []);

    const clearHooks = useCallback(() => {
        clearHooksRef.current();
    }, []);

    const toggleVisibility = useCallback(() => {
        toggleVisibilityRef.current();
    }, []);

    return {
        addHook,
        removeHook,
        updateHookState,
        getHooks,
        hooks,
        clearHooks,
        toggleVisibility,
        isVisible,
    };
}

/**
 * Higher-order function that wraps a hook to automatically debug it.
 * 
 * @param hookFunction - The hook function to wrap
 * @param debugInfo - Debug information for the hook
 * @returns Wrapped hook that automatically registers itself for debugging
 */
export function withDebugging<T extends (...args: any[]) => any>(
    hookFunction: T,
    debugInfo: Omit<HookDebugInfo, 'state'>
): T {
    return ((...args: Parameters<T>) => {
        const result = hookFunction(...args);

        // Register the hook for debugging
        // Note: This is a simplified version - in a real implementation,
        // you'd need to access the debugger context
        console.log(`[Hook Debug] ${debugInfo.name}:`, result);

        return result;
    }) as T;
}

/**
 * Utility function to create debug info for a hook
 */
export function createDebugInfo(
    id: string,
    name: string,
    state: any,
    options: Partial<Omit<HookDebugInfo, 'id' | 'name' | 'state'>> = {}
): HookDebugInfo {
    return {
        id,
        name,
        state,
        ...options,
    };
}
