"use client";

import { createContext, useContext, useState, ReactNode } from "react";
import { PanelContext } from "./types";

type Ctx = {
  panel: PanelContext;
  setPanel: (p: PanelContext) => void;
};

const StudyContext = createContext<Ctx | null>(null);

export function StudyProvider({ children }: { children: ReactNode }) {
  const [panel, setPanel] = useState<PanelContext>({});
  return (
    <StudyContext.Provider value={{ panel, setPanel }}>
      {children}
    </StudyContext.Provider>
  );
}

export function useStudyPanel() {
  const ctx = useContext(StudyContext);
  if (!ctx) throw new Error("useStudyPanel must be used within StudyProvider");
  return ctx;
}
