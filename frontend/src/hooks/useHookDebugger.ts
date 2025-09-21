import { useState, useCallback, useRef } from 'react';

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
    console.log(`[PERF] useHookDebugger: Hook initialized at ${new Date().toISOString()}`);

    const [hooks, setHooks] = useState<HookDebugInfo[]>([]);
    const [isVisible, setIsVisible] = useState(false);

    // Use ref to store stable references to functions
    const addHookRef = useRef((hookInfo: HookDebugInfo) => {
        console.log(`[PERF] useHookDebugger: addHook called for ${hookInfo.id} at ${new Date().toISOString()}`);
        setHooks(prev => {
            const existingIndex = prev.findIndex(hook => hook.id === hookInfo.id);
            if (existingIndex >= 0) {
                console.log(`[PERF] useHookDebugger: Updating existing hook ${hookInfo.id} at ${new Date().toISOString()}`);
                // Update existing hook
                const updated = [...prev];
                updated[existingIndex] = { ...updated[existingIndex], ...hookInfo };
                return updated;
            } else {
                console.log(`[PERF] useHookDebugger: Adding new hook ${hookInfo.id} at ${new Date().toISOString()}`);
                // Add new hook
                return [...prev, hookInfo];
            }
        });
    });

    const removeHookRef = useRef((hookId: string) => {
        setHooks(prev => prev.filter(hook => hook.id !== hookId));
    });

    const updateHookStateRef = useRef((hookId: string, state: any) => {
        console.log(`[PERF] useHookDebugger: updateHookState called for ${hookId} at ${new Date().toISOString()}`);
        setHooks(prev =>
            prev.map(hook =>
                hook.id === hookId
                    ? { ...hook, state }
                    : hook
            )
        );
    });

    const clearHooksRef = useRef(() => {
        setHooks([]);
    });

    const toggleVisibilityRef = useRef(() => {
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

    const getHooks = useCallback(() => hooks, [hooks]);

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
