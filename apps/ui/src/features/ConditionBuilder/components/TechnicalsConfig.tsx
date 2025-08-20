// src/features/ConditionBuilder/components/TechnicalsConfig.tsx
export default function TechnicalsConfig({
  value, onChange,
}: { value: Record<string, unknown>; onChange: (v: Record<string, unknown>) => void }) {
  return (
    <div className="text-xs text-gray-600 italic">
      TechnicalsConfig placeholder
      <button className="ml-2 underline" onClick={() => onChange({})}>Reset</button>
    </div>
  );
}
