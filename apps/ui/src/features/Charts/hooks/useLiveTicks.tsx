// hooks/useLiveTicks.tsx
useEffect(() => {
  if (!symbol || !broker) {
    setTick(null);
    return;
  }

  const url = `${WS_URL}?broker=${broker}`;
  setTick(null);

  if (useDummy || isMarketClosed()) {
    let ltp = 100 + Math.random() * 50;
    const interval = setInterval(() => {
      const change = (Math.random() - 0.5) * 2;
      ltp = Math.max(10, ltp + change);
      setTick({
        symbol,
        token: 'DUMMY',
        ltp: parseFloat(ltp.toFixed(2)),
        timestamp: new Date().toISOString(),
      });
    }, 1000);
    return () => clearInterval(interval);
  }

  let socket: WebSocket | null = null;

  try {
    socket = new WebSocket(url);
  } catch (e) {
    console.error("WS constructor failed", e);
    return;
  }

  socket.onopen = () => {
    socket?.send(JSON.stringify({ action: 'subscribe', symbol }));
  };

  socket.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data);
      if (data.symbol === symbol) setTick(data);
    } catch (err) {
      console.error('Invalid WS message', err);
    }
  };

  socket.onerror = (err) => console.error('WS error', err);
  socket.onclose = (e) => {
    // optional: reconnection strategy here
    // console.warn('WS closed', e.code, e.reason, e.wasClean);
  };

  return () => {
    if (socket && socket.readyState === WebSocket.OPEN) {
      socket.send(JSON.stringify({ action: 'unsubscribe', symbol }));
      socket.close();
    }
    socket = null;
  };
}, [symbol, broker, useDummy]);
