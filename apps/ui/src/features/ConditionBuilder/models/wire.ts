// apps/ui/src/features/ConditionBuilder/models/wire.ts
export type WireCondition = {
  keyword: string;
  params: Record<string, string>;
  label: string;
};

export type WireGroup = {
  logic: 'AND' | 'OR';
  blocks: WireCondition[];
};

/**
 * Take your ChooseBlock UI state and produce a backend-friendly envelope.
 * It flattens each ChooseBlock's selectedItems into `blocks`.
 */
export function toWireGroup(
  chooseBlocks: Array<{
    id: string;
    keyword: string;
    contextParams: Record<string, string>;
    selectedItems: Array<{ id: string; keyword?: string; label: string; params?: Record<string, string> }>;
  }>,
  logic: 'AND' | 'OR'
): WireGroup {
  const blocks: WireCondition[] = [];

  for (const b of chooseBlocks) {
    // take confirmed chips first (most reliable)
    for (const chip of b.selectedItems) {
      blocks.push({
        keyword: chip.keyword ?? (b.keyword || 'custom'),
        params: chip.params ?? {},
        label: chip.label,
      });
    }

    // if a keyword is currently selected but not confirmed, you can also push that (optional)
    // if (b.keyword && Object.keys(b.contextParams).length > 0) {
    //   blocks.push({ keyword: b.keyword, params: b.contextParams, label: `${b.keyword}` });
    // }
  }

  return { logic, blocks };
}
