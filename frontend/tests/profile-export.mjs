import { chromium } from "playwright";

const frontendUrl = process.env.FRONTEND_URL ?? "http://127.0.0.1:5173";

const browser = await chromium.launch();
const page = await browser.newPage();

try {
  await page.goto(frontendUrl, { waitUntil: "domcontentloaded" });
  await page.getByRole("button", { name: "Mi criterio" }).click();
  await page.getByRole("button", { name: "Mi ficha" }).click();

  const exportResponse = page.waitForResponse(
    (response) => {
      const url = new URL(response.url());
      return url.pathname === "/profiles/default/export" && response.request().method() === "GET";
    },
    { timeout: 90000 },
  );
  await page.getByRole("button", { name: "Ver ficha completa" }).click();
  await exportResponse;

  const exportBox = page.locator(".proposalBox", { hasText: "Ficha completa" });
  await exportBox.getByText("profile-export-v1").waitFor();
  await exportBox.locator(".metric", { hasText: "Contextos" }).waitFor();
  await exportBox.locator(".metric", { hasText: "Gustos" }).waitFor();
  await exportBox
    .getByText("La exportacion del perfil no incluye ni modifica la base de conocimiento.")
    .waitFor();
  await exportBox.getByText("Contextos guardados").waitFor();
} finally {
  await browser.close();
}
