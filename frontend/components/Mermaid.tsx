"use client";

import { useEffect, useRef } from "react";
import mermaid from "mermaid";

mermaid.initialize({ startOnLoad: false, theme: "default" });

export default function Mermaid({ chart }: { chart: string }) {
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!ref.current || !chart) return;
    const id = "m" + Math.random().toString(36).slice(2);
    mermaid
      .render(id, chart)
      .then(({ svg }) => {
        if (ref.current) ref.current.innerHTML = svg;
      })
      .catch(() => {
        if (ref.current) ref.current.textContent = chart;
      });
  }, [chart]);

  return <div ref={ref} className="overflow-x-auto" />;
}
