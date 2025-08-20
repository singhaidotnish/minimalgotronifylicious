// apps/ui/src/features/ConditionBuilder/utils/previewBuilder.ts
type Params = Record<string, unknown>;

/**
 * Build a Tradetron-style two-line preview.
 * Examples:
 * LINEARREG_SLOPE
 * CLOSE ( Symbol | Instrument Name ( ), day, All ), 14
 */
export function buildPreview(keyword: string, params: Params, fallbackLabel?: string): string {
  const k = keyword.toLowerCase().replace(/\s+/g, '');
  const SERIES = String(params.series ?? '—').toUpperCase();
  const PERIOD = params.period ?? '—';

  // the bit after the first line is the same across LINREG family
  const linregTail = `${SERIES} ( Symbol | Instrument Name ( ), day, All ), ${PERIOD}`;

  switch (k) {
    case 'linreg':
    case 'linearreg':
      return `LINEARREG\n${linregTail}`;

    case 'linregslope':
    case 'linreg_slope':
    case 'linearregslope':
      return `LINEARREG_SLOPE\n${linregTail}`;

    case 'linregintercept':
    case 'linreg_intercept':
    case 'linearregintercept':
      return `LINEARREG_INTERCEPT\n${linregTail}`;

    case 'linregangle':
    case 'linreg_angle':
    case 'linearregangle':
      return `LINEARREG_ANGLE\n${linregTail}`;

    // ready for next round you asked for
    case 'rsi':
      return `RSI\n${SERIES} ( ${PERIOD} )`;

    case 'ema':
      return `EMA\n${SERIES} ( ${PERIOD} )`;

    case 'harami': {
      const LB = params.lookback ?? '—';
      return `HARAMI\nLookback ${LB}`;
    }

    default: {
      const pretty =
        Object.entries(params)
          .map(([k, v]) => `${k}=${v ?? '—'}`)
          .join(', ') || '—';
      return `${(fallbackLabel || keyword).toUpperCase()}\n${pretty}`;
    }
  }
}
