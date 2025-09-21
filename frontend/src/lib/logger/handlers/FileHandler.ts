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
    private fullPath: string;

    constructor(
        fileName: string = 'app.log',
        level: LogLevel = LogLevel.INFO,
        maxSize: number = 1000,
        formatter?: Formatter
    ) {
        super(level, formatter);
        this.fileName = fileName;
        this.maxSize = maxSize;

        // Create fully qualified path
        this.fullPath = this.createFullPath(fileName);

        // Log the fully qualified path to console
        console.log(`[FileHandler] Initialized with fully qualified path: ${this.fullPath}`);
    }

    private createFullPath(fileName: string): string {
        // Get the current timestamp for unique file naming
        const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
        const timestampedFileName = fileName.replace('.log', `-${timestamp}.log`);

        // Create a fully qualified path using the browser's download directory
        // In a browser environment, we'll use a descriptive path that shows the intended location
        const basePath = window.location.origin;
        const fullPath = `${basePath}/logs/${timestampedFileName}`;

        return fullPath;
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

        // Extract just the filename from the full path for download
        const downloadFileName = this.fullPath.split('/').pop() || this.fileName;

        const link = document.createElement('a');
        link.href = url;
        link.download = downloadFileName;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(url);

        // Log the flush action with the full path
        console.log(`[FileHandler] Flushed logs to file: ${this.fullPath}`);

        this.logs = [];
    }

    /**
     * Get the fully qualified path for this file handler
     */
    getFullPath(): string {
        return this.fullPath;
    }
}
