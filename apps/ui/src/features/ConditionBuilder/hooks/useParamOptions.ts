// src/features/ConditionBuilder/hooks/useParamOptions.ts
import { useEffect, useState } from 'react';
import axios from 'axios';
import type { Option } from '../types';

const cache = new Map<string, Option[]>();

export function useParamOptions(type: 'series' | 'underlying') {
  const [opts, setOpts] = useState<Option[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    let on = true;
    const run = async () => {
      if (cache.has(type)) { setOpts(cache.get(type)!); return; }
      setLoading(true);
      try {
        const { data } = await axios.get(`/api/param-options?type=${type}`);
        const mapped: Option[] = data.map((v: string) => ({ label: v, value: v }));
        cache.set(type, mapped);
        if (on) setOpts(mapped);
      } finally { if (on) setLoading(false); }
    };
    run();
    return () => { on = false; };
  }, [type]);

  return { options: opts, loading };
}
