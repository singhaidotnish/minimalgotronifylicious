// apps/ui/src/features/ConditionBuilder/api/testStrategy.ts
import type { WireGroup } from '../models/wire';

const API_BASE = process.env.NEXT_PUBLIC_BACKEND_URL as string;

export async function testOnAngelOne(payload: WireGroup) {
  if (!API_BASE) throw new Error('NEXT_PUBLIC_BACKEND_URL is not set');
  const res = await fetch(`${API_BASE}/api/angel-one/test`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  const text = await res.text();
  if (!res.ok) throw new Error(text || `HTTP ${res.status}`);
  try {
    return JSON.parse(text);
  } catch {
    return { ok: true, raw: text };
  }
}
