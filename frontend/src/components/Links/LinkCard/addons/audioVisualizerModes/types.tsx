import type { AudioVisualizerMode } from '../../../../../types/link';

export type AudioVisualizerFrameInput = {
    t: number;
    w: number;
    h: number;
    dpr: number;
    accent: string;
    ctx2d: CanvasRenderingContext2D;
    analyser: AnalyserNode | null;
    freqData: Uint8Array | null;
    timeData: Uint8Array | null;
};

export type AudioVisualizerRenderer = {
    mode: AudioVisualizerMode;
    renderFrame: (input: AudioVisualizerFrameInput) => void;
};

