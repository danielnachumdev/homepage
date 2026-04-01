import type { AudioVisualizerRenderer } from './types';

export function createWaveformRenderer(): AudioVisualizerRenderer {
    return {
        mode: 'waveform',
        renderFrame: ({ t, w, h, dpr, ctx2d, analyser, timeData }) => {
            if (analyser && timeData) analyser.getByteTimeDomainData(timeData);

            const padX = Math.round(10 * dpr);
            const midY = h / 2;
            const amp = (h / 2 - Math.round(14 * dpr)) * 0.85;

            // subtle glow
            const idlePulse = 0.08 + 0.06 * Math.sin(t / 500);
            const bg = ctx2d.createLinearGradient(0, 0, w, h);
            bg.addColorStop(0, `rgba(102,227,255,${0.06 + idlePulse})`);
            bg.addColorStop(1, 'rgba(0,0,0,0)');
            ctx2d.fillStyle = bg;
            ctx2d.fillRect(0, 0, w, h);

            ctx2d.lineWidth = Math.max(1, 2.2 * dpr);
            ctx2d.strokeStyle = 'rgba(255,255,255,0.85)';
            ctx2d.beginPath();

            const samples = timeData ? timeData.length : 0;
            const usableW = Math.max(1, w - padX * 2);
            for (let i = 0; i < samples; i++) {
                const x = padX + (i / (samples - 1)) * usableW;
                const v = timeData ? (timeData[i] - 128) / 128 : 0;
                const y = midY + v * amp;
                if (i === 0) ctx2d.moveTo(x, y);
                else ctx2d.lineTo(x, y);
            }
            ctx2d.stroke();

            // centerline
            ctx2d.lineWidth = Math.max(1, 1 * dpr);
            ctx2d.strokeStyle = 'rgba(255,255,255,0.15)';
            ctx2d.beginPath();
            ctx2d.moveTo(padX, midY);
            ctx2d.lineTo(w - padX, midY);
            ctx2d.stroke();
        },
    };
}

