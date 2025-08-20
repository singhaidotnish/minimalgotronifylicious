// src/features/ConditionBuilder/types.ts
export type LogicOp = 'AND' | 'OR';

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


/**
 * A single leaf/atomic condition (non-group).
 * Extend this with whatever your evaluateCondition() needs
 * (e.g., keyword, params, operator, thresholds, etc.)
 */
export type ConditionLeaf = {
  type: 'condition';      // discriminant
  id: string;
  symbol?: string;
  keyword?: string;
  params?: Record<string, string>;
  // add fields you actually evaluate:
  // comparator?: '>' | '>=' | '<' | '<=' | '==' | '!=';
  // leftKey?: string;
  // rightValue?: number;
};

/** A group of conditions combined with AND/OR */
export type ConditionGroup = {
  type: 'group';          // discriminant
  id: string;
  logic: LogicOp;         // 'AND' | 'OR'
  conditions: ConditionNode[];
};

/** Discriminated union used everywhere */
export type ConditionNode = ConditionGroup | ConditionLeaf;
