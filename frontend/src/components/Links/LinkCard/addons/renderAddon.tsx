import React from 'react';
import type { LinkCardAddon, LinkCardCompositeAddon, LinkCardLeafAddon, LinkSubItem } from '../../../../types/link';
import { AudioPlayerAddon } from './AudioPlayerAddon';
import { AudioVisualizerAddon } from './AudioVisualizerAddon';
import { CompositeAddon } from './CompositeAddon';
import { SublinksAddon } from './SublinksAddon';

type AddonRenderContext = {
    stopCardInteraction: (e: React.SyntheticEvent) => void;
    onSublinkActivate: (sub: LinkSubItem) => void;
    SubLinkRow: React.ComponentType<{ sub: LinkSubItem; onActivate: () => void }>;
};

type AddonType = LinkCardAddon['type'];
type AddonRendererMap = {
    [K in AddonType]: (addon: Extract<LinkCardAddon, { type: K }>, ctx: AddonRenderContext) => React.ReactNode;
};

type LeafAddonType = LinkCardLeafAddon['type'];
type LeafAddonRendererMap = {
    [K in LeafAddonType]: (addon: Extract<LinkCardLeafAddon, { type: K }>, ctx: AddonRenderContext) => React.ReactNode;
};

const leafAddonRenderers = {
    audioPlayer: (addon, ctx) => <AudioPlayerAddon addon={addon} stopCardInteraction={ctx.stopCardInteraction} />,
    audioVisualizer: (addon, ctx) => (
        <AudioVisualizerAddon addon={addon} stopCardInteraction={ctx.stopCardInteraction} />
    ),
    sublinks: (addon, ctx) => (
        <SublinksAddon
            addon={addon}
            stopCardInteraction={ctx.stopCardInteraction}
            onSublinkActivate={ctx.onSublinkActivate}
            SubLinkRow={ctx.SubLinkRow}
        />
    ),
} satisfies LeafAddonRendererMap;

function renderLeafAddon(addon: LinkCardLeafAddon, ctx: AddonRenderContext): React.ReactNode {
    switch (addon.type) {
        case 'audioPlayer':
            return leafAddonRenderers.audioPlayer(addon, ctx);
        case 'audioVisualizer':
            return leafAddonRenderers.audioVisualizer(addon, ctx);
        case 'sublinks':
            return leafAddonRenderers.sublinks(addon, ctx);
        default: {
            const _exhaustive: never = addon;
            return _exhaustive;
        }
    }
}

const addonRenderers = {
    audioPlayer: (addon, ctx) => renderLeafAddon(addon, ctx),
    audioVisualizer: (addon, ctx) => renderLeafAddon(addon, ctx),
    sublinks: (addon, ctx) => renderLeafAddon(addon, ctx),
    composite: (addon: LinkCardCompositeAddon, ctx) => (
        <CompositeAddon
            addon={addon}
            stopCardInteraction={ctx.stopCardInteraction}
            renderLeafAddon={(leaf) => renderLeafAddon(leaf, ctx)}
        />
    ),
} satisfies AddonRendererMap;

export function renderLinkCardAddon(addon: LinkCardAddon | undefined, ctx: AddonRenderContext): React.ReactNode {
    if (!addon) return null;

    switch (addon.type) {
        case 'audioPlayer':
            return addonRenderers.audioPlayer(addon, ctx);
        case 'audioVisualizer':
            return addonRenderers.audioVisualizer(addon, ctx);
        case 'sublinks':
            return addonRenderers.sublinks(addon, ctx);
        case 'composite':
            return addonRenderers.composite(addon, ctx);
        default: {
            const _exhaustive: never = addon;
            return _exhaustive;
        }
    }
}

