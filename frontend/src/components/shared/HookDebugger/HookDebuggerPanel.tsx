import { useState } from 'react';
import {
    Box,
    Paper,
    Typography,
    IconButton,
    Tooltip,
    Accordion,
    AccordionSummary,
    AccordionDetails,
    Chip,
    Stack,
} from '@mui/material';
import {
    BugReport as BugReportIcon,
    VisibilityOff as VisibilityOffIcon,
    ExpandMore as ExpandMoreIcon,
    Settings as SettingsIcon,
} from '@mui/icons-material';
import styles from './HookDebuggerPanel.module.css';

export interface HookDebugInfo {
    /** Unique identifier for this hook */
    id: string;
    /** Display name for the hook */
    name: string;
    /** Current state/value returned by the hook */
    state: any;
    /** Optional description of what this hook does */
    description?: string;
    /** Custom formatter function for displaying the state */
    formatter?: (state: any) => string;
    /** Whether to show a refresh button */
    showRefresh?: boolean;
    /** Callback for refresh action */
    onRefresh?: () => void;
    /** Additional metadata to display */
    metadata?: Record<string, any>;
}

export interface HookDebuggerPanelProps {
    /** Array of hook debug information */
    hooks: HookDebugInfo[];
    /** Whether the panel is visible by default */
    defaultVisible?: boolean;
    /** Whether the panel is expanded by default */
    defaultExpanded?: boolean;
    /** Custom title for the debug panel */
    title?: string;
    /** Position of the debug panel */
    position?: 'top-right' | 'top-left' | 'bottom-right' | 'bottom-left';
}

/**
 * Panel component for debugging multiple hooks at once.
 * Provides a consolidated view of all hook states.
 */
export function HookDebuggerPanel({
    hooks,
    defaultVisible = false,
    defaultExpanded = false,
    title = 'Hook Debug Panel',
    position = 'bottom-right',
}: HookDebuggerPanelProps) {
    const [visible, setVisible] = useState(defaultVisible);
    const [expanded, setExpanded] = useState(defaultExpanded);
    const [expandedHooks, setExpandedHooks] = useState<Set<string>>(new Set());

    const toggleHookExpansion = (hookId: string) => {
        setExpandedHooks(prev => {
            const newSet = new Set(prev);
            if (newSet.has(hookId)) {
                newSet.delete(hookId);
            } else {
                newSet.add(hookId);
            }
            return newSet;
        });
    };

    const getPositionClass = () => {
        switch (position) {
            case 'top-left':
                return styles.debugPanelTopLeft;
            case 'bottom-right':
                return styles.debugPanelBottomRight;
            case 'bottom-left':
                return styles.debugPanelBottomLeft;
            case 'top-right':
            default:
                return styles.debugPanelTopRight;
        }
    };

    const getStateType = (value: any): string => {
        if (value === null) return 'null';
        if (Array.isArray(value)) return 'array';
        return typeof value;
    };

    const getStateTypeColor = (type: string): string => {
        switch (type) {
            case 'boolean': return '#4caf50';
            case 'number': return '#2196f3';
            case 'string': return '#ff9800';
            case 'object': return '#9c27b0';
            case 'array': return '#e91e63';
            case 'function': return '#673ab7';
            case 'null': return '#757575';
            case 'undefined': return '#9e9e9e';
            default: return '#000000';
        }
    };

    const formatValue = (value: any): string => {
        if (value === null) return 'null';
        if (value === undefined) return 'undefined';
        if (typeof value === 'boolean') return value.toString();
        if (typeof value === 'number') return value.toString();
        if (typeof value === 'string') return `"${value}"`;
        if (Array.isArray(value)) return `Array(${value.length})`;
        if (typeof value === 'object') {
            const keys = Object.keys(value);
            return `Object{${keys.length} keys}`;
        }
        if (typeof value === 'function') return 'Function';

        return String(value);
    };

    if (!visible) {
        return (
            <Tooltip title="Show Debug Panel">
                <IconButton
                    onClick={() => setVisible(true)}
                    className={styles.debugToggleButton}
                >
                    <BugReportIcon />
                </IconButton>
            </Tooltip>
        );
    }

    return (
        <Box className={`${styles.debugPanel} ${getPositionClass()}`}>
            <Paper className={styles.debugPanelPaper}>
                <Box className={styles.debugHeader}>
                    <Box className={styles.debugTitleContainer}>
                        <BugReportIcon color="primary" />
                        <Typography variant="h6" component="h3" className={styles.debugTitle}>
                            {title}
                        </Typography>
                        <Chip
                            label={`${hooks.length} hooks`}
                            size="small"
                            color="primary"
                            variant="outlined"
                            className={styles.debugHookCount}
                        />
                    </Box>
                    <Box className={styles.debugActions}>
                        <Tooltip title="Toggle All">
                            <IconButton size="small" onClick={() => setExpanded(!expanded)}>
                                <SettingsIcon />
                            </IconButton>
                        </Tooltip>
                        <Tooltip title="Hide Debug Panel">
                            <IconButton size="small" onClick={() => setVisible(false)}>
                                <VisibilityOffIcon />
                            </IconButton>
                        </Tooltip>
                    </Box>
                </Box>

                <Box className={styles.debugContent}>
                    <Stack className={styles.debugHooksList}>
                        {hooks.map((hook) => (
                            <Accordion
                                key={hook.id}
                                expanded={expandedHooks.has(hook.id)}
                                onChange={() => toggleHookExpansion(hook.id)}
                                className={styles.debugAccordion}
                                classes={{
                                    expanded: styles.debugAccordionExpanded
                                }}
                            >
                                <AccordionSummary
                                    expandIcon={<ExpandMoreIcon />}
                                    className={styles.debugAccordionSummary}
                                    classes={{
                                        expanded: styles.debugAccordionSummaryExpanded
                                    }}
                                >
                                    <Box className={styles.debugSummaryContent}>
                                        <Typography variant="subtitle2" className={styles.debugHookName}>
                                            {hook.name}
                                        </Typography>
                                        <Chip
                                            label={getStateType(hook.state)}
                                            size="small"
                                            className={styles.debugTypeChip}
                                            sx={{
                                                bgcolor: getStateTypeColor(getStateType(hook.state)),
                                                color: 'white',
                                            }}
                                        />
                                        <Typography
                                            variant="body2"
                                            className={styles.debugStatePreview}
                                        >
                                            {hook.formatter ? hook.formatter(hook.state) : formatValue(hook.state)}
                                        </Typography>
                                    </Box>
                                </AccordionSummary>
                                <AccordionDetails className={styles.debugAccordionDetails}>
                                    <Box>
                                        {hook.description && (
                                            <Typography
                                                variant="body2"
                                                className={styles.debugDescription}
                                            >
                                                {hook.description}
                                            </Typography>
                                        )}

                                        <Typography variant="subtitle2" className={styles.debugSectionTitle}>
                                            Current State:
                                        </Typography>
                                        <Box className={styles.debugStateContainer}>
                                            <pre>
                                                {JSON.stringify(hook.state, null, 2)}
                                            </pre>
                                        </Box>

                                        {hook.metadata && Object.keys(hook.metadata).length > 0 && (
                                            <>
                                                <Typography variant="subtitle2" className={styles.debugSectionTitle} style={{ marginTop: 16 }}>
                                                    Metadata:
                                                </Typography>
                                                <Box className={styles.debugMetadataContainer}>
                                                    <pre>
                                                        {JSON.stringify(hook.metadata, null, 2)}
                                                    </pre>
                                                </Box>
                                            </>
                                        )}

                                        {hook.showRefresh && hook.onRefresh && (
                                            <Box className={styles.debugRefreshButton}>
                                                <IconButton size="small" onClick={hook.onRefresh}>
                                                    <SettingsIcon />
                                                </IconButton>
                                            </Box>
                                        )}
                                    </Box>
                                </AccordionDetails>
                            </Accordion>
                        ))}
                    </Stack>
                </Box>
            </Paper>
        </Box>
    );
}
