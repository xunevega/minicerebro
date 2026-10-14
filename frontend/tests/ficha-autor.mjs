import { chromium } from "playwright";

const frontendUrl = process.env.FRONTEND_URL ?? "http://127.0.0.1:5173";
const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1360, height: 1500 } });

try {
  await page.goto(frontendUrl, { waitUntil: "domcontentloaded" });
  await page.getByRole("link", { name: /Mi criterio/ }).first().click();
  const panel = page.locator(".fichaAutor");
  await panel.getByRole("heading", { name: "Tu ficha de autor" }).waitFor();
  const stamp = Date.now();
  await panel.getByLabel("Cómo escribes").fill(`Ensayo de opinión con frases largas ${stamp}.`);
  await panel.getByLabel("Evitas (una cosa por línea)").fill("Adverbios en -mente\nTópicos de cierre");
  await panel.getByRole("button", { name: "Guardar ficha" }).click();
  await panel.locator(".successText", { hasText: "Ficha guardada" }).waitFor();
  await panel.getByText("Ver lo que recibe el modelo").click();
  await panel.locator(".fichaAutorPrompt", { hasText: `frases largas ${stamp}` }).waitFor();
  await panel.locator(".fichaAutorPrompt", { hasText: "Adverbios en -mente" }).waitFor();
  await panel.getByRole("button", { name: "Historial" }).click();
  await panel.locator(".oficioVersions .statusPill", { hasText: "Vigente" }).waitFor();
  await page.screenshot({ path: process.env.SCREENSHOT ?? "ficha-autor.png", fullPage: false });
  console.log("ficha-autor ok");
} finally {
  await browser.close();
}
