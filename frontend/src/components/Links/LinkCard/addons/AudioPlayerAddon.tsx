import React from 'react';
import { Box } from '@mui/material';
import type { LinkCardLeafAddon } from '../../../../types/link';
import styles from './AudioPlayerAddon.module.css';

type AudioPlayerAddonConfig = Extract<LinkCardLeafAddon, { type: 'audioPlayer' }>;

export function AudioPlayerAddon({
    addon,
    stopCardInteraction,
}: {
    addon: AudioPlayerAddonConfig;
    stopCardInteraction: (e: React.SyntheticEvent) => void;
}) {
    return (
        <Box
            className={styles.audioContainer}
            onClick={stopCardInteraction}
            onMouseDown={stopCardInteraction}
            onKeyDown={stopCardInteraction}
        >
            <audio className={styles.audio} controls preload="none">
                <source src={addon.streamUrl} type={addon.mimeType ?? 'audio/mpeg'} />
                Your browser does not support the audio element.
            </audio>
        </Box>
    );
}

