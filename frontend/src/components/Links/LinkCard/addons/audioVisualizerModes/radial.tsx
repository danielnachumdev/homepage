import type { AudioVisualizerRenderer } from './types';
import type { AudioVisualizerRendererOptions } from './factory';
import { getLogBinIndex } from './math';

export function createRadialRenderer(options?: AudioVisualizerRendererOptions): AudioVisualizerRenderer {
    const logBase = options?.frequencyLogBase ?? Math.E;
    return {
        mode: 'radial',
        renderFrame: ({ t, w, h, dpr, ctx2d, analyser, freqData, timeData }) => {
            const pad = Math.round(10 * dpr);
            const cx = w / 2;
            const cy = h / 2;

            let energy = 0;
            if (analyser && freqData && timeData) {
                analyser.getByteFrequencyData(freqData);
                analyser.getByteTimeDomainData(timeData);
                for (let i = 0; i < freqData.length; i++) energy += freqData[i];
                energy /= freqData.length * 255;
            }

            const idlePulse = 0.12 + 0.08 * Math.sin(t / 550);
            const drive = Math.max(idlePulse, energy);

            const maxR = Math.min(w, h) / 2 - pad;
            const baseR = maxR * (0.42 + 0.10 * drive);
            const rings = 3;

            // glow background
            const glow = ctx2d.createRadialGradient(cx, cy, 0, cx, cy, maxR);
            glow.addColorStop(0, `rgba(102,227,255,${0.12 + 0.18 * drive})`);
            glow.addColorStop(1, 'rgba(0,0,0,0)');
            ctx2d.fillStyle = glow;
            ctx2d.fillRect(0, 0, w, h);

            // frequency "crown"
            const bars = 64;
            const barW = (Math.PI * 2) / bars;
            ctx2d.save();
            ctx2d.translate(cx, cy);
            for (let i = 0; i < bars; i++) {
                const bin = freqData ? getLogBinIndex(i / (bars - 1), freqData.length, logBase) : 0;
                const f = freqData ? freqData[bin] / 255 : 0;
                const a = i * barW;
                const len = maxR * (0.08 + 0.18 * f + 0.14 * drive);
                const r0 = baseR * 0.95;
                const x0 = Math.cos(a) * r0;
                const y0 = Math.sin(a) * r0;
                const x1 = Math.cos(a) * (r0 + len);
                const y1 = Math.sin(a) * (r0 + len);
                ctx2d.strokeStyle = `rgba(102,227,255,${0.12 + 0.55 * f})`;
                ctx2d.lineWidth = Math.max(1, 2 * dpr * (0.6 + f));
                ctx2d.beginPath();
                ctx2d.moveTo(x0, y0);
                ctx2d.lineTo(x1, y1);
                ctx2d.stroke();
            }
            ctx2d.restore();

            // soft rings
            for (let r = 0; r < rings; r++) {
                const phase = r / rings;
                const rr = baseR * (0.78 + 0.18 * r) + maxR * 0.03 * Math.sin(t / (420 + r * 120));
                ctx2d.strokeStyle = `rgba(255,255,255,${0.06 + 0.10 * drive * (1 - phase)})`;
                ctx2d.lineWidth = Math.max(1, dpr * (1.2 - r * 0.2));
                ctx2d.beginPath();
                ctx2d.arc(cx, cy, rr, 0, Math.PI * 2);
                ctx2d.stroke();
            }

            // waveform blob
            ctx2d.save();
            ctx2d.translate(cx, cy);
            ctx2d.strokeStyle = `rgba(255,255,255,${0.22 + 0.35 * drive})`;
            ctx2d.lineWidth = Math.max(1, 2.2 * dpr);
            ctx2d.beginPath();

            const points = 96;
            for (let i = 0; i <= points; i++) {
                const a = (i / points) * Math.PI * 2;
                const ti = timeData ? timeData[Math.floor((i / points) * (timeData.length - 1))] : 128;
                const n = (ti - 128) / 128;
                const wobble = (timeData ? n : Math.sin(t / 650 + a * 2)) * (maxR * 0.10);
                const rr = baseR * (0.72 + 0.10 * drive) + wobble;
                const x = Math.cos(a) * rr;
                const y = Math.sin(a) * rr;
                if (i === 0) ctx2d.moveTo(x, y);
                else ctx2d.lineTo(x, y);
            }
            ctx2d.stroke();
            ctx2d.restore();
        },
    };
}

