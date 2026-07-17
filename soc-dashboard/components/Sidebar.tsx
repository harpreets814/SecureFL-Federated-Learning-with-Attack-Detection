"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

export default function Sidebar() {
  const pathname = usePathname();

  const navItems = [
    { name: "Dashboard", path: "/" },
    { name: "Clients", path: "/clients" },
    { name: "Security", path: "/security" },
    { name: "Metrics", path: "/metrics" },
  ];

  return (
    <div className="w-64 h-screen bg-[var(--card)] border-r border-[var(--border)] p-6 flex flex-col">

      <h2 className="text-2xl font-bold mb-8">🔐 Secure FL</h2>

      <nav className="space-y-2 text-sm">
        {navItems.map((item) => {
          const active = pathname === item.path;

          return (
            <Link
              key={item.path}
              href={item.path}
              className={`block px-4 py-2 rounded-lg transition ${
                active
                  ? "bg-blue-500 text-white"
                  : "text-[var(--muted)] hover:bg-blue-500/20"
              }`}
            >
              {item.name}
            </Link>
          );
        })}
      </nav>

      <div className="mt-auto text-xs text-[var(--muted)]">
        AI Security System
      </div>
    </div>
  );
}