// src/features/ConditionBuilder/components/RootGroupNode.tsx
'use client';

import React, { useState, useRef, useEffect } from 'react';
import { Handle, Position, useReactFlow } from 'reactflow';
import { GROUPS } from '@/features/ConditionBuilder/models/conditionGroups';
import ChooseBlock from './ChooseBlock';              // ⬅ no named type import
import { v4 as uuidv4 } from 'uuid';

// 👇 derive the canonical types from ChooseBlock props (so we never drift)
type ChooseBlockProps = Parameters<typeof ChooseBlock>[0];
type SelectedItem = NonNullable<ChooseBlockProps['selectedItems']>[number];

// export so RootGroupNodeBuilder can import it
export type ChooseBlockData = {
  id: string;
  inputValue: string;
  keyword: string;
  contextParams: Record<string, string>;
  selectedItems: SelectedItem[];
};

// layout knobs for the connector lines
const SPINE_LEFT = 'left-8';
const ROW_GUTTER = 'pl-24';
const STUB_WIDTH = 'w-14';

export default function RootGroupNode({ data }: any) {
  const [chooseBlocks, setChooseBlocks] = useState<ChooseBlockData[]>([
    { id: uuidv4(), inputValue: '', keyword: '', contextParams: {}, selectedItems: [] },
  ]);
  const [logic, setLogic] = useState<'AND' | 'OR'>('AND');

  const { setNodes } = useReactFlow();
  const nodeRef = useRef<HTMLDivElement>(null);
  const addLockRef = useRef(false);

  // keep RF node height in sync with content
  useEffect(() => {
    if (!nodeRef.current) return;
    const height = nodeRef.current.offsetHeight;
    setNodes((nds) =>
      nds.map((node) =>
        node.id === data.id ? { ...node, style: { ...node.style, height } } : node
      )
    );
  }, [chooseBlocks.length, data?.id, setNodes]);

  // guarded add handlers (prevent duplicate rows)
  const addCondition = (e?: React.MouseEvent) => {
    e?.preventDefault();
    e?.stopPropagation();
    if (addLockRef.current) return;
    addLockRef.current = true;

    setChooseBlocks((prev) => [
      ...prev,
      { id: uuidv4(), inputValue: '', keyword: '', contextParams: {}, selectedItems: [] },
    ]);

    queueMicrotask(() => { addLockRef.current = false; });
  };

  const addGroup = (e?: React.MouseEvent) => {
    // TODO: real nested group later; for now mirror addCondition
    addCondition(e);
  };

  return (
    <div
      ref={nodeRef}
      className="bg-gray-100 p-4 w-full"
      onClick={(e) => e.stopPropagation()}
    >
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
                e.preventDefault();
                e.stopPropagation();
                setChooseBlocks([{ id: uuidv4(), inputValue: '', keyword: '', contextParams: {}, selectedItems: [] }]);
              }}
              className="text-xs px-2 py-1 bg-red-200 rounded hover:bg-red-300"
            >
              ×
            </button>
          </div>
        </div>

        {/* spine anchored to rows only */}
        <div className="relative">
          <div className="relative">
            <div
              className={[
                'absolute', SPINE_LEFT, 'top-0', 'bottom-0', 'w-px', 'bg-gray-300', 'pointer-events-none',
              ].join(' ')}
              aria-hidden
            />
            <div className="flex flex-col gap-4">
              {chooseBlocks.map((block) => (
                <div key={block.id} className={['relative', ROW_GUTTER].join(' ')}>
                  <div
                    className={[
                      'absolute', SPINE_LEFT, 'top-1/2', '-translate-y-1/2',
                      STUB_WIDTH, 'h-px', 'bg-gray-400', 'pointer-events-none',
                    ].join(' ')}
                    aria-hidden
                  />
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
                    onSelectedItemsChange={(items: SelectedItem[]) =>
                      setChooseBlocks((prev) =>
                        prev.map((b) =>
                          b.id === block.id ? { ...b, selectedItems: items } : b
                        )
                      )
                    }
                    onSelectOption={(opt) => console.log('Selected:', opt)}
                  />
                </div>
              ))}
            </div>
          </div>
        </div>

        <div className="pt-4 flex justify-center">
          <button
            type="button"
            onMouseDown={(e) => e.preventDefault()}
            onClick={(e) => { e.preventDefault(); e.stopPropagation(); console.log('Submit pressed'); }}
            className="bg-blue-600 text-white px-6 py-2 rounded shadow hover:bg-blue-700"
          >
            Submit
          </button>
        </div>

        <Handle type="source" position={Position.Bottom} />
        <Handle type="target" position={Position.Top} />
      </div>
    </div>
  );
}
