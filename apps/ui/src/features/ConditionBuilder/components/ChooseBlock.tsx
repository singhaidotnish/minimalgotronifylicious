// src/features/ConditionBuilder/components/ChooseBlock.tsx
'use client';

import React, { useEffect } from 'react';
import { X, Copy, ClipboardPaste } from 'lucide-react';
import { DndContext, closestCenter } from '@dnd-kit/core';
import { arrayMove, SortableContext, useSortable, horizontalListSortingStrategy } from '@dnd-kit/sortable';
import { CSS } from '@dnd-kit/utilities';
import { getClipboard, setClipboard } from '@/utils/clipboard';
import { GROUPS, buildPreviewFromKey } from '@/features/ConditionBuilder/models/conditionGroups';
import ContextUI from './ContextUI';

// ✅ keep keyword optional so legacy {id,label} arrays still type-check
type SelectedItem = {
  id: string;
  label: string;                       // full two-line label
  keyword?: string;                    // optional (older callers may not include it)
  params?: Record<string, string>;
};

interface ChooseBlockProps {
  onDelete: () => void;
  inputValue: string;
  onChange: (val: string) => void;
  onSelectOption: (option: string) => void;
  groups: { label: string; options: { key: string; label: string }[] }[];
  selectedKeyword: string;
  onKeywordChange: (val: string) => void;

  // ✅ ContextUI needs an object, not ParamDef[]
  contextParams: Record<string, string>;
  onContextParamsChange: (obj: Record<string, string>) => void;

  selectedItems: SelectedItem[];
  onSelectedItemsChange: (items: SelectedItem[]) => void;
}

// ❌ delete any local buildPreview() or previewBuilder util imports — we ONLY use buildPreviewFromKey

function generateUniqueId(base: string): string {
  return `${base}-${Math.random().toString(36).slice(2, 9)}`;
}

function PreviewBlock({
  id, label, content, onRemove,
}: { id: string; label: string; content: string; onRemove: (id: string) => void }) {
  const { attributes, listeners, setNodeRef, transform, transition } = useSortable({ id });
  const style = { transform: CSS.Transform.toString(transform), transition };
  const copyToClipboard = (content: string) => {
    console.log('🔍 Copying content:', content);
    setClipboard(content);
  };

  return (
    <div ref={setNodeRef} style={style} {...attributes} {...listeners}
      className="relative bg-white border border-blue-200 shadow-sm rounded-sm p-1 text-xs text-blue-700 w-fit min-w-[120px] min-h-0 flex items-center gap-1 overflow-visible">
      <button onClick={() => copyToClipboard(content)} className="absolute -top-3 -left-3 z-10 bg-white rounded-full w-6 h-6 flex items-center justify-center shadow" title="Copy Block">
        <Copy className="w-3.5 h-3.5 text-blue-600" />
      </button>
      <button onClick={() => onRemove(id)} className="absolute -top-3 -right-3 z-10 bg-white rounded-full w-6 h-6 flex items-center justify-center shadow" title="Remove Block">
        <X className="w-3.5 h-3.5 text-red-600" />
      </button>

      <div className="font-bold text-center text-blue-700 mb-1">{label}</div>
      <div className="text-xs text-center text-blue-700 whitespace-pre-line">{content}</div>
    </div>
  );
}

export default function ChooseBlock(props: ChooseBlockProps) {
  const {
    onDelete, inputValue, onChange, onSelectOption, groups,
    selectedKeyword, onKeywordChange,
    contextParams, onContextParamsChange,
    selectedItems, onSelectedItemsChange,
  } = props;

  const [filtered, setFiltered] = React.useState<typeof groups>([]);

  const selectedOption = GROUPS.flatMap(g => g.options).find(o => o.key === selectedKeyword);

  useEffect(() => {
    if (!inputValue.trim()) { setFiltered([]); return; }
    const q = inputValue.toLowerCase();
    const matches = groups
      .map(g => ({ label: g.label, options: g.options.filter(o => o.label.toLowerCase().includes(q)) }))
      .filter(g => g.options.length > 0);
    setFiltered(matches);
  }, [inputValue, groups]);

  const handleSelect = (optLabel: string) => {
    onSelectOption(optLabel);
    setFiltered([]);
  };

  const handlePaste = () => {
    const data = getClipboard();
    console.log('🔍 Pasting content:', data);
    if (data) {
      const uniqueId = generateUniqueId(data);
      onSelectedItemsChange([...selectedItems, { id: uniqueId, label: data }]);
      onSelectOption(data);
      setFiltered([]);
    }
    // ❌ setClipboard(null) → string only
    setClipboard('');
  };

  const handleRemove = (id: string) => {
    onSelectedItemsChange(selectedItems.filter(it => it.id !== id));
  };

  const handleDragEnd = (event: any) => {
    const { active, over } = event;
    if (active.id !== over?.id) {
      const oldIndex = selectedItems.findIndex(i => i.id === active.id);
      const newIndex = selectedItems.findIndex(i => i.id === over.id);
      onSelectedItemsChange(arrayMove(selectedItems, oldIndex, newIndex));
    }
  };

  return (
    <div className="w-full max-w-6xl mx-auto border border-gray-200 bg-white shadow-sm overflow-visible p-1">
      <div className="relative">
        <button onClick={handlePaste} className="absolute -top-3 right-6 z-10 bg-white rounded-full w-6 h-6 flex items-center justify-center shadow" title="Paste">
          <ClipboardPaste className="w-3.5 h-3.5 text-green-600" />
        </button>
        <button onClick={onDelete} className="absolute -top-3 -right-3 z-10 bg-white rounded-full w-6 h-6 flex items-center justify-center shadow" title="Remove">
          <X className="w-3.5 h-3.5 text-red-600" />
        </button>
      </div>

      <div className="flex items-start gap-4 px-2 pt-2">
        <div className="flex flex-col gap-2 shrink-0 z-10 w-48">
          <select
            value={selectedKeyword || ''}
            onChange={(e) => {
              const key = e.target.value;
              onKeywordChange(key);
              onContextParamsChange({});
              onChange(key);
              onSelectOption(key);
            }}
            className="border border-gray-300 rounded h-8"
          >
            <option value="">Choose...</option>
            {GROUPS.map(group => (
              <optgroup key={group.label} label={group.label}>
                {group.options.map(opt => (
                  <option key={opt.key} value={opt.key}>{opt.label}</option>
                ))}
              </optgroup>
            ))}
          </select>

          {filtered.length > 0 && (
            <ul className="absolute top-full left-0 w-full bg-white border z-50 shadow text-xs">
              {filtered.map((g, gi) => (
                <React.Fragment key={gi}>
                  <li className="px-2 py-1 font-semibold text-gray-500 bg-gray-50 cursor-default">{g.label}</li>
                  {g.options.map((opt, i) => (
                    <li key={i} className="px-2 py-1 hover:bg-blue-100 cursor-pointer" onClick={() => handleSelect(opt.label)}>
                      {opt.label}
                    </li>
                  ))}
                </React.Fragment>
              ))}
            </ul>
          )}
        </div>

        {selectedKeyword && selectedOption && (
          <ContextUI
            keyword={selectedKeyword}
            // ✅ ContextUI wants an object of current values
            params={contextParams}
            // ✅ ContextUI prop is onParamChange, NOT onContextParamsChange
            onParamChange={(key: string, val: string) =>
              onContextParamsChange({ ...contextParams, [key]: val })
            }
            // ✅ onConfirm has 0 args in your current ContextUI
            onConfirm={() => {
              const label = buildPreviewFromKey(selectedKeyword, contextParams, selectedOption.label);
              onSelectedItemsChange([
                ...selectedItems,
                { id: generateUniqueId(selectedKeyword), keyword: selectedKeyword, label, params: { ...contextParams } },
              ]);
              onKeywordChange('');
              onContextParamsChange({});
            }}
            onCancel={() => {
              onKeywordChange('');
              onContextParamsChange({});
            }}
          />
        )}

        <DndContext collisionDetection={closestCenter} onDragEnd={handleDragEnd}>
          <SortableContext items={selectedItems.map(i => i.id)} strategy={horizontalListSortingStrategy}>
            <div className="flex flex-wrap gap-4 items-stretch min-h-[80px]">
              {selectedItems.map(item => (
                <PreviewBlock
                  key={item.id}
                  id={item.id}
                  label={item.label.split('\n')[0]}
                  content={item.label}            // full two-line label we already built
                  onRemove={handleRemove}
                />
              ))}
            </div>
          </SortableContext>
        </DndContext>
      </div>
    </div>
  );
}
