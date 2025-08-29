// Base setting interface that all settings must implement
export interface BaseSetting {
    id: string;
    name: string;
    description: string;
    type: string;
    value: any;
}

// Specific setting types
export interface BooleanSetting extends BaseSetting {
    type: 'boolean';
    value: boolean;
}

export interface StringSetting extends BaseSetting {
    type: 'string';
    value: string;
    maxLength?: number;
}

export interface NumberSetting extends BaseSetting {
    type: 'number';
    value: number;
    min?: number;
    max?: number;
    step?: number;
}

export interface SelectSetting extends BaseSetting {
    type: 'select';
    value: string;
    options: string[];
}

export interface ColorSetting extends BaseSetting {
    type: 'color';
    value: string;
}

export interface FileSetting extends BaseSetting {
    type: 'file';
    value: string;
    acceptedTypes?: string[];
}

export interface ChromeProfileSetting extends BaseSetting {
    type: 'chrome-profile';
    value: {
        displayName: string;
        icon: string;
    };
    profileId: string;
    originalName: string;
}

// Union type for all possible setting types
export type Setting =
    | BooleanSetting
    | StringSetting
    | NumberSetting
    | SelectSetting
    | ColorSetting
    | FileSetting
    | ChromeProfileSetting;

export interface SettingsCategory {
    id: string;
    name: string;
    description?: string;
    settings: Setting[];
}

// Component-based category interface
export interface SettingsCategoryComponent {
    id: string;
    title: string;
    description?: string;
    component: React.ComponentType;
}
