// src/features/ConditionBuilder/components/ConditionBuilder.tsx
'use client';

import React from 'react';
import type { ConditionGroup } from '@/features/ConditionBuilder/types';
import ConditionCard from './ConditionCard';

export type ConditionBuilderProps = {
  /** preferred */
  group?: ConditionGroup;
  /** legacy alias */
  node?: ConditionGroup;
  onChange: React.Dispatch<React.SetStateAction<ConditionGroup>>;
};

export default function ConditionBuilder(props: ConditionBuilderProps) {
  const { onChange } = props;
  const group = props.group ?? props.node;
  if (!group) {
    if (process.env.NODE_ENV !== 'production') {
      throw new Error('ConditionBuilder: pass `group` (preferred) or `node`');
    }
    return null;
  }

  // EXAMPLE RENDER: map children into presentational cards
  return (
    <div className="space-y-2">
      {group.conditions.map((child, idx) => (
        <ConditionCard
          key={child.id ?? idx}
          id={child.id ?? String(idx)}
          onDelete={() => {
            onChange(cur => ({
              ...cur,
              conditions: cur.conditions.filter((_, i) => i !== idx),
            }));
          }}
        />
      ))}

      <button
        className="bg-blue-600 text-white text-xs px-3 py-1 rounded hover:bg-blue-700"
        onClick={() =>
          onChange(cur => ({
            ...cur,
            conditions: [
              ...cur.conditions,
              { id: crypto.randomUUID(), type: 'condition' } as any, // stub leaf
            ],
          }))
        }
      >
        + Add Condition
      </button>
    </div>
  );
}
