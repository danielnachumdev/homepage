import type { AudioVisualizerMode } from '../../../../../types/link';
import type { AudioVisualizerRenderer } from './types';
import { createRadialRenderer } from './radial';
import { createSpectrogramRenderer } from './spectrogram';
import { createWaveformRenderer } from './waveform';

type AudioVisualizerRendererFactory = () => AudioVisualizerRenderer;

const factories = {
    radial: createRadialRenderer,
    waveform: createWaveformRenderer,
    spectrogram: createSpectrogramRenderer,
} satisfies Record<AudioVisualizerMode, AudioVisualizerRendererFactory>;

export function createAudioVisualizerRenderer(mode: AudioVisualizerMode): AudioVisualizerRenderer {
    return factories[mode]();
}

