// src/features/ConditionBuilder/components/types.ts
export type ParamType =
  | 'number'
  | 'select'
  | 'series'       // async dropdown from API
  | 'underlying'   // async dropdown from API
  | 'priceSource'; // OPEN/HIGH/LOW/CLOSE (local enum)

export type Option = { label: string; value: string };

export interface BaseParam {
  name: string;
  label?: string;
  type: ParamType;
  required?: boolean;
  // for select-like params
  options?: Option[] | (() => Promise<Option[]>); // can be async
  placeholder?: string;
  min?: number;
  max?: number;
  step?: number;
}

export interface IndicatorDef {
  key: string;
  label: string;
  group: 'Technical' | 'Candle' | 'Statistics' | 'Math'; // future filtering
  params: BaseParam[];
  preview: (p: Record<string, unknown>) => string; // produces chip text
}

export type ConditionItem = {
  id: string;
  keyword: string;
  label: string;
  params: Record<string, any>;
};
