"use client";

import { useEffect, useState } from "react";
import { getDashboard } from "@/lib/api";
import { Dashboard } from "@/lib/types";
import RadarChart from "@/components/dashboard/RadarChart";

export default function DashboardPage() {
  const [d, setD] = useState<Dashboard | null>(null);

  useEffect(() => {
    getDashboard().then(setD).catch(() => {});
  }, []);

  return (
    <div>
      <header className="mb-6">
        <h1 className="text-2xl font-bold">📊 学習進捗ダッシュボード</h1>
        <p className="text-slate-500 text-sm mt-1">
          全体とカテゴリ別の学習状況を確認できます。
        </p>
      </header>

      {!d && <p className="text-slate-400">読み込み中...</p>}

      {d && (
        <div className="space-y-6">
          <div className="grid grid-cols-3 gap-3">
            <Stat label="学習済み記事" value={`${d.completed}`} />
            <Stat label="総記事数" value={`${d.total}`} />
            <Stat label="学習率" value={`${d.rate}%`} />
          </div>

          <div className="grid md:grid-cols-2 gap-6">
            <div className="border rounded-xl bg-white p-4">
              <h2 className="font-semibold mb-3">カテゴリ別到達度</h2>
              <RadarChart
                data={d.categories.map((c) => ({
                  label: c.category,
                  value: c.rate,
                }))}
              />
            </div>

            <div className="border rounded-xl bg-white p-4">
              <h2 className="font-semibold mb-3">カテゴリ別進捗</h2>
              <div className="space-y-3">
                {d.categories.map((c) => (
                  <div key={c.category}>
                    <div className="flex justify-between text-sm mb-1">
                      <span>{c.category}</span>
                      <span className="text-slate-400">
                        {c.completed}/{c.total} ({c.rate}%)
                      </span>
                    </div>
                    <div className="h-2 bg-slate-100 rounded-full overflow-hidden">
                      <div
                        className="h-full bg-sky-500"
                        style={{ width: `${c.rate}%` }}
                      />
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

function Stat({ label, value }: { label: string; value: string }) {
  return (
    <div className="border rounded-xl bg-white p-4 text-center">
      <p className="text-3xl font-bold text-sky-700">{value}</p>
      <p className="text-xs text-slate-500 mt-1">{label}</p>
    </div>
  );
}
