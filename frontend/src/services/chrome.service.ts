import { api } from '../lib/api';

export interface ChromeProfile {
    id: string;
    name: string;
    icon?: string;
    is_active: boolean;
    path?: string;
}

export interface ChromeProfileListResponse {
    success: boolean;
    profiles: ChromeProfile[];
    message?: string;
}

export interface OpenUrlRequest {
    url: string;
    profile_id: string;
}

export interface OpenUrlResponse {
    success: boolean;
    message: string;
    profile_name?: string;
}

class ChromeService {
    async getChromeProfiles(): Promise<ChromeProfileListResponse> {
        try {
            const response = await api.get<ChromeProfileListResponse>('/api/v1/chrome/profiles');
            return response.data;
        } catch (error) {
            console.error('Failed to get Chrome profiles:', error);
            throw error;
        }
    }

    async openUrlInProfile(request: OpenUrlRequest): Promise<OpenUrlResponse> {
        try {
            const response = await api.post<OpenUrlResponse>('/api/v1/chrome/open-url', request);
            return response.data;
        } catch (error) {
            console.error('Failed to open URL in profile:', error);
            throw error;
        }
    }
}

export const chromeService = new ChromeService();
