import { chromium } from "playwright";

const frontendUrl = process.env.FRONTEND_URL ?? "http://127.0.0.1:5173";

const browser = await chromium.launch();
const page = await browser.newPage();

try {
  await page.goto(frontendUrl, { waitUntil: "domcontentloaded" });
  await page.getByRole("button", { name: "Aprender de mi" }).click();
  await page.getByRole("button", { name: "Ficha" }).click();

  await page.getByRole("heading", { name: "Ficha personal" }).waitFor();
  await page.getByText("Gustos, ajustes y ficha personal.").waitFor();
} finally {
  await browser.close();
}
