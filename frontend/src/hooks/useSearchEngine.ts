import { useCallback } from 'react';
import { useSettings } from '../contexts/SettingsContext';
import { searchEngineManager, type SearchEngineStrategy } from '../components/Search/SearchEngineStrategy';

interface UseSearchEngineReturn {
    selectedEngine: SearchEngineStrategy;
    availableEngines: SearchEngineStrategy[];
    setSelectedEngine: (engineName: string) => Promise<void>;
    loading: boolean;
    error: string | null;
}

export function useSearchEngine(): UseSearchEngineReturn {
    const { settings, updateSetting, loading, error } = useSettings();

    // Get the current selected engine strategy
    const selectedEngine = searchEngineManager.getStrategy(settings.searchEngine.selectedEngine);

    // Get all available engines
    const availableEngines = searchEngineManager.getAllStrategies();

    const setSelectedEngine = useCallback(async (engineName: string) => {
        try {
            await updateSetting('searchEngine', 'selectedEngine', engineName);
        } catch (err) {
            console.error('Failed to update search engine setting:', err);
            throw err;
        }
    }, [updateSetting]);

    return {
        selectedEngine,
        availableEngines,
        setSelectedEngine,
        loading,
        error,
    };
}
