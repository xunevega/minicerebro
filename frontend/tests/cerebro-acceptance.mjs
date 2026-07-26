import { chromium } from "playwright";

const frontendUrl = process.env.FRONTEND_URL ?? "http://127.0.0.1:5173";

const browser = await chromium.launch();
const page = await browser.newPage();

try {
  await page.goto(`${frontendUrl}?internal=1`, { waitUntil: "domcontentloaded" });

  await page.getByLabel("Navegacion principal").getByRole("button", { name: "Sistema" }).click();
  await page.getByLabel("Vista").selectOption("__toggle_internal");
  await page.getByLabel("Vista").selectOption("cerebro");
  const cerebroPanel = page.locator(".panel", { hasText: "Revision de cantera" });
  await cerebroPanel.getByText("Revision de cantera").waitFor();
  await cerebroPanel.getByText("Bloqueos antes de reutilizar").waitFor();

  await page.getByLabel("Vista").selectOption("acceptance");
  const acceptancePanel = page.locator(".panel", { hasText: "Aceptacion interna" });
  await acceptancePanel.getByText("Aceptacion interna").waitFor();
} finally {
  await browser.close();
}
