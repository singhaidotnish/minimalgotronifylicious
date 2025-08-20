// src/features/ConditionBuilder/components/ContextUI.tsx

'use client';
import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { GROUPS } from '../models/conditionGroups';
import { PARAM_OPTIONS } from '../config/paramOptions';

/** Contract stays the same */
export interface ContextUIProps {
  keyword: string;
  params: Record<string, string>;
  onParamChange: (key: string, value: string) => void;
  onConfirm: () => void;  // zero-arg
  onCancel: () => void;
}

/** (Optional helper used in some screens) — merge both lists once */
function SeriesDropdown({
  value,
  onChange,
}: {
  value: string;
  onChange: (v: string) => void;
}) {
  const [seriesOptions, setSeriesOptions] = useState<string[]>([]);

  useEffect(() => {
    let mounted = true;
    (async () => {
      try {
        const [series, underlying] = await Promise.all([
          axios.get('/api/param-options?type=series'),
          axios.get('/api/param-options?type=underlying'),
        ]);
        if (!mounted) return;
        const merged = Array.from(new Set([...(series.data ?? []), ...(underlying.data ?? [])]));
        setSeriesOptions(merged);
      } catch (err) {
        console.error('Failed to fetch series/underlying options', err);
      }
    })();
    return () => {
      mounted = false;
    };
  }, []);

  return (
    <select
      value={value}
      onChange={(e) => onChange(e.target.value)}
      className="border p-1 rounded"
    >
      {seriesOptions.map((opt) => (
        <option key={opt} value={opt}>
          {opt}
        </option>
      ))}
    </select>
  );
}

function getOptionMeta(keyword: string) {
  for (const group of GROUPS) {
    for (const opt of group.options) {
      if (opt.key === keyword) return opt;
    }
  }
  return null;
}

// src/features/ConditionBuilder/components/ContextUI.tsx
// ...keep the existing imports and component signature

export default function ContextUI({
  keyword,
  params,
  onParamChange,
  onConfirm,
  onCancel,
}: ContextUIProps) {
  const option = getOptionMeta(keyword);
  const [localParams, setLocalParams] = useState<Record<string, string>>(params);
  const confirmLockRef = useRef(false);

  useEffect(() => setLocalParams(params), [params]);
  if (!option) return null;

  // ✅ simple validity: every declared param must be non-empty
  const isValid = option.params.every(p => (localParams[p.name] ?? '').toString().trim() !== '');

  const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    e.stopPropagation();
    if (confirmLockRef.current || !isValid) return;
    confirmLockRef.current = true;
    onConfirm();
    requestAnimationFrame(() => { confirmLockRef.current = false; });
  };

  const handleChange = (key: string, value: string) => {
    setLocalParams(prev => ({ ...prev, [key]: value }));
    onParamChange(key, value);
  };

  // helper: number-ish inputs (period/window/length)
  const isNumberParam = (name: string, type?: string) =>
    type === 'number' || /period|window|length|count|size/i.test(name);

  return (
    <div className="fixed inset-0 bg-black/20 backdrop-blur-sm flex items-center justify-center z-50"
         onClick={(e) => { if (e.target === e.currentTarget) onCancel(); }}>
      <form onSubmit={handleSubmit}
            className="bg-white p-6 rounded-lg shadow-xl w-full max-w-md"
            onClick={(e) => e.stopPropagation()}>
        <h4 className="text-lg font-semibold mb-4">Configure: {option.label}</h4>

        <div className="space-y-3">
          {option.params.map((p, idx) => {
            const val = localParams[p.name] ?? '';
            const numberField = isNumberParam(p.name, (p as any).type);
            return (
              <div key={`${p.name}-${idx}`} className="flex flex-col gap-1">
                <label className="text-xs text-gray-600 capitalize">{p.name}</label>
                {PARAM_OPTIONS[(p as any).type] ? (
                  <select
                    className="border px-2 py-1 rounded w-full text-sm"
                    value={val}
                    onChange={(e) => handleChange(p.name, e.target.value)}
                    // autofocus the first empty field for ADHD-friendly flow
                    autoFocus={!val && idx === 0}
                  >
                    <option value="">Select {p.name}</option>
                    {PARAM_OPTIONS[(p as any).type].map((opt: string) => (
                      <option key={opt} value={opt}>{opt}</option>
                    ))}
                  </select>
                ) : (
                  <input
                    className="border px-2 py-1 rounded w-full text-sm"
                    value={val}
                    onChange={(e) => handleChange(p.name, e.target.value)}
                    placeholder={`Enter ${p.name}`}
                    inputMode={numberField ? 'numeric' : undefined}
                    type={numberField ? 'number' : 'text'}
                    min={numberField ? 1 : undefined}
                    autoFocus={!val && idx === 0}
                  />
                )}
              </div>
            );
          })}
        </div>

        <div className="pt-6 flex justify-end gap-3">
          <button type="button"
                  onClick={(e) => { e.preventDefault(); e.stopPropagation(); onCancel(); }}
                  className="border border-gray-300 bg-white px-4 py-1 rounded shadow-sm text-sm hover:bg-gray-100">
            Cancel
          </button>
          <button type="submit"
                  onMouseDown={(e) => e.preventDefault()}
                  disabled={!isValid}
                  className={`px-4 py-1 rounded shadow-sm text-sm text-white ${
                    isValid ? 'bg-blue-600 hover:bg-blue-700' : 'bg-blue-300 cursor-not-allowed'
                  }`}>
            OK
          </button>
        </div>
      </form>
    </div>
  );
}
