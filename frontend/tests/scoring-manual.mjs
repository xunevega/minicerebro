import { chromium } from "playwright";

const frontendUrl = process.env.FRONTEND_URL ?? "http://127.0.0.1:5173";

const browser = await chromium.launch();
const page = await browser.newPage();

try {
  await page.goto(frontendUrl, { waitUntil: "domcontentloaded" });
  await page.getByRole("button", { name: "Mi perfil" }).click();
  await page.getByRole("button", { name: "Puntuacion" }).click();

  await page.getByText("Variables").waitFor();
  await page.getByLabel("Por que cambias la puntuacion").fill("Smoke UI de puntuacion.");
} finally {
  await browser.close();
}
