import React, { useEffect, useMemo, useRef, useState } from 'react';
import { Box, IconButton, Tooltip, Typography } from '@mui/material';
import { Pause as PauseIcon, PlayArrow as PlayArrowIcon, VolumeUp as VolumeUpIcon } from '@mui/icons-material';
import type { LinkCardLeafAddon } from '../../../../types/link';
import styles from '../LinkCard.module.css';

type AudioVisualizerAddonConfig = Extract<LinkCardLeafAddon, { type: 'audioVisualizer' }>;

export function AudioVisualizerAddon({
    addon,
    stopCardInteraction,
}: {
    addon: AudioVisualizerAddonConfig;
    stopCardInteraction: (e: React.SyntheticEvent) => void;
}) {
    const audioRef = useRef<HTMLAudioElement | null>(null);
    const canvasRef = useRef<HTMLCanvasElement | null>(null);
    const rafRef = useRef<number | null>(null);

    const audioContextRef = useRef<AudioContext | null>(null);
    const analyserRef = useRef<AnalyserNode | null>(null);
    const sourceRef = useRef<MediaElementAudioSourceNode | null>(null);

    const [isPlaying, setIsPlaying] = useState(false);
    const [lastError, setLastError] = useState<string | null>(null);

    const accent = addon.accentColor ?? '#66e3ff';
    const backgroundGradient = useMemo(() => {
        return `radial-gradient(120% 120% at 50% 15%, rgba(255,255,255,0.10) 0%, rgba(0,0,0,0.0) 60%),
linear-gradient(135deg, rgba(102,227,255,0.12) 0%, rgba(0,0,0,0.0) 40%, rgba(255,255,255,0.06) 100%)`;
    }, []);

    const ensureAudioGraph = async () => {
        const audioEl = audioRef.current;
        if (!audioEl) return;

        if (!audioContextRef.current) {
            const Ctx = window.AudioContext || (window as any).webkitAudioContext;
            audioContextRef.current = new Ctx();
        }

        const ctx = audioContextRef.current;
        if (!ctx) return;

        if (ctx.state !== 'running') {
            await ctx.resume();
        }

        if (!analyserRef.current) {
            analyserRef.current = ctx.createAnalyser();
            analyserRef.current.fftSize = 2048;
            analyserRef.current.smoothingTimeConstant = 0.85;
        }

        if (!sourceRef.current) {
            sourceRef.current = ctx.createMediaElementSource(audioEl);
            sourceRef.current.connect(analyserRef.current);
            analyserRef.current.connect(ctx.destination);
        }
    };

    const startRendering = () => {
        const canvas = canvasRef.current;
        if (!canvas) return;

        const ctx2d = canvas.getContext('2d');
        if (!ctx2d) return;

        const analyser = analyserRef.current;
        const buffer = analyser ? new Uint8Array(analyser.frequencyBinCount) : null;
        const timeBuffer = analyser ? new Uint8Array(analyser.fftSize) : null;

        const draw = (t: number) => {
            const { width, height } = canvas.getBoundingClientRect();
            const dpr = window.devicePixelRatio || 1;
            const w = Math.max(1, Math.round(width * dpr));
            const h = Math.max(1, Math.round(height * dpr));
            if (canvas.width !== w || canvas.height !== h) {
                canvas.width = w;
                canvas.height = h;
            }

            ctx2d.clearRect(0, 0, w, h);

            const pad = Math.round(10 * dpr);
            const cx = w / 2;
            const cy = h / 2 + Math.round(4 * dpr);

            let energy = 0;
            if (analyser && buffer && timeBuffer) {
                analyser.getByteFrequencyData(buffer);
                analyser.getByteTimeDomainData(timeBuffer);
                for (let i = 0; i < buffer.length; i++) energy += buffer[i];
                energy /= buffer.length * 255;
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
                const f = buffer ? buffer[Math.floor((i / bars) * buffer.length)] / 255 : 0;
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
                const ti = timeBuffer ? timeBuffer[Math.floor((i / points) * (timeBuffer.length - 1))] : 128;
                const n = (ti - 128) / 128;
                const wobble = (timeBuffer ? n : Math.sin(t / 650 + a * 2)) * (maxR * 0.10);
                const rr = baseR * (0.72 + 0.10 * drive) + wobble;
                const x = Math.cos(a) * rr;
                const y = Math.sin(a) * rr;
                if (i === 0) ctx2d.moveTo(x, y);
                else ctx2d.lineTo(x, y);
            }
            ctx2d.stroke();
            ctx2d.restore();

            rafRef.current = window.requestAnimationFrame(draw);
        };

        if (rafRef.current) window.cancelAnimationFrame(rafRef.current);
        rafRef.current = window.requestAnimationFrame(draw);
    };

    const stopRendering = () => {
        if (rafRef.current) {
            window.cancelAnimationFrame(rafRef.current);
            rafRef.current = null;
        }
    };

    const handleTogglePlay = async () => {
        const audioEl = audioRef.current;
        if (!audioEl) return;

        setLastError(null);

        try {
            if (audioEl.paused) {
                await ensureAudioGraph();
                await audioEl.play();
                setIsPlaying(true);
                startRendering();
            } else {
                audioEl.pause();
                setIsPlaying(false);
            }
        } catch (e) {
            setIsPlaying(false);
            setLastError(e instanceof Error ? e.message : 'Failed to start audio');
        }
    };

    useEffect(() => {
        const audioEl = audioRef.current;
        if (!audioEl) return;

        const onPlay = () => {
            setIsPlaying(true);
            startRendering();
        };
        const onPause = () => setIsPlaying(false);
        const onEnded = () => setIsPlaying(false);
        const onError = () => setLastError('Audio error');

        audioEl.addEventListener('play', onPlay);
        audioEl.addEventListener('pause', onPause);
        audioEl.addEventListener('ended', onEnded);
        audioEl.addEventListener('error', onError);

        return () => {
            audioEl.removeEventListener('play', onPlay);
            audioEl.removeEventListener('pause', onPause);
            audioEl.removeEventListener('ended', onEnded);
            audioEl.removeEventListener('error', onError);
        };
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, []);

    useEffect(() => {
        return () => {
            stopRendering();
            try {
                sourceRef.current?.disconnect();
                analyserRef.current?.disconnect();
            } catch {
                // ignore
            }
            sourceRef.current = null;
            analyserRef.current = null;
            // Intentionally not closing AudioContext to allow fast resume on remount/navigation.
        };
    }, []);

    return (
        <Box
            className={styles.visualizerRoot}
            onClick={stopCardInteraction}
            onMouseDown={stopCardInteraction}
            onKeyDown={stopCardInteraction}
            style={
                {
                    ['--visualizer-accent' as any]: accent,
                    backgroundImage: backgroundGradient,
                } as React.CSSProperties
            }
        >
            <audio ref={audioRef} src={addon.streamUrl} preload="none" crossOrigin="anonymous" />

            <canvas ref={canvasRef} className={styles.visualizerCanvas} />

            <Box className={styles.visualizerOverlay}>
                <Tooltip title={isPlaying ? 'Pause' : 'Play'} arrow>
                    <IconButton
                        size="small"
                        onClick={(e) => {
                            stopCardInteraction(e);
                            void handleTogglePlay();
                        }}
                        className={styles.visualizerButton}
                        aria-label={isPlaying ? 'Pause audio' : 'Play audio'}
                    >
                        {isPlaying ? <PauseIcon fontSize="small" /> : <PlayArrowIcon fontSize="small" />}
                    </IconButton>
                </Tooltip>

                <Box className={styles.visualizerMeta}>
                    <VolumeUpIcon sx={{ fontSize: 14, opacity: 0.9 }} />
                    <Typography variant="caption" className={styles.visualizerLabel}>
                        Live
                    </Typography>
                </Box>
            </Box>

            {lastError && (
                <Box className={styles.visualizerError}>
                    <Typography variant="caption" className={styles.visualizerErrorText}>
                        {lastError}
                    </Typography>
                </Box>
            )}
        </Box>
    );
}

