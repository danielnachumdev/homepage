export interface LinkData {
    title: string;
    icon: string | string[]; // URL, icon name, or array of fallback URLs
    description?: string; // Optional description
    url: string;
    /** Optional, typed addon rendered inside the card (specialized UI). */
    addon?: LinkCardAddon;
    chromeProfileEnabled?: boolean; // Defaults to false
    chromeProfiles?: string[]; // Available Chrome profiles for this link
}

export type AudioVisualizerMode = 'radial' | 'waveform' | 'spectrogram' | 'radialOverSpectrogram';

export type LinkCardLeafAddon =
    | {
          type: 'audioPlayer';
          streamUrl: string;
          mimeType?: string;
      }
    | {
          type: 'audioVisualizer';
          streamUrl: string;
          mimeType?: string;
          modeInline?: AudioVisualizerMode;
          modeFullscreen?: AudioVisualizerMode;
          /** Curvature control for log frequency scaling (>= 1). Default matches current behavior. */
          frequencyLogBase?: number;
          /**
           * Opacity curve for spectrogram masking in composite modes.
           * Function over x in [0..1] returning y in [0..1].
           * Example: (x) => 1 - x
           */
          spectrogramOpacityCurve?: (x: number) => number;
          /** Max overall opacity multiplier for the spectrogram mask (0..1). */
          spectrogramMaxOpacity?: number;
          /** Optional accent color (CSS color string). */
          accentColor?: string;
      }
    | {
          type: 'sublinks';
          items: LinkSubItem[];
      };

export type LinkCardCompositeAddon = {
    type: 'composite';
    layout: 'stack';
    addons: LinkCardLeafAddon[];
};

export type LinkCardAddon = LinkCardLeafAddon | LinkCardCompositeAddon;

/**
 * Same shape as LinkData for reuse (e.g. spread a full link or build a minimal object).
 * Only `title`, `url`, and `icon` are required; everything else matches LinkData but optional.
 */
export type LinkSubItem = Required<Pick<LinkData, 'title' | 'url' | 'icon'>> &
    Partial<Omit<LinkData, 'title' | 'url' | 'icon'>>;

export interface LinkCardProps {
    link: LinkData;
    onLinkClick: (link: LinkData) => void;
    onChromeProfileClick?: (link: LinkData, profile: string) => void;
    onSublinkClick?: (parent: LinkData, sub: LinkSubItem) => void;
}

export interface LinksSectionProps {
    links: LinkData[];
    onLinkClick: (link: LinkData) => void;
    onChromeProfileClick?: (link: LinkData, profile: string) => void;
    onSublinkClick?: (parent: LinkData, sub: LinkSubItem) => void;
}
