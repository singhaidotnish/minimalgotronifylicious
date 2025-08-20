'use client';
import { useEffect, useState } from "react";
import { api } from "@/lib/apiClient";

// ADHD: Simple smoke test widget for backend connectivity.
export default function BrokersWidget() {
  const [brokers, setBrokers] = useState<string[]>([]);
  const [error, setError] = useState<string>("");

  useEffect(() => {
    let isAlive = true;
    api.get("/brokers")
      .then(r => { if (isAlive) setBrokers(r.data); })
      .catch(e => { if (isAlive) setError(e?.message || "Failed to load"); });
    return () => { isAlive = false; };
  }, []);

  if (error) return <div className="text-red-600">Error: {error}</div>;
  return (
    <div className="p-4 border rounded-lg">
      <div className="font-semibold mb-2">Brokers (live from backend)</div>
      <pre className="text-sm">{JSON.stringify(brokers, null, 2)}</pre>
    </div>
  );
}
