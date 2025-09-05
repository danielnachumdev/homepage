import React, { createContext, useContext, useCallback } from 'react';
import { useChromeProfiles } from '../hooks/useChromeProfiles';

interface ChromeProfilesContextType {
    refreshProfiles: () => Promise<void>;
}

const ChromeProfilesContext = createContext<ChromeProfilesContextType | undefined>(undefined);

export const useChromeProfilesContext = () => {
    const context = useContext(ChromeProfilesContext);
    if (!context) {
        throw new Error('useChromeProfilesContext must be used within a ChromeProfilesProvider');
    }
    return context;
};

interface ChromeProfilesProviderProps {
    children: React.ReactNode;
}

export const ChromeProfilesProvider: React.FC<ChromeProfilesProviderProps> = ({ children }) => {
    const { refreshProfiles } = useChromeProfiles();

    const contextValue: ChromeProfilesContextType = {
        refreshProfiles,
    };

    return (
        <ChromeProfilesContext.Provider value={contextValue}>
            {children}
        </ChromeProfilesContext.Provider>
    );
};
