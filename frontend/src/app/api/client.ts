import { API_BASE } from "../config.ts";

export async function processRepo(repoUrl: string) {
  const res = await fetch(`${API_BASE}/process_repo`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    credentials: "include", // REQUIRED for session cookie
    body: JSON.stringify({ repo_url: repoUrl }),
  });

  if (!res.ok) {
    const err = await res.text();
    throw new Error(err);
  }

  return res.json();
}

export async function queryRepo(query: string) {
  const res = await fetch(`${API_BASE}/query`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    credentials: "include", // REQUIRED
    body: JSON.stringify({ query }),
  });

  if (!res.ok) {
    const err = await res.text();
    throw new Error(err);
  }

  return res.json();
}
