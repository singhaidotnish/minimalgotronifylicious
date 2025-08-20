'use client';

import React, { useRef, useEffect } from 'react';
import {
  createChart,
  CrosshairMode,
  LineStyle,
  UTCTimestamp,
  type ISeriesApi,
} from 'lightweight-charts';

type SeriesKind = 'Line' | 'Area' | 'Candlestick' | 'Bar';

// derive chart instance type (safe), but DON'T look up methods on it in types
type ChartApi = ReturnType<typeof createChart>;

// Describe ONLY what we need the chart to have for compile-time safety
interface ChartWithAdders {
  addLineSeries: (opts?: unknown) => ISeriesApi<'Line'>;
  addAreaSeries: (opts?: unknown) => ISeriesApi<'Area'>;
  addCandlestickSeries: (opts?: unknown) => ISeriesApi<'Candlestick'>;
  addBarSeries: (opts?: unknown) => ISeriesApi<'Bar'>;
}

type AnySeries =
  | ISeriesApi<'Line'>
  | ISeriesApi<'Area'>
  | ISeriesApi<'Candlestick'>
  | ISeriesApi<'Bar'>;

export default function FallbackChart({ type, width, height }: { type: SeriesKind; width: number; height: number; }) {
  const containerRef = useRef<HTMLDivElement>(null);
  const chartRef = useRef<ChartApi | null>(null);
  const seriesRef = useRef<AnySeries | null>(null);

  useEffect(() => {
    if (!containerRef.current) return;

    const chart = createChart(containerRef.current, {
      width,
      height,
      layout: { background: { color: '#000' }, textColor: '#fff' },
      timeScale: { timeVisible: true },
      crosshair: { mode: CrosshairMode.Normal },
    });

    chartRef.current = chart;

    // --- create initial series
    const c = chartRef.current as unknown as ChartWithAdders;
    switch (type) {
      case 'Candlestick':
        seriesRef.current = c.addCandlestickSeries({});
        break;
      case 'Bar':
        seriesRef.current = c.addBarSeries({});
        break;
      case 'Area':
        seriesRef.current = c.addAreaSeries({
          // sample styling
          topColor: 'rgba(33, 150, 243, 0.56)',
          bottomColor: 'rgba(33, 150, 243, 0.04)',
        });
        break;
      case 'Line':
      default:
        seriesRef.current = c.addLineSeries({ lineStyle: LineStyle.Solid });
    }

    return () => {
      chart.remove();
      chartRef.current = null;
      seriesRef.current = null;
    };
  }, []); // once

  useEffect(() => {
    if (!chartRef.current) return;
    chartRef.current.applyOptions({ width, height });

    // rebuild series on type change
    if (seriesRef.current) {
      chartRef.current.removeSeries(seriesRef.current);
      seriesRef.current = null;
    }

    const c = chartRef.current as unknown as ChartWithAdders;
    switch (type) {
      case 'Candlestick':
        seriesRef.current = c.addCandlestickSeries({});
        break;
      case 'Bar':
        seriesRef.current = c.addBarSeries({});
        break;
      case 'Area':
        seriesRef.current = c.addAreaSeries({
          topColor: 'rgba(33, 150, 243, 0.56)',
          bottomColor: 'rgba(33, 150, 243, 0.04)',
        });
        break;
      case 'Line':
      default:
        seriesRef.current = c.addLineSeries({ lineStyle: LineStyle.Solid });
    }

    // dummy data (same as before) ...
    const now = Date.now();
    const points = Array.from({ length: 120 }).map((_, i) => {
      const t = (now - (120 - i) * 60_000) / 1000 as UTCTimestamp;
      const base = 100 + Math.sin(i / 8) * 2 + (Math.random() - 0.5) * 0.5;
      return {
        time: t,
        value: base,
        open: base * 0.995,
        high: base * 1.01,
        low: base * 0.99,
        close: base,
      };
    });

    if (!seriesRef.current) return;

    if (type === 'Candlestick' || type === 'Bar') {
      (seriesRef.current as ISeriesApi<'Candlestick'> | ISeriesApi<'Bar'>).setData(
        points.map(p => ({ time: p.time, open: p.open, high: p.high, low: p.low, close: p.close }))
      );
    } else {
      (seriesRef.current as ISeriesApi<'Line'> | ISeriesApi<'Area'>).setData(
        points.map(p => ({ time: p.time, value: p.value }))
      );
    }
  }, [type, width, height]);

  return <div ref={containerRef} style={{ width, height }} />;
}
