import React, { createContext, useContext, ReactNode } from 'react';
import { useSettingsStore } from '../lib/stores/SettingsStore';
import type { UseSettingsReturn } from '../types/settings';

interface SettingsContextType extends UseSettingsReturn { }

const SettingsContext = createContext<SettingsContextType | undefined>(undefined);

interface SettingsProviderProps {
    children: ReactNode;
}

export function SettingsProvider({ children }: SettingsProviderProps) {
    const settings = useSettingsStore();

    return (
        <SettingsContext.Provider value={settings}>
            {children}
        </SettingsContext.Provider>
    );
}

export function useSettingsContext(): UseSettingsReturn {
    const context = useContext(SettingsContext);
    if (context === undefined) {
        throw new Error('useSettingsContext must be used within a SettingsProvider');
    }
    return context;
}

// Export the hook with a more convenient name
export const useAppSettings = useSettingsContext;
