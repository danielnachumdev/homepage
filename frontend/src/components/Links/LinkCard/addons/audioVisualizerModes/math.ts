export function clamp01(v: number): number {
    if (!Number.isFinite(v)) return 0;
    if (v <= 0) return 0;
    if (v >= 1) return 1;
    return v;
}

/**
 * Normalized exponential easing of a fraction in [0..1].
 * - base <= 1: identity
 * - base > 1: emphasizes values near 0 as base grows
 */
export function warpFrac(frac01: number, base: number): number {
    const f = clamp01(frac01);
    if (!Number.isFinite(base) || base <= 1) return f;
    return (Math.pow(base, f) - 1) / (base - 1);
}

/**
 * Map 0..1 -> [minBin..maxBin] logarithmically, with additional curvature controlled by `base`.
 */
export function getLogBinIndex(frac01: number, nBins: number, base: number): number {
    const minBin = 2;
    const maxBin = Math.max(minBin, nBins - 1);
    const f = warpFrac(frac01, base);
    const logMin = Math.log(minBin);
    const logMax = Math.log(maxBin);
    return Math.floor(Math.exp(logMin + f * (logMax - logMin)));
}

