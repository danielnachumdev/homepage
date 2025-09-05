import { useCallback, useMemo } from 'react';
import { useSettings } from './useSettings';
import { searchEngineManager, type SearchEngineStrategy } from '../components/Search/SearchEngineStrategy';

interface UseSearchEngineReturn {
    // Search engine specific data
    selectedEngine: SearchEngineStrategy;
    availableEngines: SearchEngineStrategy[];
    setSelectedEngine: (engineName: string) => Promise<void>;

    // Inherited from useSettings
    loading: boolean;
    error: string | null;
    refresh: () => Promise<void>;
}

export function useSearchEngine(): UseSearchEngineReturn {
    const { settings, updateSetting, loading, error, refresh } = useSettings();

    // Memoize expensive computations
    const selectedEngine = useMemo(() =>
        searchEngineManager.getStrategy(settings.searchEngine.selectedEngine),
        [settings.searchEngine.selectedEngine]
    );

    const availableEngines = useMemo(() =>
        searchEngineManager.getAllStrategies(),
        []
    );

    const setSelectedEngine = useCallback(async (engineName: string) => {
        try {
            await updateSetting('searchEngine', 'selectedEngine', engineName);
        } catch (err) {
            console.error('Failed to update search engine setting:', err);
            throw err;
        }
    }, [updateSetting]);

    return {
        // Search engine specific data
        selectedEngine,
        availableEngines,
        setSelectedEngine,

        // Inherited from useSettings
        loading,
        error,
        refresh,
    };
}
