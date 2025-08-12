// src/features/ConditionBuilder/config/indicatorRegistry.ts
import type { IndicatorDef } from '../types';

const seriesParam = { name: 'series', label: 'Series', type: 'series', required: true } as const;
const periodParam = { name: 'period', label: 'Period', type: 'number', min: 1, step: 1, required: true } as const;

const LinRegCommon: IndicatorDef['params'] = [seriesParam, periodParam];

const INDICATORS: IndicatorDef[] = [
  {
    key: 'linreg',
    label: 'Linear Regression',
    group: 'Technical',
    params: LinRegCommon,
    preview: (p) => `${String(p.series)} ( Symbol | ${String(p.period)} )`,
  },
  {
    key: 'linreg_slope',
    label: 'Linear Regression Slope',
    group: 'Technical',
    params: LinRegCommon,
    preview: (p) => `LINEARREG_SLOPE\n${String(p.series)} ( Symbol | ${String(p.period)} )`,
  },
  {
    key: 'linreg_intercept',
    label: 'Linear Regression Intercept',
    group: 'Technical',
    params: LinRegCommon,
    preview: (p) => `LINEARREG_INTERCEPT\n${String(p.series)} ( Symbol | ${String(p.period)} )`,
  },
  {
    key: 'linreg_angle',
    label: 'Linear Regression Angle',
    group: 'Technical',
    params: LinRegCommon,
    preview: (p) => `LINEARREG_ANGLE\n${String(p.series)} ( Symbol | ${String(p.period)} )`,
  },

  // 🔜 easy future adds:
  {
    key: 'rsi',
    label: 'RSI',
    group: 'Technical',
    params: [seriesParam, periodParam],
    preview: (p) => `RSI\n${String(p.series)} ( ${String(p.period)} )`,
  },
  {
    key: 'ema',
    label: 'EMA',
    group: 'Technical',
    params: [seriesParam, periodParam],
    preview: (p) => `EMA\n${String(p.series)} ( ${String(p.period)} )`,
  },
  {
    key: 'harami',
    label: 'Harami',
    group: 'Candle',
    params: [{ name: 'lookback', label: 'Lookback', type: 'number', min: 1, step: 1, required: true }],
    preview: (p) => `HARAMI\nLookback ${String(p.lookback)}`,
  },
];

export const IndicatorRegistry = new Map(INDICATORS.map(i => [i.key, i]));
export const IndicatorList = INDICATORS; // convenient for menus
