"use client";

import Link from "next/link";
import Image from "next/image";
import { usePathname, useSearchParams } from "next/navigation";
import { useState, Suspense } from "react";

const NAV = [
  { href: "/", label: "ホーム", icon: "🏠" },
  { href: "/glossary", label: "用語集", icon: "📖" },
  { href: "/glossary?tab=Statistics", label: "統計", icon: "📊", tab: "Statistics" },
  { href: "/glossary?tab=ML", label: "機械学習", icon: "🤖", tab: "ML" },
  { href: "/glossary?tab=DL", label: "深層学習", icon: "🧠", tab: "DL" },
  { href: "/glossary?tab=GenAI", label: "生成AI", icon: "✨", tab: "GenAI" },
  { href: "/glossary?tab=Python", label: "Python", icon: "🐍", tab: "Python" },
  { href: "/glossary?tab=アルゴリズム", label: "アルゴリズム", icon: "⚙️", tab: "アルゴリズム" },
  { href: "/glossary?tab=C言語", label: "C言語", icon: "🔧", tab: "C言語" },
  { href: "/glossary?tab=CAD%2F設計", label: "CAD/設計", icon: "📐", tab: "CAD/設計" },
  { href: "/chat", label: "AIチャット", icon: "💬" },
  { href: "/favorites", label: "お気に入り", icon: "⭐" },
  { href: "/board", label: "掲示板", icon: "📝" },
];

function SidebarNavInner() {
  const path = usePathname();
  const searchParams = useSearchParams();
  const currentTab = searchParams.get("tab") ?? "";
  const [collapsed, setCollapsed] = useState(true);

  return (
    <aside
      className={`${
        collapsed ? "w-14" : "w-56"
      } shrink-0 border-r bg-white py-4 overflow-y-auto transition-all duration-300 flex flex-col`}
    >
      {/* ロゴ */}
      <Link href="/" className="flex items-center gap-2.5 px-3 pb-4 border-b border-slate-100 mb-2">
        <Image
          src="/icon-192.png"
          alt="Network Copilot"
          width={32}
          height={32}
          className="rounded-lg shrink-0"
        />
        {!collapsed && (
          <span className="text-sm font-bold text-slate-800 truncate leading-tight">
            Network<br />Copilot
          </span>
        )}
      </Link>

      <nav className="flex-1 space-y-1 px-2">
        {NAV.map((n) => {
          let active: boolean;
          if (n.href === "/") {
            active = path === "/";
          } else if ("tab" in n && n.tab) {
            active = path === "/glossary" && currentTab === n.tab;
          } else if (n.href === "/glossary") {
            active = path === "/glossary" && !currentTab;
          } else {
            active = path.startsWith(n.href);
          }
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

export default function SidebarNav() {
  return (

    <Suspense fallback={
      <aside className="w-14 shrink-0 border-r bg-white py-4" />
    }>
      <SidebarNavInner />
    </Suspense>
  );
}
