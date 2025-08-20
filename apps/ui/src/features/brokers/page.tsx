import BrokersWidget from "@/features/brokers/BrokersWidget";

export const dynamic = "force-dynamic"; // ADHD: avoid caching while testing

export default function Page() {
  return (
    <main className="p-6">
      <h1 className="text-xl font-bold mb-4">Brokers Connectivity Test</h1>
      <BrokersWidget />
    </main>
  );
}
