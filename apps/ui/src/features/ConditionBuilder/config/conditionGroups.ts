// src/features/ConditionBuilder/config/conditionGroups.ts
export const CONDITION_GROUPS = [
  { key: 'linreg',           label: 'Linear Regression',          params: [{ name: 'series', type: 'series' }, { name: 'period', type: 'number' }] },
  { key: 'linreg_slope',     label: 'Linear Regression Slope',    params: [{ name: 'series', type: 'series' }, { name: 'period', type: 'number' }] },
  { key: 'linreg_intercept', label: 'Linear Regression Intercept',params: [{ name: 'series', type: 'series' }, { name: 'period', type: 'number' }] },
  { key: 'linreg_angle',     label: 'Linear Regression Angle',    params: [{ name: 'series', type: 'series' }, { name: 'period', type: 'number' }] },
  // later
  { key: 'rsi',              label: 'RSI',                        params: [{ name: 'series', type: 'series' }, { name: 'period', type: 'number' }] },
  { key: 'ema',              label: 'EMA',                        params: [{ name: 'series', type: 'series' }, { name: 'period', type: 'number' }] },
  { key: 'harami',           label: 'Harami',                     params: [{ name: 'lookback', type: 'number' }] },
] as const;
