import { chromium } from "playwright";

const frontendUrl = process.env.FRONTEND_URL ?? "http://127.0.0.1:5173";
const candidateId = `knowledge-ui-candidate-${Date.now().toString(36)}`;

const browser = await chromium.launch();
const page = await browser.newPage();

try {
  await page.goto(frontendUrl, { waitUntil: "networkidle" });

  const panel = page.locator(".proposalBox", { hasText: "Candidato y publicacion" });
  await panel.getByText("Crear candidato congela un snapshot revisable.").waitFor();

  await page.getByLabel("ID de candidate").fill(candidateId);
  await page.getByLabel("Version base de candidate").selectOption("knowledge-v3");
  await page.getByLabel("Autor de candidate").fill("smoke-ui");
  await page.getByLabel("Motivo").fill("Smoke UI de candidate y publicacion.");

  const candidateResponse = page.waitForResponse((response) => {
    const url = new URL(response.url());
    return url.pathname === "/knowledge/candidates" && response.request().method() === "POST";
  });
  await panel.getByRole("button", { name: "Crear candidate" }).click();
  await candidateResponse;

  await page.getByLabel("Version candidata para publicar").selectOption(candidateId);
  const readinessResponse = page.waitForResponse((response) => {
    const url = new URL(response.url());
    return (
      url.pathname === "/knowledge/publication/readiness" &&
      url.searchParams.get("version") === candidateId
    );
  });
  await panel.getByRole("button", { name: "Ver readiness" }).click();
  await readinessResponse;
  await panel.locator(".metric", { hasText: "Version" }).filter({ hasText: candidateId }).waitFor();
  await panel.locator(".metric", { hasText: "Publicable" }).filter({ hasText: "si" }).waitFor();
  await panel.locator(".metric", { hasText: "Bloqueos" }).filter({ hasText: "0" }).waitFor();

  const publicationResponse = page.waitForResponse((response) => {
    const url = new URL(response.url());
    return url.pathname === "/knowledge/publications" && response.request().method() === "POST";
  });
  await panel.getByRole("button", { name: "Publicar candidate" }).click();
  await publicationResponse;

  await panel.locator(".metric", { hasText: "Estado" }).filter({ hasText: "published" }).waitFor();
  await page.getByLabel("Version explorada").selectOption(candidateId);
  await page.locator(".metric", { hasText: "Version cargada" }).filter({ hasText: candidateId }).waitFor();
} finally {
  await browser.close();
}
