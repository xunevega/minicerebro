import { chromium } from "playwright";

const frontendUrl = process.env.FRONTEND_URL ?? "http://127.0.0.1:5173";

const browser = await chromium.launch();
const page = await browser.newPage();

try {
  await page.goto(frontendUrl, { waitUntil: "networkidle" });
  await page.getByRole("button", { name: "Lo que sabe" }).click();

  const exportResponse = page.waitForResponse((response) => {
    const url = new URL(response.url());
    return url.pathname === "/profiles/default/export" && response.request().method() === "GET";
  });
  await page.getByRole("button", { name: "Ver export del perfil" }).click();
  await exportResponse;

  const exportBox = page.locator(".proposalBox", { hasText: "Export del perfil" });
  await exportBox.getByText("profile-export-v1").waitFor();
  await exportBox.locator(".metric", { hasText: "Contextos" }).waitFor();
  await exportBox.locator(".metric", { hasText: "Preferencias" }).waitFor();
  await exportBox
    .getByText("La exportacion del perfil no incluye ni modifica la base de conocimiento.")
    .waitFor();
  await exportBox.getByText("Contextos exportados").waitFor();
} finally {
  await browser.close();
}
