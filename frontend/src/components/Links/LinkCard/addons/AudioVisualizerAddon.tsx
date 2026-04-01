import React, { useEffect, useMemo, useRef, useState } from 'react';
import { Box, IconButton, Modal, Tooltip, Typography } from '@mui/material';
import {
    Fullscreen as FullscreenIcon,
    FullscreenExit as FullscreenExitIcon,
    Pause as PauseIcon,
    PlayArrow as PlayArrowIcon
} from '@mui/icons-material';
import type { AudioVisualizerMode, LinkCardLeafAddon } from '../../../../types/link';
import styles from './AudioVisualizerAddon.module.css';
import { createAudioVisualizerRenderer } from './audioVisualizerModes/factory';
import type { AudioVisualizerRenderer } from './audioVisualizerModes/types';

type AudioVisualizerAddonConfig = Extract<LinkCardLeafAddon, { type: 'audioVisualizer' }>;

export function AudioVisualizerAddon({
    addon,
    stopCardInteraction,
}: {
    addon: AudioVisualizerAddonConfig;
    stopCardInteraction: (e: React.SyntheticEvent) => void;
}) {
    const audioRef = useRef<HTMLAudioElement | null>(null);
    const inlineCanvasRef = useRef<HTMLCanvasElement | null>(null);
    const fullscreenCanvasRef = useRef<HTMLCanvasElement | null>(null);
    const activeCanvasRef = useRef<HTMLCanvasElement | null>(null);
    const rafRef = useRef<number | null>(null);

    const audioContextRef = useRef<AudioContext | null>(null);
    const analyserRef = useRef<AnalyserNode | null>(null);
    const sourceRef = useRef<MediaElementAudioSourceNode | null>(null);
    const inlineRendererRef = useRef<{
        key: string;
        curve?: (x: number) => number;
        renderer: AudioVisualizerRenderer;
    } | null>(null);
    const fullscreenRendererRef = useRef<{
        key: string;
        curve?: (x: number) => number;
        renderer: AudioVisualizerRenderer;
    } | null>(null);

    const [isPlaying, setIsPlaying] = useState(false);
    const [lastError, setLastError] = useState<string | null>(null);
    const [isFullscreen, setIsFullscreen] = useState(false);

    const accent = addon.accentColor ?? '#66e3ff';
    const modeInline: AudioVisualizerMode = addon.modeInline ?? 'waveform';
    const modeFullscreen: AudioVisualizerMode = addon.modeFullscreen ?? 'radial';
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
        const canvas = activeCanvasRef.current;
        if (!canvas) return;

        const ctx2d = canvas.getContext('2d');
        if (!ctx2d) return;

        const spectroMax = addon.spectrogramMaxOpacity ?? 0.8;
        const spectroCurve = addon.spectrogramOpacityCurve;
        const selectedMode: AudioVisualizerMode = isFullscreen ? modeFullscreen : modeInline;
        const rendererKey = `${selectedMode}|${spectroMax}`;
        const slot = isFullscreen ? fullscreenRendererRef : inlineRendererRef;

        if (!slot.current || slot.current.key !== rendererKey || slot.current.curve !== spectroCurve) {
            slot.current = {
                key: rendererKey,
                curve: spectroCurve,
                renderer: createAudioVisualizerRenderer(selectedMode, {
                    spectrogramOpacityCurve: spectroCurve,
                    spectrogramMaxOpacity: spectroMax,
                }),
            };
        }

        const renderer = slot.current.renderer;

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

            renderer.renderFrame({
                t,
                w,
                h,
                dpr,
                accent,
                ctx2d,
                analyser: analyserRef.current,
                freqData: buffer,
                timeData: timeBuffer,
            });

            rafRef.current = window.requestAnimationFrame(draw);
        };

        if (rafRef.current) window.cancelAnimationFrame(rafRef.current);
        rafRef.current = window.requestAnimationFrame(draw);
    };

    useEffect(() => {
        activeCanvasRef.current = inlineCanvasRef.current;
        startRendering();
    }, []);

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

    const handleRootToggle = (e: React.SyntheticEvent) => {
        stopCardInteraction(e);
        void handleTogglePlay();
    };

    const handleToggleFullscreen = (e: React.SyntheticEvent) => {
        stopCardInteraction(e);
        setIsFullscreen((v) => !v);
    };

    useEffect(() => {
        const target = isFullscreen ? fullscreenCanvasRef : inlineCanvasRef;

        // Modal content mounts asynchronously; wait at least a frame so ref is set and layout is computed.
        const raf1 = window.requestAnimationFrame(() => {
            const raf2 = window.requestAnimationFrame(() => {
                activeCanvasRef.current = target.current;
                startRendering();
            });
            // store raf2 in closure; cancel via raf1's cleanup below by capturing in outer scope
            (rafRef as any).currentModalSwapRaf2 = raf2;
        });

        return () => {
            window.cancelAnimationFrame(raf1);
            const raf2 = (rafRef as any).currentModalSwapRaf2 as number | undefined;
            if (raf2) window.cancelAnimationFrame(raf2);
        };
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [isFullscreen]);

    const OverlayButtons = ({ mode }: { mode: 'inline' | 'fullscreen' }) => (
        <Box className={styles.visualizerOverlay}>
            <Box className={styles.visualizerCenterButton}>
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
            </Box>

            <Box className={styles.visualizerFullscreenButton}>
                <Tooltip title={mode === 'fullscreen' ? 'Exit fullscreen' : 'Fullscreen'} arrow>
                    <IconButton
                        size="small"
                        onClick={handleToggleFullscreen}
                        className={styles.visualizerButton}
                        aria-label={mode === 'fullscreen' ? 'Exit fullscreen' : 'Enter fullscreen'}
                    >
                        {mode === 'fullscreen' ? (
                            <FullscreenExitIcon fontSize="small" />
                        ) : (
                            <FullscreenIcon fontSize="small" />
                        )}
                    </IconButton>
                </Tooltip>
            </Box>
        </Box>
    );

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
        <>
            <Box
                className={styles.visualizerRoot}
                onClick={handleRootToggle}
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

                <canvas ref={inlineCanvasRef} className={styles.visualizerCanvas} />

                <OverlayButtons mode="inline" />

                {lastError && (
                    <Box className={styles.visualizerError}>
                        <Typography variant="caption" className={styles.visualizerErrorText}>
                            {lastError}
                        </Typography>
                    </Box>
                )}
            </Box>

            <Modal
                open={isFullscreen}
                onClose={(_, reason) => {
                    if (reason === 'escapeKeyDown') setIsFullscreen(false);
                }}
                closeAfterTransition={false}
                BackdropProps={{ className: styles.visualizerModalBackdrop }}
            >
                <Box className={styles.visualizerModalContent}>
                    <Box
                        className={styles.visualizerClickShield}
                        onClick={stopCardInteraction}
                        onMouseDown={stopCardInteraction}
                        onKeyDown={stopCardInteraction}
                    />
                    <Box className={styles.visualizerModalFrame}>
                        <Box
                            className={styles.visualizerRoot}
                            onClick={handleRootToggle}
                            onMouseDown={stopCardInteraction}
                            onKeyDown={stopCardInteraction}
                            style={
                                {
                                    ['--visualizer-accent' as any]: accent,
                                    backgroundImage: backgroundGradient,
                                } as React.CSSProperties
                            }
                        >
                            <canvas ref={fullscreenCanvasRef} className={styles.visualizerCanvas} />
                            <OverlayButtons mode="fullscreen" />
                            {lastError && (
                                <Box className={styles.visualizerError}>
                                    <Typography variant="caption" className={styles.visualizerErrorText}>
                                        {lastError}
                                    </Typography>
                                </Box>
                            )}
                        </Box>
                    </Box>
                </Box>
            </Modal>
        </>
    );
}

