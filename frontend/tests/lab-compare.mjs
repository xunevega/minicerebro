import { chromium } from "playwright";

const frontendUrl = process.env.FRONTEND_URL ?? "http://127.0.0.1:5173";

const browser = await chromium.launch();
const page = await browser.newPage();

try {
  await page.goto(frontendUrl, { waitUntil: "networkidle" });
  await page.getByRole("button", { name: "Laboratorio" }).click();

  const labPanel = page.locator(".panel", { hasText: "Simulacion" });
  await labPanel.locator("textarea").first().fill("Texto base para comparar.");
  await page
    .getByLabel("Texto revisado de laboratorio")
    .fill("Texto base para comparar con mas claridad.");

  const labCompareResponse = page.waitForResponse((response) => {
    const url = new URL(response.url());
    return url.pathname === "/lab/compare" && response.request().method() === "POST";
  });
  await page.getByRole("button", { name: "Comparar sin guardar" }).click();
  await labCompareResponse;

  await page.getByRole("heading", { name: "Comparacion temporal" }).waitFor();
  await page.locator(".metric", { hasText: "Modificacion temporal" }).waitFor();
  await page.locator(".metric", { hasText: "Adecuacion temporal" }).waitFor();
  await page.getByText("Cambios temporales").waitFor();
} finally {
  await browser.close();
}
