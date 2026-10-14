import { chromium } from "playwright";

const frontendUrl = process.env.FRONTEND_URL ?? "http://127.0.0.1:5173";

const browser = await chromium.launch();
const page = await browser.newPage();

try {
  await page.goto(frontendUrl, { waitUntil: "domcontentloaded" });
  await page
    .getByRole("link", { name: "Escribir" })
    .click();
  await page.getByLabel("Vista").selectOption("lab");

  const labPanel = page.locator(".panel", { hasText: "Simulación" });
  await labPanel.locator("textarea").first().fill("Texto base para comparar.");
  await page
    .getByLabel("Texto revisado de laboratorio")
    .fill("Texto base para comparar con mas claridad.");

  const labCompareResponse = page.waitForResponse(
    (response) => {
      const url = new URL(response.url());
      return url.pathname === "/lab/compare" && response.request().method() === "POST";
    },
    { timeout: 90000 },
  );
  await page.getByRole("button", { name: "Comparar sin guardar" }).click();
  await labCompareResponse;

  await page.getByRole("heading", { name: "Comparación temporal" }).waitFor();
  await page.locator(".metric", { hasText: "Modificacion temporal" }).waitFor();
  await page.locator(".metric", { hasText: "Fidelidad temporal" }).waitFor();
  await page.getByText("Cambios temporales").waitFor();
} finally {
  await browser.close();
}
