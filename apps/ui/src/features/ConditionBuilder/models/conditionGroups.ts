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
const RAW_GROUPS: ConditionGroup[] = [
  // ---- PriceData
  { label: 'PriceData', options: [
    { key: 'open',               label: 'Open',                                params: [] },
    { key: 'high',               label: 'High',                                params: [] },
    { key: 'low',                label: 'Low',                                 params: [] },
    { key: 'close',              label: 'Close',                               params: [] },
    { key: 'typical_price',      label: 'Typical Price',                       params: [] },
    { key: 'upper_bollinger',    label: 'Upper Bollinger',                     params: [{ name: 'length', type: 'number' }, { name: 'stddev', type: 'number' }, { name: 'series', type: 'series' }] },
    { key: 'lower_bollinger',    label: 'Lower Bollinger',                     params: [{ name: 'length', type: 'number' }, { name: 'stddev', type: 'number' }, { name: 'series', type: 'series' }] },
    { key: 'bbpercentage',       label: 'BB Percentage (%B)',                  params: [{ name: 'length', type: 'number' }, { name: 'stddev', type: 'number' }, { name: 'series', type: 'series' }] },
    { key: 'bb_width',           label: 'Bollinger Band Width',                params: [{ name: 'length', type: 'number' }, { name: 'stddev', type: 'number' }, { name: 'series', type: 'series' }] },
    { key: 'pivot_point',        label: 'Pivot Point',                          params: [{ name: 'session', type: 'select', options: ['daily','weekly','monthly'] }] },
    { key: 'cpr',                label: 'Central Pivot Range',                  params: [{ name: 'session', type: 'select', options: ['daily','weekly','monthly'] }] },
  ]},

  // ---- Technical
  { label: 'Technical', options: [
    { key: 'sma',                label: 'SMA',                                 params: [{ name: 'period', type: 'number' }, { name: 'series', type: 'series' }] },
    { key: 'ema',                label: 'EMA',                                 params: [{ name: 'period', type: 'number' }, { name: 'series', type: 'series' }] },
    { key: 'dema',               label: 'DEMA',                                params: [{ name: 'period', type: 'number' }, { name: 'series', type: 'series' }] },
    { key: 'tema',               label: 'TEMA',                                params: [{ name: 'period', type: 'number' }, { name: 'series', type: 'series' }] },
    { key: 'trima',              label: 'TRIMA',                               params: [{ name: 'period', type: 'number' }, { name: 'series', type: 'series' }] },
    { key: 'hma',                label: 'Hull MA',                             params: [{ name: 'period', type: 'number' }, { name: 'series', type: 'series' }] },
    { key: 'lsma',               label: 'Least Squares MA (LSMA)',             params: [{ name: 'period', type: 'number' }, { name: 'series', type: 'series' }] },
    { key: 'alma',               label: 'ALMA',                                params: [{ name: 'length', type: 'number' }, { name: 'offset', type: 'number' }, { name: 'sigma', type: 'number' }, { name: 'series', type: 'series' }] },

    { key: 'rsi',                label: 'RSI',                                 params: [{ name: 'period', type: 'number' }, { name: 'series', type: 'series' }] },
    { key: 'rsi_series',         label: 'RSI Series',                          params: [{ name: 'period', type: 'number' }, { name: 'series', type: 'series' }] },
    { key: 'stochk',             label: 'Stoch K',                             params: [{ name: 'k', type: 'number' }, { name: 'd', type: 'number' }, { name: 'smooth', type: 'number' }] },
    { key: 'stochd',             label: 'Stoch D',                             params: [{ name: 'k', type: 'number' }, { name: 'd', type: 'number' }, { name: 'smooth', type: 'number' }] },
    { key: 'smi',                label: 'Stochastic Momentum Index',           params: [{ name: 'k', type: 'number' }, { name: 'd', type: 'number' }, { name: 'smooth', type: 'number' }] },
    { key: 'mfi',                label: 'MFI',                                 params: [{ name: 'period', type: 'number' }] },
    { key: 'cci',                label: 'CCI',                                 params: [{ name: 'period', type: 'number' }] },
    { key: 'cmo',                label: 'Chande Momentum Oscillator',          params: [{ name: 'period', type: 'number' }, { name: 'series', type: 'series' }] },
    { key: 'mom',                label: 'Momentum',                            params: [{ name: 'period', type: 'number' }, { name: 'series', type: 'series' }] },
    { key: 'mom_osc',            label: 'Momentum Oscillator',                 params: [{ name: 'period', type: 'number' }, { name: 'series', type: 'series' }] },

    { key: 'macd',               label: 'MACD',                                params: [{ name: 'fast', type: 'number' }, { name: 'slow', type: 'number' }, { name: 'signal', type: 'number' }, { name: 'series', type: 'series' }] },
    { key: 'macdsignal',         label: 'MACD Signal',                         params: [{ name: 'fast', type: 'number' }, { name: 'slow', type: 'number' }, { name: 'signal', type: 'number' }, { name: 'series', type: 'series' }] },
    { key: 'macdhist',           label: 'MACD Histogram',                      params: [{ name: 'fast', type: 'number' }, { name: 'slow', type: 'number' }, { name: 'signal', type: 'number' }, { name: 'series', type: 'series' }] },
    { key: 'ppo',                label: 'Percentage Price Oscillator',         params: [{ name: 'fast', type: 'number' }, { name: 'slow', type: 'number' }, { name: 'signal', type: 'number' }, { name: 'series', type: 'series' }] },

    { key: 'atr',                label: 'ATR',                                 params: [{ name: 'period', type: 'number' }] },
    { key: 'natr',               label: 'Normalized ATR',                      params: [{ name: 'period', type: 'number' }] },
    { key: 'supertrend',         label: 'Supertrend',                          params: [{ name: 'atrPeriod', type: 'number' }, { name: 'multiplier', type: 'number' }] },
    { key: 'st_sma',             label: 'Supertrend (SMA base)',               params: [{ name: 'atrPeriod', type: 'number' }, { name: 'multiplier', type: 'number' }] },

    { key: 'keltner',            label: 'Keltner Channels',                    params: [{ name: 'length', type: 'number' }, { name: 'mult', type: 'number' }, { name: 'series', type: 'series' }] },
    { key: 'keltner_close',      label: 'Keltner Close',                       params: [{ name: 'length', type: 'number' }, { name: 'mult', type: 'number' }, { name: 'series', type: 'series' }] },

    { key: 'fisher',             label: 'Fisher Transform',                    params: [{ name: 'period', type: 'number' }, { name: 'series', type: 'series' }] },
    { key: 'hv',                 label: 'Historical Volatility',               params: [{ name: 'period', type: 'number' }] },
    { key: 'obv',                label: 'OBV',                                 params: [] },

    { key: 'ado',                label: 'Awesome Oscillator',                  params: [{ name: 'fast', type: 'number' }, { name: 'slow', type: 'number' }, { name: 'series', type: 'series' }] }, // alias 'ao'
    { key: 'bop',                label: 'Balance of Power',                    params: [] },
    { key: 'efi',                label: 'Elder Force Index',                   params: [{ name: 'period', type: 'number' }] },

    { key: 'adx',                label: 'ADX',                                 params: [{ name: 'period', type: 'number' }] },
    { key: 'adx_smooth',         label: 'ADX Smooth',                          params: [{ name: 'period', type: 'number' }] },
    { key: 'di_plus',            label: 'DI+',                                 params: [{ name: 'period', type: 'number' }] },
    { key: 'di_minus',           label: 'DI-',                                 params: [{ name: 'period', type: 'number' }] },
    { key: 'aroondown',          label: 'Aroon Down',                          params: [{ name: 'period', type: 'number' }] },
    { key: 'aroonup',            label: 'Aroon Up',                            params: [{ name: 'period', type: 'number' }] },

    { key: 'linreg',             label: 'Linear Regression',                   params: [{ name: 'series', type: 'series' }, { name: 'period', type: 'number' }] },
    { key: 'linreg_slope',       label: 'Linear Regression Slope',             params: [{ name: 'series', type: 'series' }, { name: 'period', type: 'number' }] },
    { key: 'linreg_angle',       label: 'Linear Regression Angle',             params: [{ name: 'series', type: 'series' }, { name: 'period', type: 'number' }] },
    { key: 'linreg_intercept',   label: 'Linear Regression Intercept',         params: [{ name: 'series', type: 'series' }, { name: 'period', type: 'number' }] },

    { key: 'kama',               label: 'Kaufman Adaptive MA (KAMA)',          params: [{ name: 'erPeriod', type: 'number' }, { name: 'fast', type: 'number' }, { name: 'slow', type: 'number' }, { name: 'series', type: 'series' }] },
    { key: 'kei',                label: 'Kaufman Efficiency Indicator',        params: [{ name: 'period', type: 'number' }, { name: 'series', type: 'series' }] },

    { key: 'kst',                label: 'KST',                                 params: [
      { name: 'roc1', type: 'number' }, { name: 'roc2', type: 'number' }, { name: 'roc3', type: 'number' }, { name: 'roc4', type: 'number' },
      { name: 'sma1', type: 'number' }, { name: 'sma2', type: 'number' }, { name: 'sma3', type: 'number' }, { name: 'sma4', type: 'number' },
      { name: 'series', type: 'series' }
    ] },
    { key: 'kst_signal',         label: 'KST Signal',                          params: [{ name: 'signal', type: 'number' }] },

    { key: 'sar',                label: 'Parabolic SAR',                       params: [{ name: 'step', type: 'number' }, { name: 'max', type: 'number' }] },
  ]},

  // ---- Series_Ops (math on time-series)
  { label: 'Series_Ops', options: [
    { key: 'mean',               label: 'Mean (SMA of series)',               params: [{ name: 'period', type: 'number' }, { name: 'series', type: 'series' }] },
    { key: 'median',             label: 'Median (Rolling)',                   params: [{ name: 'period', type: 'number' }, { name: 'series', type: 'series' }] },
    { key: 'stdev',              label: 'Standard Deviation',                 params: [{ name: 'period', type: 'number' }, { name: 'series', type: 'series' }] },
    { key: 'variance',           label: 'Variance (Rolling)',                 params: [{ name: 'period', type: 'number' }, { name: 'series', type: 'series' }] },
    { key: 'sum',                label: 'Sum (Rolling)',                       params: [{ name: 'period', type: 'number' }, { name: 'series', type: 'series' }] },

    { key: 'roc',                label: 'Rate of Change (ROC)',               params: [{ name: 'period', type: 'number' }, { name: 'series', type: 'series' }] },
    { key: 'rocp',               label: 'Rate of Change % (ROCP)',            params: [{ name: 'period', type: 'number' }, { name: 'series', type: 'series' }] },
    { key: 'log',                label: 'Log (Natural ln)',                   params: [{ name: 'series', type: 'series' }] },
    { key: 'log_return',         label: 'Log Return',                          params: [{ name: 'series', type: 'series' }, { name: 'period', type: 'number' }] },

    { key: 'ratio',              label: 'Ratio',                               params: [{ name: 'left', type: 'series' }, { name: 'right', type: 'series' }] },
    { key: 'multiply',           label: 'Multiply Array',                      params: [{ name: 'left', type: 'series' }, { name: 'right', type: 'series' }] },
    { key: 'divide',             label: 'Divide Array',                        params: [{ name: 'left', type: 'series' }, { name: 'right', type: 'series' }] },
    { key: 'subtract',           label: 'Subtract Array',                      params: [{ name: 'left', type: 'series' }, { name: 'right', type: 'series' }] },
    { key: 'power',              label: 'Power',                               params: [{ name: 'base', type: 'series' }, { name: 'exponent', type: 'number' }] },

    { key: 'percentile',         label: 'Percentile',                          params: [{ name: 'period', type: 'number' }, { name: 'q', type: 'number' }, { name: 'series', type: 'series' }] },
    { key: 'percentile_rank',    label: 'Percentile Rank',                     params: [{ name: 'period', type: 'number' }, { name: 'series', type: 'series' }] },

    { key: 'highest_high',       label: 'Highest High Value',                  params: [{ name: 'period', type: 'number' }] },
    { key: 'lowest_low',         label: 'Lowest Low Value',                    params: [{ name: 'period', type: 'number' }] },

    { key: 'donchian_lower',     label: 'Donchian Channel Lower',              params: [{ name: 'period', type: 'number' }] },
    { key: 'donchian_middle',    label: 'Donchian Channel Middle',             params: [{ name: 'period', type: 'number' }] },
    { key: 'donchian_upper',     label: 'Donchian Channel Upper',              params: [{ name: 'period', type: 'number' }] },
    { key: 'donchian_width',     label: 'Donchian Channel Width',              params: [{ name: 'period', type: 'number' }] },
  ]},

  // ---- Candle Patterns (no params)
  { label: 'Candle Patterns', options: [
    { key: 'doji',               label: 'Doji',                               params: [] },
    { key: 'dragonfly_doji',     label: 'Dragonfly Doji',                     params: [] },
    { key: 'gravestone_doji',    label: 'Gravestone Doji',                    params: [] },
    { key: 'hammer',             label: 'Hammer',                             params: [] },
    { key: 'hangingman',         label: 'Hanging Man',                        params: [] },
    { key: 'harami',             label: 'Harami',                             params: [] },
    { key: 'engulfing',          label: 'Engulfing',                          params: [] },
    { key: 'marubozu',           label: 'Marubozu',                           params: [] },
    { key: 'shootingstar',       label: 'Shooting Star',                      params: [] },
    { key: 'morningstar',        label: 'Morning Star',                       params: [] },
    { key: 'morningdojistar',    label: 'Morning Doji Star',                  params: [] },
    // add EveningStar etc. likewise
  ]},

  // ---- Math (pure math helpers)
  { label: 'Math', options: [
    { key: 'sqrt',               label: 'Square Root',                        params: [{ name: 'series', type: 'series' }] },
    { key: 'mean',               label: 'Mean (SMA of series)',               params: [{ name: 'period', type: 'number' }, { name: 'series', type: 'series' }] },
    { key: 'median',             label: 'Median (Rolling)',                   params: [{ name: 'period', type: 'number' }, { name: 'series', type: 'series' }] },
    { key: 'variance',           label: 'Variance (Rolling)',                 params: [{ name: 'period', type: 'number' }, { name: 'series', type: 'series' }] },
  ]},

  // ---- Statistics
  { label: 'Statistics', options: [
    { key: 'percentile',         label: 'Percentile',                         params: [{ name: 'period', type: 'number' }, { name: 'q', type: 'number' }, { name: 'series', type: 'series' }] },
    { key: 'percentile_rank',    label: 'Percentile Rank',                    params: [{ name: 'period', type: 'number' }, { name: 'series', type: 'series' }] },
  ]},

  // ---- DateTime (example — fill out as you add)
  { label: 'DateTime', options: [
    // e.g., { key: 'time', label: 'Time (Exchange)', params: [{ name: 'session', type:'select', options:['NSE','NFO']}] },
  ]},

  // ---- RuntimeVariables (example)
  { label: 'RuntimeVariables', options: [
    // e.g., { key: 'dti', label: 'DTI', params: [{ name: 'period', type: 'number' }] },
  ]},

  // ---- StrategyInfo (example)
  { label: 'StrategyInfo', options: [
    // e.g., { key: 'sentiment_score', label: 'Sentiment Score', params: [] },
  ]},

  // ---- InstrumentFormula (Alligator etc.)
  { label: 'InstrumentFormula', options: [
    { key: 'alligator',          label: 'Alligator',                           params: [
      { name: 'jawLength', type: 'number' }, { name: 'teethLength', type: 'number' }, { name: 'lipsLength', type: 'number' },
      { name: 'output', type: 'select', options: ['jaw','teeth','lips'] }, { name: 'series', type: 'series' }
    ] },
  ]},
  // === Options (parity with your screenshot) ==================================
  { label: 'Options', options: [
    // Put-Call Ratio (OI/Volume) aggregated for the chosen expiry
    { key: 'pcr',               label: 'PCR',                   params: [
      { name: 'basis',     type: 'select', options: ['oi','volume'] },
      { name: 'expirySel', type: 'select', options: ['current_week','next_week','monthly','custom'] },
      { name: 'expiry',    type: 'number' } // used only when custom (yyyymmdd or epoch)
    ] },

    // Total OI (sum across all strikes) – optionally per CE/PE or both
    { key: 'total_oi',          label: 'Total OI',              params: [
      { name: 'side',      type: 'select', options: ['both','CE','PE'] },
      { name: 'expirySel', type: 'select', options: ['current_week','next_week','monthly','custom'] },
      { name: 'expiry',    type: 'number' }
    ] },

    // Strike with maximum OI (returns a strike value)
    { key: 'max_oi_strike',     label: 'Max OI Strike',         params: [
      { name: 'side',      type: 'select', options: ['CE','PE'] },
      { name: 'expirySel', type: 'select', options: ['current_week','next_week','monthly','custom'] },
      { name: 'expiry',    type: 'number' }
    ] },

    // Value of the maximum OI (returns the OI number)
    { key: 'max_oi_value',      label: 'Max OI Value',          params: [
      { name: 'side',      type: 'select', options: ['CE','PE','both'] },
      { name: 'expirySel', type: 'select', options: ['current_week','next_week','monthly','custom'] },
      { name: 'expiry',    type: 'number' }
    ] },

    // Instrument (tradingsymbol) that has the max OI (returns e.g. NIFTY25SEP22500CE)
    { key: 'max_oi_instrument', label: 'Max OI Instrument',     params: [
      { name: 'side',      type: 'select', options: ['CE','PE'] },
      { name: 'expirySel', type: 'select', options: ['current_week','next_week','monthly','custom'] },
      { name: 'expiry',    type: 'number' }
    ] },

    // (Optional handy readers used everywhere)
    { key: 'opt_ltp',           label: 'Option LTP',            params: [
      { name: 'side',      type: 'select', options: ['CE','PE'] },
      { name: 'strikeSel', type: 'select', options: ['ATM','OTM+steps','ITM+steps','ByStrike'] },
      { name: 'steps',     type: 'number' },   // used when OTM/ITM+steps
      { name: 'strike',    type: 'number' },   // used when ByStrike
      { name: 'expirySel', type: 'select', options: ['current_week','next_week','monthly','custom'] },
      { name: 'expiry',    type: 'number' }
    ] },
    { key: 'opt_iv',            label: 'Option IV',             params: [
      { name: 'side',      type: 'select', options: ['CE','PE'] },
      { name: 'strikeSel', type: 'select', options: ['ATM','OTM+steps','ITM+steps','ByStrike'] },
      { name: 'steps',     type: 'number' }, { name: 'strike', type: 'number' },
      { name: 'expirySel', type: 'select', options: ['current_week','next_week','monthly','custom'] },
      { name: 'expiry',    type: 'number' }
    ] },
    { key: 'opt_oi',            label: 'Option OI',             params: [
      { name: 'side',      type: 'select', options: ['CE','PE'] },
      { name: 'strikeSel', type: 'select', options: ['ATM','OTM+steps','ITM+steps','ByStrike'] },
      { name: 'steps',     type: 'number' }, { name: 'strike', type: 'number' },
      { name: 'expirySel', type: 'select', options: ['current_week','next_week','monthly','custom'] },
      { name: 'expiry',    type: 'number' }
    ] },
  ]},
  // === OptionGreeks (submenu right after “Total OI” in your screenshot) =======
  { label: 'OptionGreeks', options: [
    { key: 'greek_delta',       label: 'Delta',                 params: [
      { name: 'side',      type: 'select', options: ['CE','PE'] },
      { name: 'strikeSel', type: 'select', options: ['ATM','OTM+steps','ITM+steps','ByStrike'] },
      { name: 'steps',     type: 'number' }, { name: 'strike', type: 'number' },
      { name: 'expirySel', type: 'select', options: ['current_week','next_week','monthly','custom'] },
      { name: 'expiry',    type: 'number' }
    ] },
    { key: 'greek_gamma',       label: 'Gamma',                 params: [ /* same shape as delta */ ] },
    { key: 'greek_theta',       label: 'Theta',                 params: [ /* same shape */ ] },
    { key: 'greek_vega',        label: 'Vega',                  params: [ /* same shape */ ] },
  ]},
];

// Feature-flag: show/hide Options + OptionGreeks without touching renderers
const ENABLE_OPTIONS = process.env.NEXT_PUBLIC_ENABLE_OPTIONS === 'true';

export const GROUPS: ConditionGroup[] = RAW_GROUPS.map(g =>
  (g.label === 'Options' || g.label === 'OptionGreeks')
    ? (ENABLE_OPTIONS ? g : { ...g, options: [] })   // keep section, hide items
    : g
);
