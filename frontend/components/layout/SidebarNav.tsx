"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useState } from "react";

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
];

export default function SidebarNav() {
  const path = usePathname();
  const [collapsed, setCollapsed] = useState(true);

  return (
    <aside
      className={`${
        collapsed ? "w-14" : "w-56"
      } shrink-0 border-r bg-white py-4 overflow-y-auto transition-all duration-300 flex flex-col`}
    >
      <nav className="flex-1 space-y-1 px-2">
        {NAV.map((n) => {
          const active =
            n.href === "/" ? path === "/" : path.startsWith(n.href);
          return (
            <Link
              key={n.href}
              href={n.href}
              title={collapsed ? n.label : undefined}
              className={`flex items-center gap-3 px-2 py-2 rounded-lg text-sm font-medium transition-colors ${
                active
                  ? "bg-sky-50 text-sky-700"
                  : "text-slate-600 hover:bg-slate-100"
              }`}
            >
              <span className="text-lg shrink-0">{n.icon}</span>
              {!collapsed && <span className="truncate">{n.label}</span>}
            </Link>
          );
        })}
      </nav>

      <button
        onClick={() => setCollapsed((c) => !c)}
        className="mx-2 mt-3 py-1.5 rounded-lg text-slate-400 hover:bg-slate-100 hover:text-slate-600 transition-colors text-xs flex items-center justify-center gap-1"
        title={collapsed ? "サイドバーを展開" : "サイドバーを折りたたむ"}
      >
        <span className="text-base">{collapsed ? "→" : "←"}</span>
        {!collapsed && <span>閉じる</span>}
      </button>
    </aside>
  );
}
