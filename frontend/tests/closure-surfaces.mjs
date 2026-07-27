import { chromium } from "playwright";

const frontendUrl = process.env.FRONTEND_URL ?? "http://127.0.0.1:5173";

const browser = await chromium.launch();
const page = await browser.newPage();

try {
  await page.goto(`${frontendUrl}?internal=1`, { waitUntil: "domcontentloaded" });

  await page.getByLabel("Navegacion principal").getByRole("button", { name: "Sistema" }).click();
  await page.getByLabel("Vista").selectOption("persistence");
  const persistencePanel = page.locator(".panel", { hasText: "Datos guardados" });
  await persistencePanel.getByRole("heading", { name: "Textos" }).waitFor();
  await page.waitForFunction(
    () =>
      document.body.textContent?.includes("Todavia no hay textos generados en este contexto.") ||
      document.querySelector(".auditItem") !== null,
  );

  await page.getByLabel("Vista").selectOption("__toggle_internal");
  await page.getByLabel("Vista").selectOption("closure");
  const closurePanel = page.locator(".panel", { hasText: "Condiciones de cierre" });
  await closurePanel.getByRole("heading", { name: "Cierre interno" }).waitFor();
  await closurePanel.getByText("Limites 21/22").waitFor();
  await closurePanel.getByText("Resultado esperado").waitFor();

  await page.getByLabel("Vista").selectOption("roadmap");
  const roadmapPanel = page.locator(".panel", { hasText: "Plan interno" });
  await roadmapPanel.getByText("Observabilidad").waitFor();

  await page.getByLabel("Vista").selectOption("screens");
  const screensPanel = page.locator(".panel", { hasText: "Pantallas internas" });
  await screensPanel.getByText("Feedback pendiente").waitFor();
  await page.waitForFunction(
    () =>
      document.body.textContent?.includes("Sin propuestas pendientes.") ||
      document.body.textContent?.includes("variables"),
  );
} finally {
  await browser.close();
}
