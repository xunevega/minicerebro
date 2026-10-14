import { chromium } from "playwright";

const frontendUrl = process.env.FRONTEND_URL ?? "http://127.0.0.1:5173";

const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1360, height: 900 } });

try {
  await page.goto(`${frontendUrl}/biblioteca`, { waitUntil: "domcontentloaded" });
  await page.getByRole("heading", { name: "Fichas de oficio" }).waitFor();
  if ((await page.getByText("Estado de la base").count()) !== 0) {
    throw new Error("La Biblioteca no debe mostrar la base antigua.");
  }

  await page.getByRole("button", { name: "La lengua como material", exact: true }).click();
  await page.getByPlaceholder("Buscar: dequeísmo, conectores, diálogo…").fill("dequeismo");
  await page.locator(".oficioItem", { hasText: "Dequeísmo" }).click();
  const detail = page.locator(".oficioDetail");
  await detail.getByRole("heading", { name: "Dequeísmo" }).waitFor();
  await detail.getByText("No aplica", { exact: true }).waitFor();
  await detail.getByText("Pienso de que no vendrá.").waitFor();
  await detail.getByText("Diccionario panhispánico de dudas", { exact: false }).waitFor();

  // Las relaciones llevan a la otra ficha.
  await detail.getByRole("button", { name: "Queísmo", exact: true }).click();
  await detail.getByRole("heading", { name: "Queísmo" }).waitFor();

  const feedback = page.waitForResponse(
    (response) => new URL(response.url()).pathname === "/revision/feedback/queismo",
  );
  await detail.getByRole("button", { name: "Me sirve", exact: true }).click();
  if ((await feedback).status() !== 200) throw new Error("No se guardó la postura sobre la ficha.");
  await detail.locator(".statusPill", { hasText: "Te sirve" }).waitFor();

  await page.screenshot({ path: process.env.SCREENSHOT ?? "oficio-library.png", fullPage: false });
  console.log("oficio-library ok");
} finally {
  await browser.close();
}
