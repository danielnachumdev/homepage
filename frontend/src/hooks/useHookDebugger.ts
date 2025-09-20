import { useState, useCallback } from 'react';

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
    const [hooks, setHooks] = useState<HookDebugInfo[]>([]);
    const [isVisible, setIsVisible] = useState(false);

    const addHook = useCallback((hookInfo: HookDebugInfo) => {
        setHooks(prev => {
            const existingIndex = prev.findIndex(hook => hook.id === hookInfo.id);
            if (existingIndex >= 0) {
                // Update existing hook
                const updated = [...prev];
                updated[existingIndex] = { ...updated[existingIndex], ...hookInfo };
                return updated;
            } else {
                // Add new hook
                return [...prev, hookInfo];
            }
        });
    }, []);

    const removeHook = useCallback((hookId: string) => {
        setHooks(prev => prev.filter(hook => hook.id !== hookId));
    }, []);

    const updateHookState = useCallback((hookId: string, state: any) => {
        setHooks(prev =>
            prev.map(hook =>
                hook.id === hookId
                    ? { ...hook, state }
                    : hook
            )
        );
    }, []);

    const getHooks = useCallback(() => hooks, [hooks]);

    const clearHooks = useCallback(() => {
        setHooks([]);
    }, []);

    const toggleVisibility = useCallback(() => {
        setIsVisible(prev => !prev);
    }, []);

    return {
        addHook,
        removeHook,
        updateHookState,
        getHooks,
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
