// src/features/ConditionBuilder/components/RootGroupNode.tsx
'use client';

import React, { useState, useRef, useEffect } from 'react';
import { Handle, Position, useReactFlow } from 'reactflow';
import { GROUPS } from '@/features/ConditionBuilder/models/conditionGroups';
import ChooseBlock from '@/features/ConditionBuilder/components/ChooseBlock';
import { v4 as uuidv4 } from 'uuid';

// Keep SelectedItem shape compatible with ChooseBlock
type SelectedItem = {
  id: string;
  keyword: string;
  label: string;
  params?: Record<string, string>;
};

type ChooseBlockData = {
  id: string;
  inputValue: string;
  keyword: string;
  contextParams: Record<string, string>;
  selectedItems: SelectedItem[];
};

export default function RootGroupNode({ data }: any) {
  const [chooseBlocks, setChooseBlocks] = useState<ChooseBlockData[]>([
    { id: uuidv4(), inputValue: '', keyword: '', contextParams: {}, selectedItems: [] },
  ]);
  const [logic, setLogic] = useState<'AND' | 'OR'>('AND');

  const { setNodes } = useReactFlow();
  const nodeRef = useRef<HTMLDivElement>(null);
  const addLockRef = useRef(false);

  // keep React Flow node height in sync with content
  useEffect(() => {
    if (!nodeRef.current) return;
    const height = nodeRef.current.offsetHeight;
    setNodes((nds) =>
      nds.map((node) =>
        node.id === data.id ? { ...node, style: { ...node.style, height } } : node
      )
    );
  }, [chooseBlocks.length, data?.id, setNodes]);

  // ---------- add handlers (guarded, non-bubbling, never-submit) ----------
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
    // TODO: when you have a nested-group model, create a true child group node here.
    // For now, behave like addCondition to avoid phantom/empty bars.
    addCondition(e);
  };

  // single place to render the list (no >1 vs ===1 split)
  const renderBlocks = () => (
    <div className="flex flex-col gap-2">
      {chooseBlocks.map((block) => (
        <ChooseBlock
          key={block.id}
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
              prev.map((b) => (b.id === block.id ? { ...b, selectedItems: items } : b))
            )
          }
          onSelectOption={(opt) => console.log('Selected:', opt)}
        />
      ))}
    </div>
  );

  return (
    <div
      ref={nodeRef}
      className="bg-gray-100 p-4 w-full"
      onClick={(e) => e.stopPropagation()}  // keep clicks local
    >
      <div className="border rounded bg-gray-100 shadow p-4 w-full">
        {/* AND/OR toggle */}
        <div className="flex items-center gap-2 mb-3">
          <div className="inline-flex border rounded overflow-hidden text-xs bg-white shadow">
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

        {renderBlocks()}

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
