import { chromium } from "playwright";

const frontendUrl = process.env.FRONTEND_URL ?? "http://127.0.0.1:5173";

const browser = await chromium.launch();
const page = await browser.newPage();

try {
  await page.goto(frontendUrl, { waitUntil: "domcontentloaded" });

  await page.getByLabel("Navegacion principal").getByRole("button", { name: "Sistema" }).click();
  await page.getByRole("button", { name: "Guardado" }).click();
  const persistencePanel = page.locator(".panel", { hasText: "Datos guardados" });
  await persistencePanel.getByRole("heading", { name: "Textos" }).waitFor();
  await persistencePanel.getByText("Todavia no hay textos generados en este contexto.").waitFor();

  await page.getByRole("button", { name: "Mostrar tecnico" }).click();
  await page.getByRole("button", { name: "Cierre" }).click();
  const closurePanel = page.locator(".panel", { hasText: "Condiciones de cierre" });
  await closurePanel.getByRole("heading", { name: "Cierre interno" }).waitFor();
  await closurePanel.getByText("Limites 21/22").waitFor();
  await closurePanel.getByText("Resultado esperado").waitFor();

  await page.getByRole("button", { name: "Plan" }).click();
  const roadmapPanel = page.locator(".panel", { hasText: "Plan interno" });
  await roadmapPanel.getByText("Observabilidad").waitFor();

  await page.getByRole("button", { name: "Pantallas" }).click();
  const screensPanel = page.locator(".panel", { hasText: "Pantallas internas" });
  await screensPanel.getByText("Feedback pendiente").waitFor();
  await screensPanel.getByText("Sin propuestas pendientes.").waitFor();
} finally {
  await browser.close();
}
