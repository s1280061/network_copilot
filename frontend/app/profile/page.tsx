"use client";

import { useEffect, useState } from "react";
import { useProfile } from "@/lib/profile";
import { getHome } from "@/lib/api";

const ROLES = [
  "ADAS Engineer",
  "組み込みエンジニア",
  "ネットワークエンジニア",
  "学生",
  "その他",
];

const GOALS = ["自動運転", "SDV", "車載Ethernet", "AUTOSAR", "ROS2 / DDS", "診断 (DoIP/UDS)"];

export default function ProfilePage() {
  const { profile, update } = useProfile();
  const [role, setRole] = useState("");
  const [interests, setInterests] = useState<string[]>([]);
  const [goals, setGoals] = useState<string[]>([]);
  const [categories, setCategories] = useState<string[]>([]);
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    setRole(profile.role);
    setInterests(profile.interests);
    setGoals(profile.goals);
  }, [profile]);

  useEffect(() => {
    getHome()
      .then((h) => setCategories(h.categories.map((c) => c.name)))
      .catch(() => {});
  }, []);

  function toggle(list: string[], setList: (v: string[]) => void, val: string) {
    setList(list.includes(val) ? list.filter((x) => x !== val) : [...list, val]);
    setSaved(false);
  }

  function save() {
    update({ role, interests, goals });
    setSaved(true);
  }

  return (
    <div className="max-w-2xl">
      <header className="mb-6">
        <h1 className="text-2xl font-bold">👤 ユーザープロファイル</h1>
        <p className="text-slate-500 text-sm mt-1">
          職種・興味分野・学習目標を設定すると、ホームのおすすめがパーソナライズされます。(この端末に保存されます)
        </p>
      </header>

      <Field label="職種">
        <select
          value={role}
          onChange={(e) => {
            setRole(e.target.value);
            setSaved(false);
          }}
          className="border rounded-lg px-3 py-2 w-full"
        >
          <option value="">選択してください</option>
          {ROLES.map((r) => (
            <option key={r} value={r}>
              {r}
            </option>
          ))}
        </select>
      </Field>

      <Field label="興味分野(カテゴリ)">
        <Chips items={categories} selected={interests} onToggle={(v) => toggle(interests, setInterests, v)} />
      </Field>

      <Field label="学習目標">
        <Chips items={GOALS} selected={goals} onToggle={(v) => toggle(goals, setGoals, v)} />
      </Field>

      <button
        onClick={save}
        className="mt-2 bg-sky-600 text-white px-6 py-2 rounded-lg hover:bg-sky-700"
      >
        保存する
      </button>
      {saved && <span className="ml-3 text-sm text-green-600">✓ 保存しました</span>}
    </div>
  );
}

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div className="mb-5">
      <label className="block text-sm font-semibold text-slate-700 mb-2">{label}</label>
      {children}
    </div>
  );
}

function Chips({
  items,
  selected,
  onToggle,
}: {
  items: string[];
  selected: string[];
  onToggle: (v: string) => void;
}) {
  return (
    <div className="flex flex-wrap gap-2">
      {items.map((it) => {
        const on = selected.includes(it);
        return (
          <button
            key={it}
            onClick={() => onToggle(it)}
            className={`text-sm rounded-full px-3 py-1.5 border ${
              on
                ? "bg-sky-600 text-white border-sky-600"
                : "bg-white text-slate-600 border-slate-300 hover:border-sky-400"
            }`}
          >
            {it}
          </button>
        );
      })}
    </div>
  );
}
