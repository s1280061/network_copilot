import RoadmapTree from "@/components/roadmap/RoadmapTree";

export default function RoadmapPage() {
  return (
    <div>
      <header className="mb-6">
        <h1 className="text-2xl font-bold">学習ロードマップ</h1>
        <p className="text-slate-500 text-sm mt-1">
          通信の基礎から SDV / ADAS 通信まで、順番に学べる体系です。項目をクリックして記事を読み、学習済みにしましょう。
        </p>
      </header>
      <RoadmapTree />
    </div>
  );
}
