import type { AudioVisualizerRenderer } from './types';
import { createRadialRenderer } from './radial';
import { createSpectrogramRenderer } from './spectrogram';
import type { AudioVisualizerRendererOptions } from './factory';

export function createRadialOverSpectrogramRenderer(options?: AudioVisualizerRendererOptions): AudioVisualizerRenderer {
    const spectrogram = createSpectrogramRenderer(options);
    const radial = createRadialRenderer(options);
    const maxOpacity = Math.min(1, Math.max(0, options?.spectrogramMaxOpacity ?? 0.8));
    const curveFn = options?.spectrogramOpacityCurve ?? ((x: number) => 1 - x);

    const maskCache = {
        w: 0,
        h: 0,
        maxOpacity: -1,
        canvas: null as HTMLCanvasElement | null,
    };

    return {
        mode: 'radialOverSpectrogram',
        renderFrame: (input) => {
            const { ctx2d, w, h } = input;

            // 1) Background: spectrogram
            spectrogram.renderFrame(input);

            // 2) Apply opacity mask using user curve y=f(x) (x in [0..1], y in [0..1])
            ctx2d.save();
            ctx2d.globalCompositeOperation = 'destination-in';
            if (
                !maskCache.canvas ||
                maskCache.w !== w ||
                maskCache.h !== h ||
                maskCache.maxOpacity !== maxOpacity
            ) {
                const c = document.createElement('canvas');
                c.width = Math.max(1, w);
                c.height = Math.max(1, h);
                const mctx = c.getContext('2d');
                if (mctx) {
                    const img = mctx.createImageData(c.width, 1);
                    for (let x = 0; x < c.width; x++) {
                        const fx = c.width <= 1 ? 0 : x / (c.width - 1);
                        const yRaw = curveFn(fx);
                        const y = Number.isFinite(yRaw) ? Math.min(1, Math.max(0, yRaw)) : 0;
                        const a = Math.floor(255 * maxOpacity * y);
                        const i = x * 4;
                        img.data[i + 0] = 255;
                        img.data[i + 1] = 255;
                        img.data[i + 2] = 255;
                        img.data[i + 3] = a;
                    }
                    mctx.putImageData(img, 0, 0);
                    // stretch to full height
                    mctx.imageSmoothingEnabled = true;
                    mctx.drawImage(c, 0, 0, c.width, 1, 0, 0, c.width, c.height);
                }
                maskCache.canvas = c;
                maskCache.w = w;
                maskCache.h = h;
                maskCache.maxOpacity = maxOpacity;
            }

            if (maskCache.canvas) {
                ctx2d.drawImage(maskCache.canvas, 0, 0);
            } else {
                ctx2d.fillStyle = `rgba(255,255,255,${maxOpacity})`;
                ctx2d.fillRect(0, 0, w, h);
            }
            ctx2d.restore();

            // 3) Foreground: radial (unchanged)
            radial.renderFrame(input);
        },
    };
}

