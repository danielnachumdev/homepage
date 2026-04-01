import type { AudioVisualizerMode } from '../../../../../types/link';
import type { AudioVisualizerRenderer } from './types';
import { createRadialRenderer } from './radial';
import { createRadialOverSpectrogramRenderer } from './radialOverSpectrogram';
import { createSpectrogramRenderer } from './spectrogram';
import { createWaveformRenderer } from './waveform';

export type AudioVisualizerRendererOptions = {
    spectrogramOpacityCurve?: (x: number) => number;
    spectrogramMaxOpacity?: number;
};

type AudioVisualizerRendererFactory = (options?: AudioVisualizerRendererOptions) => AudioVisualizerRenderer;

const factories = {
    radial: createRadialRenderer,
    radialOverSpectrogram: createRadialOverSpectrogramRenderer,
    waveform: createWaveformRenderer,
    spectrogram: createSpectrogramRenderer,
} satisfies Record<AudioVisualizerMode, AudioVisualizerRendererFactory>;

export function createAudioVisualizerRenderer(
    mode: AudioVisualizerMode,
    options?: AudioVisualizerRendererOptions
): AudioVisualizerRenderer {
    return factories[mode](options);
}

