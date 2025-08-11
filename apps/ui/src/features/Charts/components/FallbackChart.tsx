// components/FallbackChart.tsx
'use client';

import React, { useRef, useEffect } from 'react';
import {
  createChart,
  IChartApi,
  UTCTimestamp,
  CrosshairMode,
  LineStyle,
  // ✅ import only option types if you need them (optional)
  AreaSeriesPartialOptions,
  BarSeriesPartialOptions,
  CandlestickSeriesPartialOptions,
  LineSeriesPartialOptions,
} from 'lightweight-charts';

interface FallbackChartProps {
  type: 'Line' | 'Area' | 'Candlestick' | 'Bar';
  width: number;
  height: number;
}

export default function FallbackChart({ type, width, height }: FallbackChartProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const chartRef = useRef<IChartApi | null>(null);
  const seriesRef = useRef<ReturnType<IChartApi['addLineSeries']> |
                           ReturnType<IChartApi['addAreaSeries']> |
                           ReturnType<IChartApi['addCandlestickSeries']> |
                           ReturnType<IChartApi['addBarSeries']> | null>(null);

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

    // initial series
    const makeSeries = () => {
      if (!chartRef.current) return;
      switch (type) {
        case 'Candlestick':
          seriesRef.current = chartRef.current.addCandlestickSeries({});
          break;
        case 'Bar':
          seriesRef.current = chartRef.current.addBarSeries({});
          break;
        case 'Area':
          seriesRef.current = chartRef.current.addAreaSeries({
            topColor: 'rgba(33, 150, 243, 0.56)',
            bottomColor: 'rgba(33, 150, 243, 0.04)',
          });
          break;
        case 'Line':
        default:
          seriesRef.current = chartRef.current.addLineSeries({ lineStyle: LineStyle.Solid });
      }
    };

    makeSeries();

    return () => {
      chart.remove();
      chartRef.current = null;
      seriesRef.current = null;
    };
  }, []); // init once

  useEffect(() => {
    if (!chartRef.current) return;
    chartRef.current.applyOptions({ width, height });

    // rebuild series when type changes
    if (seriesRef.current) {
      chartRef.current.removeSeries(seriesRef.current);
      seriesRef.current = null;
    }

    switch (type) {
      case 'Candlestick':
        seriesRef.current = chartRef.current.addCandlestickSeries({});
        break;
      case 'Bar':
        seriesRef.current = chartRef.current.addBarSeries({});
        break;
      case 'Area':
        seriesRef.current = chartRef.current.addAreaSeries({
          topColor: 'rgba(33, 150, 243, 0.56)',
          bottomColor: 'rgba(33, 150, 243, 0.04)',
        });
        break;
      case 'Line':
      default:
        seriesRef.current = chartRef.current.addLineSeries({ lineStyle: LineStyle.Solid });
    }

    // dummy data
    const now = Date.now();
    const points = Array.from({ length: 120 }).map((_, i) => {
      const t = (now - (120 - i) * 60_000) / 1000 as UTCTimestamp; // 1‑min steps
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
      // @ts-expect-error type narrowed at runtime
      seriesRef.current.setData(points.map(p => ({
        time: p.time,
        open: p.open,
        high: p.high,
        low: p.low,
        close: p.close,
      })));
    } else {
      // @ts-expect-error type narrowed at runtime
      seriesRef.current.setData(points.map(p => ({ time: p.time, value: p.value })));
    }
  }, [type, width, height]);

  return <div ref={containerRef} style={{ width, height }} />;
}
