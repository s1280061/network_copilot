"use client";

import Link from "next/link";

export default function Header() {
  return (
    <header className="h-14 shrink-0 bg-slate-900 text-white flex items-center px-6">
      <Link href="/" className="font-bold tracking-tight">
        📡 Network Learning Copilot
      </Link>
    </header>
  );
}
