// apps/ui/src/features/ConditionBuilder/models/conditionGroups.ts

// ---------- Param & option types (upgrade) ----------
export type ParamDef =
  | { name: 'series'; type: 'series' }
  | { name: 'period'; type: 'number'; min?: number; max?: number; step?: number }
  | { name: string; type: 'select' | 'underlying' | 'synthetic' | 'priceSource' | 'number'; min?: number; max?: number; step?: number; options?: string[]; placeholder?: string };

export interface ConditionOption {
  key: string;
  label: string;
  // ⬅️ was string[]; we now support structured params
  params: ParamDef[];
}

export interface ConditionGroup {
  label: string;
  options: ConditionOption[];
}

// ---------- Tradetron-like preview helpers ----------
type Params = Record<string, unknown>;

// tail shared across linear regression family
const linregTail = (p: Params) => {
  const SERIES = String(p.series ?? '—').toUpperCase();
  const PERIOD = p.period ?? '—';
  // Match Tradetron’s exact text
  return `${SERIES} ( Symbol | Instrument Name ( ), day, All ), ${PERIOD}`;
};

// One place to map a key to a preview function
const PREVIEW_BY_KEY: Record<string, (p: Params) => string> = {
  // linear regression family – support both underscore and non-underscore keys
  linreg:           (p) => `LINEARREG\n${linregTail(p)}`,
  linearreg:        (p) => `LINEARREG\n${linregTail(p)}`,

  linregslope:      (p) => `LINEARREG_SLOPE\n${linregTail(p)}`,
  linreg_slope:     (p) => `LINEARREG_SLOPE\n${linregTail(p)}`,
  linearregslope:   (p) => `LINEARREG_SLOPE\n${linregTail(p)}`,

  linregintercept:  (p) => `LINEARREG_INTERCEPT\n${linregTail(p)}`,
  linreg_intercept: (p) => `LINEARREG_INTERCEPT\n${linregTail(p)}`,
  linearregintercept: (p) => `LINEARREG_INTERCEPT\n${linregTail(p)}`,

  linregangle:      (p) => `LINEARREG_ANGLE\n${linregTail(p)}`,
  linreg_angle:     (p) => `LINEARREG_ANGLE\n${linregTail(p)}`,
  linearregangle:   (p) => `LINEARREG_ANGLE\n${linregTail(p)}`,

  // ready for next indicators (examples)
  rsi:              (p) => `RSI\n${String(p.series ?? '—').toUpperCase()} ( ${p.period ?? '—'} )`,
  ema:              (p) => `EMA\n${String(p.series ?? '—').toUpperCase()} ( ${p.period ?? '—'} )`,
  harami:           (p) => `HARAMI\nLookback ${p['lookback'] ?? '—'}`,
};

// Public helper used by ChooseBlock (no switches anywhere else)
export function buildPreviewFromKey(key: string, params: Params, fallbackLabel?: string) {
  const fn = PREVIEW_BY_KEY[key.toLowerCase()];
  if (fn) return fn(params);
  const pretty =
    Object.entries(params).map(([k, v]) => `${k}=${v ?? '—'}`).join(', ') || '—';
  return `${(fallbackLabel || key).toUpperCase()}\n${pretty}`;
}

// ---------- Your existing GROUPS (kept, but with structured params) ----------
export const GROUPS: ConditionGroup[] = [
  {
    label: 'Basic Price',
    options: [
      { key: 'avgprice', label: 'Average Price', params: [] },
      { key: 'medprice', label: 'Median Price', params: [] },
      { key: 'typprice', label: 'Typical Price', params: [] },
    ],
  },
  {
    label: 'Volatility',
    options: [
      { key: 'atr',  label: 'Average True Range (ATR)', params: [{ name: 'period', type: 'number' }] },
      { key: 'natr', label: 'Normalized ATR',          params: [{ name: 'period', type: 'number' }] },
      { key: 'bbands', label: 'Bollinger Bands',        params: [{ name: 'period', type: 'number' }, { name: 'series', type: 'series' }] },
      { key: 'var', label: 'Variance Over Period',      params: [{ name: 'period', type: 'number' }] },
    ],
  },
  {
    label: 'Momentum & Oscillators',
    options: [
      { key: 'rsi',  label: 'RSI', params: [{ name: 'period', type: 'number' }, { name: 'series', type: 'series' }] },
      { key: 'cmo',  label: 'Chande Momentum Oscillator (CMO)', params: [{ name: 'period', type: 'number' }, { name: 'series', type: 'series' }] },
      { key: 'macd', label: 'MACD', params: [
        { name: 'fast', type: 'number' },
        { name: 'slow', type: 'number' },
        { name: 'signal', type: 'number' }
      ] },
      { key: 'mfi',  label: 'Money Flow Index (MFI)', params: [{ name: 'period', type: 'number' }] },
      { key: 'stoch', label: 'Stochastic Oscillator', params: [
        { name: 'fastK', type: 'number' },
        { name: 'slowK', type: 'number' },
        { name: 'slowD', type: 'number' }
      ] },
      { key: 'ultosc', label: 'Ultimate Oscillator', params: [
        { name: 'period1', type: 'number' },
        { name: 'period2', type: 'number' },
        { name: 'period3', type: 'number' }
      ] },
    ],
  },
  {
    label: 'Trend & Smoothing',
    options: [
      { key: 'ema',  label: 'Exponential Moving Avg (EMA)', params: [{ name: 'period', type: 'number' }, { name: 'series', type: 'series' }] },
      { key: 'sma',  label: 'Simple Moving Avg (SMA)',      params: [{ name: 'period', type: 'number' }, { name: 'series', type: 'series' }] },
      { key: 'tema', label: 'Triple EMA (TEMA)',            params: [{ name: 'period', type: 'number' }, { name: 'series', type: 'series' }] },
      { key: 'dema', label: 'Double EMA (DEMA)',            params: [{ name: 'period', type: 'number' }, { name: 'series', type: 'series' }] },

      // ✅ Linear Regression family (series + period)
      { key: 'linreg',           label: 'Linear Regression',          params: [{ name: 'series', type: 'series' }, { name: 'period', type: 'number' }] },
      { key: 'linregangle',      label: 'Linear Regression Angle',    params: [{ name: 'series', type: 'series' }, { name: 'period', type: 'number' }] },
      { key: 'linregintercept',  label: 'Linear Regression Intercept',params: [{ name: 'series', type: 'series' }, { name: 'period', type: 'number' }] },
      { key: 'linregslope',      label: 'Linear Regression Slope',    params: [{ name: 'series', type: 'series' }, { name: 'period', type: 'number' }] },
    ],
  },
];
