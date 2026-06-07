"use client";

import { useEffect, useState } from "react";
import { Profile, Home, ArticleMeta } from "./types";

const PROFILE_KEY = "nlc_profile";
const VIEWS_KEY = "nlc_views";

export const EMPTY_PROFILE: Profile = { role: "", interests: [], goals: [] };

export function loadProfile(): Profile {
  if (typeof window === "undefined") return EMPTY_PROFILE;
  try {
    return { ...EMPTY_PROFILE, ...JSON.parse(localStorage.getItem(PROFILE_KEY) || "{}") };
  } catch {
    return EMPTY_PROFILE;
  }
}

export function saveProfile(p: Profile) {
  localStorage.setItem(PROFILE_KEY, JSON.stringify(p));
}

/** Record a viewed slug (client-side history for personalization). */
export function recordView(slug: string) {
  if (typeof window === "undefined") return;
  try {
    const arr: string[] = JSON.parse(localStorage.getItem(VIEWS_KEY) || "[]");
    const next = [slug, ...arr.filter((s) => s !== slug)].slice(0, 50);
    localStorage.setItem(VIEWS_KEY, JSON.stringify(next));
  } catch {
    /* ignore */
  }
}

export function loadViews(): string[] {
  if (typeof window === "undefined") return [];
  try {
    return JSON.parse(localStorage.getItem(VIEWS_KEY) || "[]");
  } catch {
    return [];
  }
}

export function useProfile() {
  const [profile, setProfile] = useState<Profile>(EMPTY_PROFILE);
  useEffect(() => setProfile(loadProfile()), []);
  const update = (p: Profile) => {
    setProfile(p);
    saveProfile(p);
  };
  return { profile, update };
}

/**
 * Personalized recommendations from profile interests (categories) + view
 * history. Prefers articles in interested categories the user hasn't seen yet.
 */
export function useProfileRecommend(home: Home | null): ArticleMeta[] {
  const [recs, setRecs] = useState<ArticleMeta[]>([]);

  useEffect(() => {
    if (!home) return;
    const profile = loadProfile();
    const viewed = new Set(loadViews());
    const all: ArticleMeta[] = home.categories.flatMap((c) => c.articles);
    if (profile.interests.length === 0 && viewed.size === 0) {
      setRecs([]);
      return;
    }

    const interests = new Set(profile.interests);
    const scored = all
      .filter((a) => !viewed.has(a.slug))
      .map((a) => {
        let score = 0;
        if (interests.has(a.category)) score += 3;
        return { a, score };
      })
      .filter((x) => x.score > 0)
      .sort((a, b) => b.score - a.score)
      .slice(0, 8)
      .map((x) => x.a);

    setRecs(scored);
  }, [home]);

  return recs;
}
