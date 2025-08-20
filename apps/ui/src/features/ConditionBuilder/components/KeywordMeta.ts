// src/features/ConditionBuilder/components/KeywordMeta.ts
export type ParamDef = {
  name: string;
  label: string;
  type: 'string' | 'number' | 'select';
  options?: { label: string; value: string }[];
};

export const KEYWORD_META: Record<string, { params: ParamDef[] }> = {
  // TODO: fill with real metadata per keyword
};
