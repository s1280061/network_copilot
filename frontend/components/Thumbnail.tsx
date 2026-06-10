"use client";

import { useState } from "react";

// Per-category colors / icons used as a fallback banner when no image exists.
export const CATEGORY_STYLE: Record<
  string,
  { bg: string; text: string; icon: string }
> = {
  Ethernet:  { bg: "bg-blue-100",   text: "text-blue-700",   icon: "🔌" },
  "TCP/IP":  { bg: "bg-sky-100",    text: "text-sky-700",    icon: "🌐" },
  PCAP:      { bg: "bg-violet-100", text: "text-violet-700", icon: "🔍" },
  "SOME/IP": { bg: "bg-orange-100", text: "text-orange-700", icon: "🚗" },
  AUTOSAR:   { bg: "bg-green-100",  text: "text-green-700",  icon: "⚙️" },
  SDV:       { bg: "bg-rose-100",   text: "text-rose-700",   icon: "🤖" },
  Python:    { bg: "bg-yellow-100", text: "text-yellow-800", icon: "🐍" },
  ML:        { bg: "bg-purple-100",  text: "text-purple-800",  icon: "🤖" },
  DL:        { bg: "bg-indigo-100", text: "text-indigo-800", icon: "🧠" },
  GenAI:     { bg: "bg-pink-100",   text: "text-pink-800",   icon: "✨" },
  CV:          { bg: "bg-teal-100",    text: "text-teal-800",    icon: "👁️" },
  Electronics: { bg: "bg-amber-100",  text: "text-amber-800",   icon: "⚡" },
};

export const DEFAULT_STYLE = {
  bg: "bg-slate-100",
  text: "text-slate-600",
  icon: "📄",
};

export function categoryStyle(category: string) {
  return CATEGORY_STYLE[category] ?? DEFAULT_STYLE;
}

/**
 * note-style thumbnail. Looks for /public/thumbnails/{slug}.(png|jpg|jpeg|webp).
 * If the image is missing/fails to load, falls back to a colored category banner.
 */
export default function Thumbnail({
  slug,
  category,
  className = "",
  iconClassName = "text-4xl",
}: {
  slug: string;
  category: string;
  className?: string;
  iconClassName?: string;
}) {
  const exts = ["png", "jpg", "jpeg", "webp"];
  const [idx, setIdx] = useState(0);
  const style = categoryStyle(category);
  const failed = idx >= exts.length;

  if (failed) {
    return (
      <div
        className={`${style.bg} flex items-center justify-center ${className}`}
      >
        <span className={iconClassName}>{style.icon}</span>
      </div>
    );
  }

  return (
    // eslint-disable-next-line @next/next/no-img-element
    <img
      src={`/thumbnails/${slug}.${exts[idx]}`}
      alt={`${slug} thumbnail`}
      onError={() => setIdx((i) => i + 1)}
      className={`object-cover ${className}`}
    />
  );
}
