import type { LogRecord } from '../types';
import { BaseFormatter } from './BaseFormatter';

/**
 * JSON formatter for structured logging
 */
export class JSONFormatter extends BaseFormatter {
    format(record: LogRecord): string {
        return JSON.stringify({
            timestamp: record.timestamp.toISOString(),
            name: record.name,
            level: record.levelName,
            message: record.message,
            module: record.module,
            function: record.function,
            line: record.line,
            args: record.args,
            extra: record.extra,
        });
    }
}
