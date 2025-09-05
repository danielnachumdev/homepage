export interface SearchEngineStrategy {
    name: string;
    logo: string;
    buildSearchUrl(query: string): string;
}

export class GoogleSearchStrategy implements SearchEngineStrategy {
    name = 'Google';
    logo = 'https://www.google.com/favicon.ico';

    buildSearchUrl(query: string): string {
        const encodedQuery = encodeURIComponent(query);
        return `https://www.google.com/search?q=${encodedQuery}`;
    }
}

export class BingSearchStrategy implements SearchEngineStrategy {
    name = 'Bing';
    logo = 'https://www.bing.com/favicon.ico';

    buildSearchUrl(query: string): string {
        const encodedQuery = encodeURIComponent(query);
        return `https://www.bing.com/search?q=${encodedQuery}`;
    }
}

export class DuckDuckGoSearchStrategy implements SearchEngineStrategy {
    name = 'DuckDuckGo';
    logo = 'https://duckduckgo.com/favicon.ico';

    buildSearchUrl(query: string): string {
        const encodedQuery = encodeURIComponent(query);
        return `https://duckduckgo.com/?q=${encodedQuery}`;
    }
}

export class YahooSearchStrategy implements SearchEngineStrategy {
    name = 'Yahoo';
    logo = 'https://search.yahoo.com/favicon.ico';

    buildSearchUrl(query: string): string {
        const encodedQuery = encodeURIComponent(query);
        return `https://search.yahoo.com/search?p=${encodedQuery}`;
    }
}

export class SearchEngineManager {
    private strategies: Map<string, SearchEngineStrategy> = new Map();
    private defaultStrategy: SearchEngineStrategy;

    constructor() {
        // Initialize strategies
        this.strategies.set('google', new GoogleSearchStrategy());
        this.strategies.set('bing', new BingSearchStrategy());
        this.strategies.set('duckduckgo', new DuckDuckGoSearchStrategy());
        this.strategies.set('yahoo', new YahooSearchStrategy());

        // Set default strategy
        this.defaultStrategy = this.strategies.get('google')!;
    }

    getStrategy(engineId: string): SearchEngineStrategy {
        return this.strategies.get(engineId) || this.defaultStrategy;
    }

    getAllStrategies(): SearchEngineStrategy[] {
        return Array.from(this.strategies.values());
    }

    getDefaultStrategy(): SearchEngineStrategy {
        return this.defaultStrategy;
    }
}

export const searchEngineManager = new SearchEngineManager();
