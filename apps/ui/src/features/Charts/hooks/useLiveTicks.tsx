// hooks/useLiveTicks.ts
import { useEffect, useRef, useState } from 'react';
import { isMarketClosed } from '@/lib/marketHours';
import { WS_URL } from '@/lib/config';

interface Tick {
  symbol: string;
  token: string;
  ltp: number;
  timestamp: string;
}

const PING_TYPES = ['ping', 'heartbeat'];

export default function useLiveTicks(
  symbol: string,
  broker: string,
  useDummy = false
): Tick | null {
  const [tick, setTick] = useState<Tick | null>(null);

  const wsRef = useRef<WebSocket | null>(null);
  const aliveRef = useRef<boolean>(false);
  const reconnectTimer = useRef<number | null>(null);
  const heartbeatTimer = useRef<number | null>(null);

  useEffect(() => {
    // reset state whenever inputs change
    setTick(null);

    // guard rails
    if (!symbol || !broker) return;

    // dummy mode (forced when market closed, or caller asked)
    if (useDummy || isMarketClosed()) {
      let ltp = 100 + Math.random() * 50;
      const id = window.setInterval(() => {
        const change = (Math.random() - 0.5) * 2;
        ltp = Math.max(10, ltp + change);
        setTick({
          symbol,
          token: 'DUMMY',
          ltp: parseFloat(ltp.toFixed(2)),
          timestamp: new Date().toISOString(),
        });
      }, 1000);
      return () => window.clearInterval(id);
    }

    const url = `${WS_URL}?broker=${encodeURIComponent(broker)}`;
    let manuallyClosed = false;

    const cleanupTimers = () => {
      if (reconnectTimer.current) {
        window.clearTimeout(reconnectTimer.current);
        reconnectTimer.current = null;
      }
      if (heartbeatTimer.current) {
        window.clearTimeout(heartbeatTimer.current);
        heartbeatTimer.current = null;
      }
    };

    const scheduleReconnect = (delay = 1000) => {
      if (manuallyClosed) return;
      cleanupTimers();
      reconnectTimer.current = window.setTimeout(connect, delay);
    };

    const startHeartbeat = () => {
      // If no message in 20s, consider dead and reconnect
      if (heartbeatTimer.current) window.clearTimeout(heartbeatTimer.current);
      heartbeatTimer.current = window.setTimeout(() => {
        if (!aliveRef.current) {
          try { wsRef.current?.close(); } catch (_) {}
          scheduleReconnect(1000);
        } else {
          aliveRef.current = false; // expect next message to flip it back
          startHeartbeat();
        }
      }, 20000);
    };

    const connect = () => {
      try {
        const ws = new WebSocket(url);
        wsRef.current = ws;

        ws.addEventListener('open', () => {
          // one subscribe message; include broker + symbol so server can route
          const payload = { action: 'subscribe', broker, symbol };
          ws.send(JSON.stringify(payload));
          aliveRef.current = true;
          startHeartbeat();
        });

        ws.addEventListener('message', (event) => {
          // any message proves liveness
          aliveRef.current = true;

          let data: any;
          try { data = JSON.parse(event.data); } catch {
            // Sometimes servers send plain "ping"
            const raw = String(event.data || '').toLowerCase();
            if (PING_TYPES.includes(raw)) {
              // Best-effort pong
              try { ws.send('pong'); } catch {}
            }
            return;
          }

          // Heartbeat/ping forms
          const typ = (data.type || '').toLowerCase();
          if (PING_TYPES.includes(typ)) {
            try { ws.send(JSON.stringify({ type: 'pong' })); } catch {}
            return;
          }

          // Normalize tick payloads
          if (!data) return;
          const incomingSymbol = data.symbol ?? data.tradingsymbol;
          const price = Number(data.ltp ?? data.price ?? data.last_price);

          if (incomingSymbol === symbol && Number.isFinite(price)) {
            setTick({
              symbol: incomingSymbol,
              token: data.token ?? data.token_id ?? '',
              ltp: price,
              timestamp: data.timestamp ?? new Date().toISOString(),
            });
          }
        });

        ws.addEventListener('error', () => {
          // close will handle reconnection
          try { ws.close(); } catch {}
        });

        ws.addEventListener('close', () => {
          cleanupTimers();
          if (!manuallyClosed) scheduleReconnect(1500); // backoff
        });
      } catch {
        // if constructor throws, retry
        scheduleReconnect(1500);
      }
    };

    connect();

    return () => {
      // component unmount or deps change
      manuallyClosed = true;
      cleanupTimers();
      const ws = wsRef.current;
      wsRef.current = null;

      try {
        if (ws && ws.readyState === WebSocket.OPEN) {
          ws.send(JSON.stringify({ action: 'unsubscribe', broker, symbol }));
        }
      } catch {}
      try { ws?.close(); } catch {}
    };
  }, [symbol, broker, useDummy]);

  return tick;
}
