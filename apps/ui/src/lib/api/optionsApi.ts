// apps/ui/src/lib/api/optionsApi.ts
const BASE = process.env.NEXT_PUBLIC_API_BASE || ''; // '' = same origin

export type Side = 'CE' | 'PE';
export type ExpirySel = 'current_week' | 'next_week' | 'monthly' | 'custom';
export type StrikeSel = 'ATM' | 'OTM+steps' | 'ITM+steps' | 'ByStrike';

export type ChainRow = {
  tradingsymbol: string;
  exchange: string;
  strike: number;
  side: Side;
  expiry: string;     // YYYY-MM-DD
  ltp: number;
  iv?: number;
  oi?: number;
  bid?: number;
  ask?: number;
};

export type ChainResp = {
  underlying: string;
  expiry: string;
  rows: ChainRow[];
};

export async function fetchChain(underlying: string, expirySel: ExpirySel, expiry?: string): Promise<ChainResp> {
  const qs = new URLSearchParams({ underlying, expirySel });
  if (expiry) qs.set('expiry', expiry);
  const r = await fetch(`${BASE}/api/options/chain?${qs.toString()}`);
  if (!r.ok) throw new Error(`chain ${r.status}`);
  return r.json();
}

export type ResolveReq = {
  underlying: string;
  side: Side;
  strikeSel: StrikeSel;
  steps?: number;
  strike?: number;
  expirySel: ExpirySel;
  expiry?: string; // YYYY-MM-DD when custom
};

export type ResolveResp = { tradingsymbol: string; exchange: string };

export async function resolveOption(body: ResolveReq): Promise<ResolveResp> {
  const r = await fetch(`${BASE}/api/options/resolve`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
  if (!r.ok) throw new Error(`resolve ${r.status}`);
  return r.json();
}

export type ValueField = 'ltp' | 'iv' | 'oi';
export type ValueResp = { symbol: string; field: ValueField; value: number; ts: number };

export async function fetchOptionValue(symbol: string, field: ValueField): Promise<ValueResp> {
  const qs = new URLSearchParams({ symbol, field });
  const r = await fetch(`${BASE}/api/options/value?${qs.toString()}`);
  if (!r.ok) throw new Error(`value ${r.status}`);
  return r.json();
}

export type GreeksResp = { symbol: string; delta: number; gamma: number; theta: number; vega: number; ts: number };

export async function fetchGreeks(symbol: string): Promise<GreeksResp> {
  const qs = new URLSearchParams({ symbol });
  const r = await fetch(`${BASE}/api/options/greeks?${qs.toString()}`);
  if (!r.ok) throw new Error(`greeks ${r.status}`);
  return r.json();
}
