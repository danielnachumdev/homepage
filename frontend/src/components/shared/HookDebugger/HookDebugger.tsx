import React, { useState } from 'react';
import {
    Box,
    Accordion,
    AccordionSummary,
    AccordionDetails,
    Typography,
    Chip,
    Paper,
    IconButton,
    Tooltip,
} from '@mui/material';
import {
    ExpandMore as ExpandMoreIcon,
    BugReport as BugReportIcon,
    VisibilityOff as VisibilityOffIcon,
    Refresh as RefreshIcon,
} from '@mui/icons-material';
import styles from './HookDebugger.module.css';

export interface HookDebuggerProps {
    /** The name/label for this hook debugger */
    name: string;
    /** The current state/value returned by the hook */
    state: any;
    /** Optional description of what this hook does */
    description?: string;
    /** Whether to show the debugger by default (collapsed/expanded) */
    defaultExpanded?: boolean;
    /** Custom formatter function for displaying the state */
    formatter?: (state: any) => string;
    /** Whether to show a refresh button */
    showRefresh?: boolean;
    /** Callback for refresh action */
    onRefresh?: () => void;
    /** Additional metadata to display */
    metadata?: Record<string, any>;
}

/**
 * Generic component for debugging hook states in the UI.
 * Displays hook state in a collapsible, formatted way.
 */
export function HookDebugger({
    name,
    state,
    description,
    defaultExpanded = false,
    formatter,
    showRefresh = false,
    onRefresh,
    metadata,
}: HookDebuggerProps) {
    const [expanded, setExpanded] = useState(defaultExpanded);
    const [visible, setVisible] = useState(true);

    const formatValue = (value: any): string => {
        if (formatter) {
            return formatter(value);
        }

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

    const renderValue = (value: any, depth = 0): React.ReactNode => {
        const indent = '  '.repeat(depth);

        if (value === null) return <code>null</code>;
        if (value === undefined) return <code>undefined</code>;
        if (typeof value === 'boolean') {
            return (
                <code style={{ color: value ? '#4caf50' : '#f44336' }}>
                    {value.toString()}
                </code>
            );
        }
        if (typeof value === 'number') {
            return <code style={{ color: '#2196f3' }}>{value}</code>;
        }
        if (typeof value === 'string') {
            return <code style={{ color: '#ff9800' }}>"{value}"</code>;
        }
        if (Array.isArray(value)) {
            return (
                <Box>
                    <code>[{value.length} items]</code>
                    {expanded && (
                        <Box sx={{ ml: 2, mt: 1 }}>
                            {value.map((item, index) => (
                                <Box key={index} sx={{ mb: 0.5 }}>
                                    <code>{indent}[{index}]: </code>
                                    {renderValue(item, depth + 1)}
                                </Box>
                            ))}
                        </Box>
                    )}
                </Box>
            );
        }
        if (typeof value === 'object' && value !== null) {
            const keys = Object.keys(value);
            return (
                <Box>
                    <code>{`{${keys.length} keys}`}</code>
                    {expanded && (
                        <Box sx={{ ml: 2, mt: 1 }}>
                            {keys.map((key) => (
                                <Box key={key} sx={{ mb: 0.5 }}>
                                    <code>{indent}{key}: </code>
                                    {renderValue(value[key], depth + 1)}
                                </Box>
                            ))}
                        </Box>
                    )}
                </Box>
            );
        }
        if (typeof value === 'function') {
            return <code style={{ color: '#9c27b0' }}>Function</code>;
        }

        return <code>{String(value)}</code>;
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
        <Box className={styles.debugPanel}>
            <Paper className={styles.debugPanelPaper}>
                <Box className={styles.debugHeader}>
                    <Box className={styles.debugTitleContainer}>
                        <BugReportIcon color="primary" />
                        <Typography variant="h6" component="h3" className={styles.debugTitle}>
                            Hook Debugger
                        </Typography>
                    </Box>
                    <Box className={styles.debugActions}>
                        {showRefresh && onRefresh && (
                            <Tooltip title="Refresh">
                                <IconButton size="small" onClick={onRefresh}>
                                    <RefreshIcon />
                                </IconButton>
                            </Tooltip>
                        )}
                        <Tooltip title="Hide Debug Panel">
                            <IconButton size="small" onClick={() => setVisible(false)}>
                                <VisibilityOffIcon />
                            </IconButton>
                        </Tooltip>
                    </Box>
                </Box>

                <Accordion expanded={expanded} onChange={() => setExpanded(!expanded)} className={styles.debugAccordion}>
                    <AccordionSummary expandIcon={<ExpandMoreIcon />} className={styles.debugAccordionSummary}>
                        <Box className={styles.debugSummaryContent}>
                            <Typography variant="subtitle1" className={styles.debugHookName}>
                                {name}
                            </Typography>
                            <Chip
                                label={getStateType(state)}
                                size="small"
                                className={styles.debugTypeChip}
                                sx={{
                                    bgcolor: getStateTypeColor(getStateType(state)),
                                    color: 'white',
                                }}
                            />
                            <Typography variant="body2" className={styles.debugStatePreview}>
                                {formatValue(state)}
                            </Typography>
                        </Box>
                    </AccordionSummary>
                    <AccordionDetails className={styles.debugAccordionDetails}>
                        <Box>
                            {description && (
                                <Typography variant="body2" className={styles.debugDescription}>
                                    {description}
                                </Typography>
                            )}

                            <Typography variant="subtitle2" className={styles.debugSectionTitle}>
                                Current State:
                            </Typography>
                            <Box className={styles.debugStateContainer}>
                                {renderValue(state)}
                            </Box>

                            {metadata && Object.keys(metadata).length > 0 && (
                                <>
                                    <Typography variant="subtitle2" className={styles.debugSectionTitle} style={{ marginTop: 16 }}>
                                        Metadata:
                                    </Typography>
                                    <Box className={styles.debugMetadataContainer}>
                                        {Object.entries(metadata).map(([key, value]) => (
                                            <Box key={key} className={styles.debugValue}>
                                                <code>{key}: </code>
                                                {renderValue(value)}
                                            </Box>
                                        ))}
                                    </Box>
                                </>
                            )}
                        </Box>
                    </AccordionDetails>
                </Accordion>
            </Paper>
        </Box>
    );
}
