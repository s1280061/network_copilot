export type Ref = { slug: string; title: string };

export type ArticleMeta = {
  slug: string;
  title: string;
  level: number;
  category: string;
  difficulty: string;
  updated: string;
  related: string[];
  next: string[];
  tags: string[];
  excerpt?: string;
  views?: number;
  completed?: boolean;
  favorite?: boolean;
};

export type HomeCategory = { name: string; articles: ArticleMeta[] };
export type RankItem = { slug: string; title: string; views: number };
export type Home = { categories: HomeCategory[]; ranking: RankItem[] };

export type Dashboard = {
  total: number;
  completed: number;
  rate: number;
  categories: { category: string; total: number; completed: number; rate: number }[];
};

export type SearchHit = {
  slug: string;
  title: string;
  category?: string;
  heading?: string;
  score?: number;
};

export type Article = ArticleMeta & {
  html: string;
  prereq_full: Ref[];
  related_full: Ref[];
  next_full: Ref[];
};

export type Profile = {
  role: string;
  interests: string[]; // category names
  goals: string[];
};

export type RoadmapItem = Ref & { completed: boolean };
export type RoadmapLevel = {
  level: number;
  title: string;
  description: string;
  items: RoadmapItem[];
};
export type Roadmap = {
  levels: RoadmapLevel[];
  progress: { completed: number; total: number };
};

export type PcapResult = {
  packet_count: number;
  protocols: Record<string, number>;
  peers: { address: string; count: number }[];
  ports: { port: number; count: number }[];
  stacks: { path: string; count: number }[];
  mermaid: string;
  explanation: string;
  recommendations: Ref[];
  recommend_note: string;
};

export type History = {
  views: { id: number; slug: string; title: string; viewed_at: string }[];
  chats: { id: number; question: string; answer: string; created_at: string }[];
  pcaps: { id: number; filename: string; summary: string; created_at: string }[];
};

// Context shown in the right-hand study panel.
export type PanelContext = {
  title?: string;
  slug?: string;
  prereq?: Ref[];
  related?: Ref[];
  next?: Ref[];
  note?: string;
  recommendations?: Ref[];
};
