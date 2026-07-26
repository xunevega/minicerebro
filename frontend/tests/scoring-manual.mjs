import { chromium } from "playwright";

const frontendUrl = process.env.FRONTEND_URL ?? "http://127.0.0.1:5173";

const browser = await chromium.launch();
const page = await browser.newPage();

try {
  await page.goto(frontendUrl, { waitUntil: "domcontentloaded" });
  await page.getByRole("button", { name: "Mi criterio" }).click();
  await page.getByRole("button", { name: "Ajustes" }).click();

  await page.getByText("Ajustes de estilo").waitFor();
  await page.getByLabel("Por que cambias este ajuste").fill("Smoke UI de ajustes.");
} finally {
  await browser.close();
}
