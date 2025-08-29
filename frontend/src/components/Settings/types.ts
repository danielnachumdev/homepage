export interface Setting {
    name: string;
    description: string;
    type: 'boolean' | 'string' | 'number' | 'select' | 'color' | 'file';
    value?: any;
    options?: string[];
    min?: number;
    max?: number;
    step?: number;
}

export interface SettingsCategory {
    id: string;
    name: string;
    description?: string;
    settings: Setting[];
}
