// src/features/ConditionBuilder/components/ParamInput.tsx
import React from 'react';
import type { BaseParam, Option } from '../types';
import { useParamOptions } from '../hooks/useParamOptions';

export function ParamInput({
  param,
  value,
  onChange,
}: {
  param: BaseParam;
  value: any;
  onChange: (v: any) => void;
}) {
  // async sources
  const seriesHook = param.type === 'series' ? useParamOptions('series') : null;
  const underlyingHook = param.type === 'underlying' ? useParamOptions('underlying') : null;

  if (param.type === 'number') {
    return (
      <input
        type="number"
        className="w-full border px-2 py-1 rounded"
        placeholder={param.placeholder}
        value={value ?? ''}
        min={param.min} max={param.max} step={param.step ?? 1}
        onChange={(e) => onChange(e.target.value === '' ? undefined : Number(e.target.value))}
      />
    );
  }

  const buildSelect = (opts: Option[], disabled = false) => (
    <select
      className="w-full border px-2 py-1 rounded"
      value={value ?? ''}
      onChange={(e) => onChange(e.target.value)}
      disabled={disabled}
    >
      <option value="">{param.placeholder ?? `Select ${param.label ?? param.name}`}</option>
      {opts.map(o => <option key={o.value} value={o.value}>{o.label}</option>)}
    </select>
  );

  if (param.type === 'series') {
    const { options, loading } = seriesHook!;
    return buildSelect(options, loading);
  }

  if (param.type === 'underlying') {
    const { options, loading } = underlyingHook!;
    return buildSelect(options, loading);
  }

  if (param.type === 'priceSource') {
    const opts: Option[] = ['OPEN','HIGH','LOW','CLOSE'].map(v => ({ label: v, value: v }));
    return buildSelect(opts);
  }

  // generic select
  if (param.type === 'select') {
    const opts = typeof param.options === 'function' ? [] : (param.options ?? []);
    return buildSelect(opts);
  }

  return null;
}
