import { chromium } from "playwright";

const frontendUrl = process.env.FRONTEND_URL ?? "http://127.0.0.1:5173";

const browser = await chromium.launch();
const page = await browser.newPage();

try {
  await page.goto(frontendUrl, { waitUntil: "domcontentloaded" });
  await page.getByRole("button", { name: "Biblioteca" }).click();
  await page.getByRole("button", { name: "Ver modo tecnico" }).click();

  const panel = page.locator(".proposalBox", {
    has: page.getByRole("heading", { name: /^Publicacion de la base$/ }),
  });
  await panel.getByText("Crear candidato congela una version revisable.").waitFor();
  await page.locator(".metric", { hasText: "Base" }).filter({ hasText: "Base publicada actual" }).first().waitFor({
    timeout: 90000,
  });

  await page
    .getByLabel("Version base del candidato")
    .locator("option", { hasText: "knowledge-v44" })
    .waitFor({ state: "attached", timeout: 90000 });
  await page.getByLabel("ID de candidato").fill(`knowledge-ui-candidate-${Date.now().toString(36)}`);
  await page.getByLabel("Autor del candidato").fill("smoke-ui");
  await page.getByLabel("Motivo").fill("Smoke UI de candidate y publicacion.");
  await panel.getByRole("button", { name: "Crear candidato" }).waitFor();
  await panel.getByRole("button", { name: "Revisar publicacion" }).waitFor();
  await panel.getByRole("button", { name: "Publicar candidato" }).waitFor();
} finally {
  await browser.close();
}
