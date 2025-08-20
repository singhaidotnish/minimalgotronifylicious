// components/ChartPanel.tsx
'use client';
import React, { useState, useRef, useEffect } from 'react';

import FallbackChart from './FallbackChart';
import { AdvancedChart } from 'react-tradingview-embed';
import { isMarketOpen } from '@/lib/marketHours';

// was: export type SeriesType = 'Line' | 'Area' | 'Candlestick' | 'Bar';
type ChartSeriesType = 'Line' | 'Area' | 'Candlestick' | 'Bar';

// apps/ui/src/features/Charts/components/ChartPanel.tsx

// 1) ensure styleMap returns strings
const styleMap: Record<ChartSeriesType, `${number}`> = {
  Line: '2',
  Area: '3',
  Candlestick: '1',
  Bar: '0',
} as const;

interface ChartPanelProps {
  symbol: string;
  seriesType: ChartSeriesType;
  height?: number;
}

// (if you have a SeriesType union, this keeps types tight)
type SeriesType = keyof typeof styleMap;


const chartOptions: SeriesType[] = ['Line', 'Area', 'Candlestick', 'Bar'];

export default function ChartPanel({ symbol, height = 400 }: ChartPanelProps) {
  const [seriesType, setSeriesType] = useState<SeriesType>('Line');
  const marketOpen = isMarketOpen();
  const containerRef = useRef<HTMLDivElement>(null);
  const [w, setW] = React.useState<number | null>(null);
  // measure container safely
  useEffect(() => {
    if (!containerRef.current) return;
    const ro = new ResizeObserver(([entry]) => {
      setW(Math.floor(entry.contentRect.width));
    });
    ro.observe(containerRef.current);
    return () => ro.disconnect();
  }, []);


  return (
    <div ref={containerRef} style={{ height }}>
      <div className="mb-2 flex items-center gap-2">
        <label className="font-medium">Chart Type:</label>
        <select
          value={seriesType}
          onChange={e => setSeriesType(e.target.value as SeriesType)}
          className="border rounded px-2 py-1"
        >
          {chartOptions.map(opt => (
            <option key={opt} value={opt}>
              {opt}
            </option>
          ))}
        </select>
      </div>

      {marketOpen ? (
        <AdvancedChart widgetProps={{ symbol, interval: "1", theme: "dark", style: styleMap[seriesType], locale: "en", autosize: true }} />
      ) : w != null ? (
        <FallbackChart type={seriesType} width={w} height={height} />
      ) : (
        <div className="h-full w-full">Loading…</div>
      )}

    </div>
  );
}
