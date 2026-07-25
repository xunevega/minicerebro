import { chromium } from "playwright";

const frontendUrl = process.env.FRONTEND_URL ?? "http://127.0.0.1:5173";

const browser = await chromium.launch();
const page = await browser.newPage();

try {
  await page.goto(frontendUrl, { waitUntil: "domcontentloaded" });
  await page.getByRole("button", { name: "Biblioteca" }).click();
  await page.getByRole("button", { name: "Mostrar panel tecnico" }).click();

  const panel = page.locator(".proposalBox", {
    has: page.getByRole("heading", { name: /^Publicacion tecnica$/ }),
  });
  await panel.getByText("Crear candidato congela una version revisable.").waitFor();
  await page.locator(".metric", { hasText: "Base lista" }).filter({ hasText: "Base publicada actual" }).first().waitFor({
    timeout: 90000,
  });

  await page
    .getByLabel("Version base de candidate")
    .locator("option", { hasText: "knowledge-v33" })
    .waitFor({ state: "attached", timeout: 90000 });
  await page.getByLabel("ID de candidate").fill(`knowledge-ui-candidate-${Date.now().toString(36)}`);
  await page.getByLabel("Autor de candidate").fill("smoke-ui");
  await page.getByLabel("Motivo").fill("Smoke UI de candidate y publicacion.");
  await panel.getByRole("button", { name: "Crear candidate" }).waitFor();
  await panel.getByRole("button", { name: "Ver readiness" }).waitFor();
  await panel.getByRole("button", { name: "Publicar candidate" }).waitFor();
} finally {
  await browser.close();
}
