import React from 'react';
import { Box } from '@mui/material';
import type { LinkCardLeafAddon, LinkSubItem } from '../../../../types/link';
import styles from '../LinkCard.module.css';

type SublinksAddonConfig = Extract<LinkCardLeafAddon, { type: 'sublinks' }>;

export function SublinksAddon({
    addon,
    stopCardInteraction,
    onSublinkActivate,
    SubLinkRow,
}: {
    addon: SublinksAddonConfig;
    stopCardInteraction: (e: React.SyntheticEvent) => void;
    onSublinkActivate: (sub: LinkSubItem) => void;
    SubLinkRow: React.ComponentType<{ sub: LinkSubItem; onActivate: () => void }>;
}) {
    return (
        <Box className={styles.sublinksScroll} onClick={stopCardInteraction} onMouseDown={stopCardInteraction}>
            {addon.items.map((sub, i) => (
                <SubLinkRow key={`${sub.title}-${i}`} sub={sub} onActivate={() => onSublinkActivate(sub)} />
            ))}
        </Box>
    );
}

