import { chromium } from "playwright";

const frontendUrl = process.env.FRONTEND_URL ?? "http://127.0.0.1:5173";

const browser = await chromium.launch();
const page = await browser.newPage();

try {
  await page.goto(frontendUrl, { waitUntil: "domcontentloaded" });
  await page.getByRole("button", { name: "Mi perfil" }).click();
  await page.getByRole("button", { name: "Ficha usuario" }).click();

  await page.getByRole("heading", { name: "Ficha usuario" }).waitFor();
  await page.getByText("Preferencias, puntuacion y ficha personal.").waitFor();
} finally {
  await browser.close();
}
