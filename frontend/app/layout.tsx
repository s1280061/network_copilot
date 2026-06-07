import type { Metadata } from "next";
import "./globals.css";
import SidebarNav from "@/components/layout/SidebarNav";
import StudyPanel from "@/components/layout/StudyPanel";
import Header from "@/components/layout/Header";
import { StudyProvider } from "@/lib/study-context";

export const metadata: Metadata = {
  title: "Network Learning Copilot",
  description:
    "ADAS・SDV・組み込みネットワーク技術を体系的に学べるAI教師プラットフォーム",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="ja">
      <body className="bg-slate-50 text-slate-800">
        <StudyProvider>
          <div className="flex flex-col h-screen">
            <Header />
            <div className="flex flex-1 overflow-hidden">
              <SidebarNav />
              <main className="flex-1 overflow-y-auto px-8 py-6">
                <div className="max-w-3xl mx-auto">{children}</div>
              </main>
              <StudyPanel />
            </div>
          </div>
        </StudyProvider>
      </body>
    </html>
  );
}
