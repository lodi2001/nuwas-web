import { LandingPageData } from "./types";

const API_URL = process.env.API_URL || "http://localhost:8008";

export async function getLandingData(): Promise<LandingPageData> {
  const res = await fetch(`${API_URL}/api/landing/`, {
    next: { revalidate: 60 },
  });

  if (!res.ok) {
    throw new Error(`API error: ${res.status}`);
  }

  return res.json();
}
