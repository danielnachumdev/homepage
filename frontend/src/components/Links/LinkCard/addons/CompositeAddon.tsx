import React from 'react';
import { Box } from '@mui/material';
import type { LinkCardCompositeAddon, LinkCardLeafAddon } from '../../../../types/link';
import styles from './CompositeAddon.module.css';

export function CompositeAddon({
    addon,
    stopCardInteraction,
    renderLeafAddon,
}: {
    addon: LinkCardCompositeAddon;
    stopCardInteraction: (e: React.SyntheticEvent) => void;
    renderLeafAddon: (addon: LinkCardLeafAddon, key: string) => React.ReactNode;
}) {
    switch (addon.layout) {
        case 'stack':
            return (
                <Box className={styles.addonStack} onClick={stopCardInteraction} onMouseDown={stopCardInteraction}>
                    {addon.addons.map((leaf, i) => renderLeafAddon(leaf, `${leaf.type}-${i}`))}
                </Box>
            );
        default: {
            const _exhaustive: never = addon.layout;
            return _exhaustive;
        }
    }
}

