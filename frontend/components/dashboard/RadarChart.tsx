"use client";

type Axis = { label: string; value: number }; // value 0..100

export default function RadarChart({ data }: { data: Axis[] }) {
  const size = 280;
  const cx = size / 2;
  const cy = size / 2;
  const r = size / 2 - 40;
  const n = data.length;
  if (n < 3) return null;

  const angle = (i: number) => (Math.PI * 2 * i) / n - Math.PI / 2;
  const point = (i: number, ratio: number) => {
    const a = angle(i);
    return [cx + r * ratio * Math.cos(a), cy + r * ratio * Math.sin(a)];
  };

  const rings = [0.25, 0.5, 0.75, 1];
  const valuePts = data
    .map((d, i) => point(i, Math.max(0.02, d.value / 100)).join(","))
    .join(" ");

  return (
    <svg viewBox={`0 0 ${size} ${size}`} className="w-full max-w-sm mx-auto">
      {/* grid rings */}
      {rings.map((ring) => (
        <polygon
          key={ring}
          points={data.map((_, i) => point(i, ring).join(",")).join(" ")}
          fill="none"
          stroke="#e2e8f0"
        />
      ))}
      {/* axes */}
      {data.map((_, i) => {
        const [x, y] = point(i, 1);
        return <line key={i} x1={cx} y1={cy} x2={x} y2={y} stroke="#e2e8f0" />;
      })}
      {/* value polygon */}
      <polygon
        points={valuePts}
        fill="rgba(2,132,199,0.25)"
        stroke="#0284c7"
        strokeWidth={2}
      />
      {/* labels */}
      {data.map((d, i) => {
        const [x, y] = point(i, 1.18);
        return (
          <text
            key={i}
            x={x}
            y={y}
            fontSize={11}
            textAnchor="middle"
            dominantBaseline="middle"
            fill="#475569"
          >
            {d.label}
          </text>
        );
      })}
    </svg>
  );
}
