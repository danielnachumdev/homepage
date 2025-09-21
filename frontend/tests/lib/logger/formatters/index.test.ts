import { describe, it, expect } from 'vitest';
import {
    BaseFormatter,
    SimpleFormatter,
    StandardFormatter,
    JSONFormatter,
    ColoredFormatter,
} from '../../../../src/lib/logger/formatters';
import { LogLevel } from '../../../../src/lib/logger/types';

describe('Formatters Index', () => {
    it('should export all formatter classes', () => {
        expect(BaseFormatter).toBeDefined();
        expect(SimpleFormatter).toBeDefined();
        expect(StandardFormatter).toBeDefined();
        expect(JSONFormatter).toBeDefined();
        expect(ColoredFormatter).toBeDefined();
    });

    it('should create instances of all formatters', () => {
        const simpleFormatter = new SimpleFormatter();
        const standardFormatter = new StandardFormatter();
        const jsonFormatter = new JSONFormatter();
        const coloredFormatter = new ColoredFormatter();

        expect(simpleFormatter).toBeInstanceOf(BaseFormatter);
        expect(standardFormatter).toBeInstanceOf(BaseFormatter);
        expect(jsonFormatter).toBeInstanceOf(BaseFormatter);
        expect(coloredFormatter).toBeInstanceOf(BaseFormatter);
    });

    it('should format records correctly', () => {
        const record = {
            name: 'test-logger',
            level: LogLevel.INFO,
            levelName: 'INFO',
            message: 'Test message',
            timestamp: new Date('2023-01-01T12:00:00.000Z'),
            module: 'test.ts',
            function: 'testFunction',
            line: 42,
            args: [{ data: 'test' }],
            extra: { userId: 123 }
        };

        const simpleFormatter = new SimpleFormatter();
        const standardFormatter = new StandardFormatter();
        const jsonFormatter = new JSONFormatter();
        const coloredFormatter = new ColoredFormatter();

        const simpleResult = simpleFormatter.format(record);
        const standardResult = standardFormatter.format(record);
        const jsonResult = jsonFormatter.format(record);
        const coloredResult = coloredFormatter.format(record);

        expect(simpleResult).toBe('Test message');
        expect(standardResult).toContain('Test message');
        expect(JSON.parse(jsonResult)).toMatchObject({
            name: 'test-logger',
            level: 'INFO',
            message: 'Test message'
        });
        expect(coloredResult).toContain('Test message');
        expect(coloredResult).toContain('\x1b[32m'); // Green for INFO
        expect(coloredResult).toContain('\x1b[0m'); // Reset
    });
});
