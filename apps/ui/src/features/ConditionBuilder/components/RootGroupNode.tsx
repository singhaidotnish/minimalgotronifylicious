// src/features/ConditionBuilder/components/RootGroupNode.tsx
'use client';

import React, { useState, useRef, useEffect } from 'react';
import { Handle, Position, useReactFlow } from 'reactflow';
import { GROUPS } from '@/features/ConditionBuilder/models/conditionGroups';
import ChooseBlock from './ChooseBlock';
import { v4 as uuidv4 } from 'uuid';

import { toWireGroup } from '@/features/ConditionBuilder/models/wire';
import { testOnAngelOne } from '@/features/ConditionBuilder/api/testStrategy';

// derive canonical types from ChooseBlock so we never drift
type ChooseBlockProps = Parameters<typeof ChooseBlock>[0];
type SelectedItem = NonNullable<ChooseBlockProps['selectedItems']>[number];

export type ChooseBlockData = {
  id: string;
  inputValue: string;
  keyword: string;
  contextParams: Record<string, string>;
  selectedItems: SelectedItem[];
};

// keep blocks where they are
const PAD_PX = 280;               // pl-24 = 96px (don’t change unless you change the class)
const DESIRED_GAP_PX = 18;        // ↓ smaller => spine closer to blocks (6–12 is nice)
// put the spine just to the LEFT of the blocks by 'DESIRED_GAP_PX'
const SPINE_ABS_LEFT_PX = PAD_PX - DESIRED_GAP_PX;

// compute a stub that always connects spine ↔︎ block edge
const MIN_STUB = 40;                                  // tiny but visible
const STUB_LEFT = Math.min(PAD_PX, SPINE_ABS_LEFT_PX);
const STUB_WIDTH = Math.max(MIN_STUB, Math.abs(PAD_PX - SPINE_ABS_LEFT_PX));

export default function RootGroupNode({ data }: any) {
  const [chooseBlocks, setChooseBlocks] = useState<ChooseBlockData[]>([
    { id: uuidv4(), inputValue: '', keyword: '', contextParams: {}, selectedItems: [] },
  ]);
  const [logic, setLogic] = useState<'AND' | 'OR'>('AND');

  const { setNodes } = useReactFlow();
  const nodeRef = useRef<HTMLDivElement>(null);
  const addLockRef = useRef(false);

  // keep RF node height in sync
  useEffect(() => {
    if (!nodeRef.current) return;
    const height = nodeRef.current.offsetHeight;
    setNodes((nds) =>
      nds.map((node) =>
        node.id === data.id ? { ...node, style: { ...node.style, height } } : node
      )
    );
  }, [chooseBlocks.length, data?.id, setNodes]);

  const addCondition = (e?: React.MouseEvent) => {
    e?.preventDefault(); e?.stopPropagation();
    if (addLockRef.current) return;
    addLockRef.current = true;

    setChooseBlocks((prev) => [
      ...prev,
      { id: uuidv4(), inputValue: '', keyword: '', contextParams: {}, selectedItems: [] },
    ]);

    queueMicrotask(() => { addLockRef.current = false; });
  };

  const addGroup = (e?: React.MouseEvent) => { addCondition(e); };

  // expose CSS vars so spine + stubs move together without moving blocks
  const cssVars = {
    // where the vertical line sits (inside the padding)
    // @ts-expect-error css var ok
    '--cb-pad': `${PAD_PX}px`,
    // @ts-expect-error css var ok
    '--cb-gap': `${DESIRED_GAP_PX}px`,
    // @ts-expect-error css var ok
    '--cb-spine-left': `calc(var(--cb-pad) - var(--cb-gap))`,
  } as React.CSSProperties;

  //handle submit
  const [submitting, setSubmitting] = React.useState(false);
  const [lastResult, setLastResult] = React.useState<null | { ok: boolean; [k: string]: any }>(null);

  async function handleSubmit() {
    try {
      setSubmitting(true);
      setLastResult(null);

      const wire = toWireGroup(chooseBlocks, logic);
      const result = await testOnAngelOne(wire);
      setLastResult(result);
      console.log('AngelOne test result:', result);
    } catch (err: any) {
      console.error(err);
      setLastResult({ ok: false, error: err?.message || String(err) });
    } finally {
      setSubmitting(false);
    }
  }


  return (
    <div
      ref={nodeRef}
      className="cb-sanitize bg-gray-100 p-4 w-full"
      onClick={(e) => e.stopPropagation()}
      style={cssVars}
    >
      {/* scoped CSS to kill stray tab indicators that draw the long blue bar */}
      <style jsx global>{`
        .cb-sanitize .tabs::after,
        .cb-sanitize [role="tablist"]::after,
        .cb-sanitize .tab.tab-active::before,
        .cb-sanitize .tab::before,
        .cb-sanitize .MuiTabs-indicator {
          display: none !important;
        }
      `}</style>

      <div className="border rounded bg-gray-100 shadow p-4 w-full">
        {/* AND/OR + buttons */}
        <div className="relative flex items-center gap-2 mb-3">
          <div className="ml-4 inline-flex border rounded overflow-hidden text-xs bg-white shadow relative z-10">
            <button
              type="button"
              className={`px-2 py-1 ${logic === 'AND' ? 'bg-blue-500 text-white' : 'bg-white text-gray-700'}`}
              onClick={(e) => { e.preventDefault(); e.stopPropagation(); setLogic('AND'); }}
            >
              AND
            </button>
            <button
              type="button"
              className={`px-2 py-1 ${logic === 'OR' ? 'bg-blue-500 text-white' : 'bg-white text-gray-700'}`}
              onClick={(e) => { e.preventDefault(); e.stopPropagation(); setLogic('OR'); }}
            >
              OR
            </button>
          </div>

          <div className="ml-auto flex gap-2">
            <button
              type="button"
              onMouseDown={(e) => e.preventDefault()}
              onClick={addCondition}
              className="text-xs px-2 py-1 bg-green-200 rounded hover:bg-green-300"
            >
              + Condition
            </button>
            <button
              type="button"
              onMouseDown={(e) => e.preventDefault()}
              onClick={addGroup}
              className="text-xs px-2 py-1 bg-blue-200 rounded hover:bg-blue-300"
            >
              + Group
            </button>
            <button
              type="button"
              onMouseDown={(e) => e.preventDefault()}
              onClick={(e) => {
                e.preventDefault(); e.stopPropagation();
                setChooseBlocks([{ id: uuidv4(), inputValue: '', keyword: '', contextParams: {}, selectedItems: [] }]);
              }}
              className="text-xs px-2 py-1 bg-red-200 rounded hover:bg-red-300"
            >
              ×
            </button>
          </div>
        </div>

        <div className="relative">
          <div className="relative pl-24">{/* ← blocks stay put */}
            {/* vertical spine (absolute, independent of padding) */}
            <div
              className="absolute top-0 bottom-0 w-px bg-gray-300 pointer-events-none"
              style={{ left: SPINE_ABS_LEFT_PX }}
              aria-hidden
            />

            <div className="flex flex-col gap-6">
              {chooseBlocks.map((block) => (
                <div key={block.id} className="relative">
                  {/* horizontal stub from spine into the row */}
                  <div
                    className="absolute top-1/2 -translate-y-1/2 border-t border-gray-400 pointer-events-none"
                    style={{ left: STUB_LEFT, width: STUB_WIDTH }}
                    aria-hidden
                  />
                  {/* your row */}
                  <ChooseBlock
                    inputValue={block.inputValue}
                    onChange={(val) =>
                      setChooseBlocks((prev) =>
                        prev.map((b) => (b.id === block.id ? { ...b, inputValue: val } : b))
                      )
                    }
                    onDelete={() =>
                      setChooseBlocks((prev) => prev.filter((b) => b.id !== block.id))
                    }
                    groups={GROUPS}
                    selectedKeyword={block.keyword}
                    onKeywordChange={(val) =>
                      setChooseBlocks((prev) =>
                        prev.map((b) => (b.id === block.id ? { ...b, keyword: val } : b))
                      )
                    }
                    contextParams={block.contextParams}
                    onContextParamsChange={(params) =>
                      setChooseBlocks((prev) =>
                        prev.map((b) => (b.id === block.id ? { ...b, contextParams: params } : b))
                      )
                    }
                    selectedItems={block.selectedItems}
                    onSelectedItemsChange={(items) =>
                      setChooseBlocks((prev) =>
                        prev.map((b) => (b.id === block.id ? { ...b, selectedItems: items } : b))
                      )
                    }
                    onSelectOption={(opt) => console.log('Selected:', opt)}
                  />
                </div>
              ))}
            </div>
          </div>
        </div>

        <div className="pt-6 flex flex-col items-center gap-3">
          <button
            type="button"
            onMouseDown={(e) => e.preventDefault()}
            onClick={(e) => { e.preventDefault(); e.stopPropagation(); handleSubmit(); }}
            className="bg-blue-600 text-white px-6 py-2 rounded shadow hover:bg-blue-700 disabled:opacity-60"
            disabled={submitting}
          >
            {submitting ? 'Testing…' : 'Submit (Test on Angel One)'}
          </button>

          {/* quick feedback block */}
          {lastResult && (
            <pre className="max-w-full whitespace-pre-wrap text-xs bg-slate-50 border rounded p-3">
              {JSON.stringify(lastResult, null, 2)}
            </pre>
          )}
        </div>

        <Handle type="source" position={Position.Bottom} />
        <Handle type="target" position={Position.Top} />
      </div>
    </div>
  );
}
