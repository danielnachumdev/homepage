import type { LogRecord, Handler, Formatter } from '../types';
import { LogLevel } from '../types';
import { BaseHandler } from './BaseHandler';

/**
 * Remote handler for sending logs to a server
 */
export class RemoteHandler extends BaseHandler {
    private endpoint: string;
    private batchSize: number;
    private batchTimeout: number;
    private batch: LogRecord[] = [];
    private timeoutId?: number;

    constructor(
        endpoint: string,
        level: LogLevel = LogLevel.ERROR,
        batchSize: number = 10,
        batchTimeout: number = 5000,
        formatter?: Formatter
    ) {
        super(level, formatter);
        this.endpoint = endpoint;
        this.batchSize = batchSize;
        this.batchTimeout = batchTimeout;
    }

    emit(record: LogRecord): void {
        this.batch.push(record);

        if (this.batch.length >= this.batchSize) {
            this.flush();
        } else if (!this.timeoutId) {
            this.timeoutId = window.setTimeout(() => this.flush(), this.batchTimeout);
        }
    }

    flush(): void {
        if (this.batch.length === 0) {
            return;
        }

        const logs = this.batch.map(record => this.format(record));
        this.batch = [];

        if (this.timeoutId) {
            clearTimeout(this.timeoutId);
            this.timeoutId = undefined;
        }

        // Send logs to server
        fetch(this.endpoint, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ logs }),
        }).catch(error => {
            console.error('Failed to send logs to server:', error);
        });
    }

    close(): void {
        this.flush();
    }
}
