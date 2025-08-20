// src/features/ConditionBuilder/components/StrategyBuilderPanel.tsx
'use client';

import React, { useEffect, useState } from 'react';
import ConditionBuilder from './ConditionBuilder';
import type { ConditionGroup, ConditionNode } from '@/features/ConditionBuilder/types';
import LivePriceSubscriber from '@/features/DataPanels/components/LivePriceSubscriber';

// ---------- symbol helpers (type-safe for string OR {symbol, token}) ----------
type SymbolObj = { symbol: string; token?: string };

function isSymbolObj(x: unknown): x is SymbolObj {
  return !!x && typeof x === 'object' && 'symbol' in (x as any);
}

function extractSymbol(s: unknown): string | undefined {
  if (typeof s === 'string') return s;
  if (isSymbolObj(s) && typeof s.symbol === 'string') return s.symbol;
  return undefined;
}

function collectSymbols(node: ConditionNode): string[] {
  if (node.type === 'group') {
    return node.conditions.flatMap(collectSymbols);
  }
  const sym = extractSymbol((node as any).symbol);
  return sym ? [sym] : [];
}

// ---------- evaluation (adapt to your real fields as needed) ----------
function evaluateCondition(cond: any, livePrices: Record<string, number>) {
  const sym = extractSymbol(cond.symbol);
  if (!sym) return false;

  const ltp = livePrices[sym];
  if (ltp === undefined) return false;

  switch (cond.operator) {
    case '>':  return ltp >  cond.value;
    case '<':  return ltp <  cond.value;
    case '>=': return ltp >= cond.value;
    case '<=': return ltp <= cond.value;
    case '==': return ltp === cond.value;
    case '!=': return ltp !== cond.value;
    default:   return false;
  }
}

export function evaluateGroup(group: ConditionGroup, livePrices: Record<string, number>): boolean {
  if (group.logic === 'AND') {
    return group.conditions.every((cond: ConditionNode) =>
      cond.type === 'group' ? evaluateGroup(cond, livePrices) : evaluateCondition(cond, livePrices)
    );
  }
  // OR
  return group.conditions.some((cond: ConditionNode) =>
    cond.type === 'group' ? evaluateGroup(cond, livePrices) : evaluateCondition(cond, livePrices)
  );
}

export interface StrategyBuilderPanelProps {
  minRules?: number;
}

export default function StrategyBuilderPanel({ minRules = 1 }: StrategyBuilderPanelProps) {
  const [rootGroup, setRootGroup] = useState<ConditionGroup>({
    id: 'root',            // required by your ConditionGroup type
    type: 'group',
    logic: 'AND',
    conditions: [],
  });

  const [livePrices, setLivePrices] = useState<Record<string, number>>({});
  const [symbols, setSymbols] = useState<string[]>([]);

  // keep symbols list in sync with the tree
  useEffect(() => {
    setSymbols(Array.from(new Set(collectSymbols(rootGroup))));
  }, [rootGroup]);

  const subscribers = symbols.map((symbol) => (
    <LivePriceSubscriber
      key={symbol}
      symbol={symbol}
      onUpdate={(sym: string, ltp: number) =>
        setLivePrices((prev) => ({ ...prev, [sym]: ltp }))
      }
    />
  ));

  const allMet =
    rootGroup.conditions.length >= minRules &&
    evaluateGroup(rootGroup, livePrices);

  return (
    <div className="space-y-4">
      {/* ✅ ConditionBuilder expects `group` */}
      <ConditionBuilder group={rootGroup} onChange={setRootGroup} />
      {subscribers}
      <div className="mt-4">
        <span className="text-sm font-medium">Result: </span>
        <span className={allMet ? 'text-green-600' : 'text-red-600'}>
          {allMet ? 'All conditions met' : 'Not met'}
        </span>
      </div>
    </div>
  );
}
