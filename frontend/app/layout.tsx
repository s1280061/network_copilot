import type { Metadata } from "next";
import "./globals.css";
import SidebarNav from "@/components/layout/SidebarNav";
import StudyPanel from "@/components/layout/StudyPanel";
import Header from "@/components/layout/Header";
import { StudyProvider } from "@/lib/study-context";

export const metadata: Metadata = {
  title: "Network Copilot",
  description: "車載ネットワーク・データサイエンスの技術記事サイト",
  icons: {
    icon: [
      { url: "/favicon-32.png", sizes: "32x32", type: "image/png" },
      { url: "/icon-192.png",   sizes: "192x192", type: "image/png" },
      { url: "/icon-512.png",   sizes: "512x512", type: "image/png" },
    ],
    apple: { url: "/icon-192.png", sizes: "192x192" },
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="ja">
      <head>
        <link rel="manifest" href="/manifest.json" />
      </head>
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
