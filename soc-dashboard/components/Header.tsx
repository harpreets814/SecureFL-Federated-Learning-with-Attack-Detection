"use client";

export default function Header({ dark, setDark }: any) {
  return (
    <div className="flex justify-between items-center mb-6">

      <h1 className="text-2xl font-bold">
        Federated Learning Dashboard
      </h1>

      <button
        onClick={() => setDark(!dark)}
        className="px-3 py-2 rounded-lg bg-[var(--card)] border border-[var(--border)] hover:scale-105 transition"
      >
        {dark ? "☀️ Light" : "🌙 Dark"}
      </button>

    </div>
  );
}