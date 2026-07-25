import { chromium } from "playwright";

const frontendUrl = process.env.FRONTEND_URL ?? "http://127.0.0.1:5173";

const browser = await chromium.launch();
const page = await browser.newPage();

try {
  await page.goto(frontendUrl, { waitUntil: "domcontentloaded" });

  await page.getByLabel("Navegacion principal").getByRole("button", { name: "Historial" }).click();
  await page.getByRole("button", { name: "Mostrar tecnico" }).click();
  await page.getByRole("button", { name: "Cerebro" }).click();
  const cerebroPanel = page.locator(".panel", { hasText: "Revision de cantera" });
  await cerebroPanel.getByText("Revision de cantera").waitFor();
  await cerebroPanel.getByText("Bloqueos antes de reutilizar").waitFor();

  await page.getByRole("button", { name: "Aceptacion" }).click();
  const acceptancePanel = page.locator(".panel", { hasText: "Aceptacion interna" });
  await acceptancePanel.getByText("Aceptacion interna").waitFor();
} finally {
  await browser.close();
}
