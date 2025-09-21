import type { LogRecord, Handler, Formatter } from '../types';
import { LogLevel } from '../types';
import { BaseHandler } from './BaseHandler';

/**
 * File handler for persistent logging (using browser's download API)
 */
export class FileHandler extends BaseHandler {
    private logs: string[] = [];
    private maxSize: number;
    private fileName: string;

    constructor(
        fileName: string = 'app.log',
        level: LogLevel = LogLevel.INFO,
        maxSize: number = 1000,
        formatter?: Formatter
    ) {
        super(level, formatter);
        this.fileName = fileName;
        this.maxSize = maxSize;
    }

    emit(record: LogRecord): void {
        const message = this.format(record);
        this.logs.push(message);

        // Keep only the last maxSize logs
        if (this.logs.length > this.maxSize) {
            this.logs = this.logs.slice(-this.maxSize);
        }
    }

    flush(): void {
        if (this.logs.length === 0) {
            return;
        }

        const content = this.logs.join('\n');
        const blob = new Blob([content], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);

        const link = document.createElement('a');
        link.href = url;
        link.download = this.fileName;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(url);

        this.logs = [];
    }
}
