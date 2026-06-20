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
  Statistics:  { bg: "bg-lime-100",   text: "text-lime-800",    icon: "📊" },
  Electronics: { bg: "bg-amber-100",  text: "text-amber-800",   icon: "⚡" },
  Automotive:  { bg: "bg-red-100",    text: "text-red-800",     icon: "🚗" },
  Wireless:    { bg: "bg-cyan-100",   text: "text-cyan-800",    icon: "📡" },
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
  title,
  category,
  className = "",
  iconClassName = "text-4xl",
}: {
  slug: string;
  title?: string;
  category: string;
  className?: string;
  iconClassName?: string;
}) {
  // 0..N-1 = local extensions, N = Pollinations, N+1 = emoji fallback
  const exts = ["png", "jpg", "jpeg", "webp"];
  const [idx, setIdx] = useState(0);
  const style = categoryStyle(category);

  const pollinationsUrl = (() => {
    const prompt = encodeURIComponent(
      `${title ?? slug} automotive ADAS network technical diagram, professional, dark blue theme`
    );
    return `https://image.pollinations.ai/prompt/${prompt}?width=640&height=360&nologo=true&seed=${slug.length}`;
  })();

  // All local extensions tried + Pollinations tried → show emoji
  if (idx > exts.length) {
    return (
      <div className={`${style.bg} flex items-center justify-center ${className}`}>
        <span className={iconClassName}>{style.icon}</span>
      </div>
    );
  }

  const src = idx < exts.length
    ? `/thumbnails/${slug}.${exts[idx]}`
    : pollinationsUrl;

  return (
    // eslint-disable-next-line @next/next/no-img-element
    <img
      src={src}
      alt={`${slug} thumbnail`}
      onError={() => setIdx((i) => i + 1)}
      className={`object-cover ${className}`}
    />
  );
}
