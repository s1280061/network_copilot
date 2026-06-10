"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const NAV = [
  { href: "/", label: "ホーム", icon: "🏠" },
  { href: "/roadmap", label: "学習ロードマップ", icon: "📚" },
  { href: "/glossary", label: "用語集", icon: "📖" },
  { href: "/dashboard", label: "ダッシュボード", icon: "📊" },
  { href: "/chat", label: "AIチャット", icon: "💬" },
  { href: "/pcap", label: "PCAP解析", icon: "📂" },
  { href: "/favorites", label: "お気に入り", icon: "⭐" },
  { href: "/history", label: "学習履歴", icon: "📝" },
  { href: "/profile", label: "プロフィール", icon: "👤" },
  { href: "/python", label: "Python DS", icon: "🐍" },
];

export default function SidebarNav() {
  const path = usePathname();

  return (
    <aside className="w-56 shrink-0 border-r bg-white py-4 overflow-y-auto">
      <nav className="space-y-1 px-3">
        {NAV.map((n) => {
          const active =
            n.href === "/" ? path === "/" : path.startsWith(n.href);
          return (
            <Link
              key={n.href}
              href={n.href}
              className={`flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                active
                  ? "bg-sky-50 text-sky-700"
                  : "text-slate-600 hover:bg-slate-100"
              }`}
            >
              <span className="text-lg">{n.icon}</span>
              {n.label}
            </Link>
          );
        })}
      </nav>
    </aside>
  );
}
