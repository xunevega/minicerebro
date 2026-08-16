export const sectionPaths = {
  write: "/escribir",
  profile: "/criterio",
  knowledge: "/biblioteca",
  history: "/historial",
  technical: "/sistema",
} as const;

export type SectionId = keyof typeof sectionPaths;

const tabBySection: Record<SectionId, string> = {
  write: "editor",
  profile: "preferences",
  knowledge: "knowledge",
  history: "audit",
  technical: "persistence",
};

export function sectionFromPath(pathname: string): SectionId {
  const normalized = pathname.replace(/\/+$/, "") || "/";
  const found = (Object.entries(sectionPaths) as Array<[SectionId, string]>).find(
    ([, path]) => path === normalized,
  );
  return found?.[0] ?? "write";
}

export function defaultTabForPath(pathname: string): string {
  return tabBySection[sectionFromPath(pathname)];
}

export function titleForSection(label: string): string {
  return `${label} — Editados`;
}
