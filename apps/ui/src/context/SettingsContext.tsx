// src/features/Settings/SettingsContext.tsx
'use client';

import React, {
  createContext,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from 'react';
import { isMarketOpen, nextMarketBoundary } from '@/lib/marketHours';

export type Broker = 'angel_one' | 'zerodha';

export interface SettingsContextValue {
  /** Whether to use dummy tick data instead of live */
  useDummyTicks: boolean;
  /** Flip between live and dummy ticks */
  setUseDummyTicks: React.Dispatch<React.SetStateAction<boolean>>;
  /** Selected broker identifier */
  broker: Broker;
  /** Update broker */
  setBroker: React.Dispatch<React.SetStateAction<Broker>>;
}

export const SettingsContext = createContext<SettingsContextValue | undefined>(undefined);

export const SettingsProvider = ({ children }: { children: ReactNode }) => {
  const [broker, setBroker] = useState<Broker>('angel_one');

  // SSR-safe default; sync after mount
  const [useDummyTicks, setUseDummyTicks] = useState<boolean>(false);

  useEffect(() => {
    // Initial sync
    setUseDummyTicks(!isMarketOpen());

    let timer: number | undefined;

    const scheduleNextBoundary = () => {
      const next = nextMarketBoundary(new Date(), 'Asia/Kolkata');
      const delay = Math.max(0, next.getTime() - Date.now());

      timer = window.setTimeout(() => {
        setUseDummyTicks(!isMarketOpen()); // flip exactly at open/close
        scheduleNextBoundary();            // schedule following flip
      }, delay);
    };

    scheduleNextBoundary();

    // Resync when tab wakes up
    const onVis = () => {
      if (document.visibilityState === 'visible') {
        setUseDummyTicks(!isMarketOpen());
      }
    };
    document.addEventListener('visibilitychange', onVis);

    return () => {
      if (timer) clearTimeout(timer);
      document.removeEventListener('visibilitychange', onVis);
    };
  }, []);

  // Memoize to prevent unnecessary consumer re-renders
  const value: SettingsContextValue = useMemo(
    () => ({ useDummyTicks, setUseDummyTicks, broker, setBroker }),
    [useDummyTicks, broker] // setters are stable
  );

  return <SettingsContext.Provider value={value}>{children}</SettingsContext.Provider>;
};

export const useSettings = (): SettingsContextValue => {
  const ctx = useContext(SettingsContext);
  if (!ctx) throw new Error('useSettings must be used within a SettingsProvider');
  return ctx;
};
