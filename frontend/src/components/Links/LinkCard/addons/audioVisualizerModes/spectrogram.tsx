import type { AudioVisualizerRenderer } from './types';

export function createSpectrogramRenderer(): AudioVisualizerRenderer {
    const state = {
        imageData: null as ImageData | null,
        lastW: 0,
        lastH: 0,
    };

    return {
        mode: 'spectrogram',
        renderFrame: ({ t, w, h, dpr, ctx2d, analyser, freqData }) => {
            if (analyser && freqData) analyser.getByteFrequencyData(freqData);

            const pad = Math.round(10 * dpr);
            const usableH = Math.max(1, h - pad * 2);
            const usableW = Math.max(1, w - pad * 2);

            if (!state.imageData || state.lastW !== usableW || state.lastH !== usableH) {
                state.imageData = ctx2d.createImageData(usableW, usableH);
                state.lastW = usableW;
                state.lastH = usableH;
                state.imageData.data.fill(0);
            }

            const img = state.imageData!;
            const data = img.data;

            // shift left by 1 column
            const rowStride = usableW * 4;
            for (let y = 0; y < usableH; y++) {
                const rowStart = y * rowStride;
                data.copyWithin(rowStart, rowStart + 4, rowStart + rowStride);
            }

            // new column on the right
            const x = usableW - 1;
            const colOffset = x * 4;
            for (let y = 0; y < usableH; y++) {
                const bin = freqData ? Math.floor((1 - y / (usableH - 1)) * (freqData.length - 1)) : 0;
                const mag = freqData ? freqData[bin] / 255 : 0;

                // teal -> white
                const r = Math.floor(40 + 215 * Math.pow(mag, 1.35));
                const g = Math.floor(80 + 175 * Math.pow(mag, 1.1));
                const b = Math.floor(120 + 135 * Math.pow(mag, 0.9));
                const a = Math.floor(255 * Math.min(1, 0.12 + 0.95 * mag));

                const i = y * rowStride + colOffset;
                data[i + 0] = r;
                data[i + 1] = g;
                data[i + 2] = b;
                data[i + 3] = a;
            }

            // faint pulse if analyser unavailable
            const idle = 0.06 + 0.04 * Math.sin(t / 520);
            ctx2d.fillStyle = `rgba(102,227,255,${idle})`;
            ctx2d.fillRect(0, 0, w, h);

            ctx2d.putImageData(img, pad, pad);

            ctx2d.strokeStyle = 'rgba(255,255,255,0.10)';
            ctx2d.lineWidth = Math.max(1, 1 * dpr);
            ctx2d.strokeRect(pad + 0.5 * dpr, pad + 0.5 * dpr, usableW - dpr, usableH - dpr);
        },
    };
}

