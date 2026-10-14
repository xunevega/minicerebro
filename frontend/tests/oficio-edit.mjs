import { chromium } from "playwright";

// Requiere un backend sin autenticación (o con sesión de administrador) y, para el
// bloque de propuestas, una propuesta pendiente sobre «Queísmo» sembrada antes.
const frontendUrl = process.env.FRONTEND_URL ?? "http://127.0.0.1:5173";

const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1360, height: 900 } });

try {
  await page.goto(`${frontendUrl}/biblioteca`, { waitUntil: "domcontentloaded" });
  await page.getByRole("heading", { name: "Fichas de oficio" }).waitFor();
  await page.getByPlaceholder("Buscar: dequeísmo, conectores, diálogo…").fill("dequeismo");
  await page.locator(".oficioItem", { hasText: "Dequeísmo" }).click();
  const detail = page.locator(".oficioDetail");
  await detail.getByRole("heading", { name: "Dequeísmo" }).waitFor();

  // Una edición que rompe la señal no se guarda y explica por qué.
  await detail.getByRole("button", { name: "Editar", exact: true }).click();
  const editor = page.locator(".oficioEditor");
  await editor.getByLabel("Ejemplo 1, mal").fill("Algo que no tiene nada que ver.");
  await editor.getByRole("button", { name: "Comprobar" }).click();
  await editor.locator(".oficioProblems", { hasText: "ejemplo malo" }).waitFor();
  await editor.getByRole("button", { name: "Cancelar" }).click();

  // Una edición válida se guarda con motivo y queda en el historial.
  await detail.getByRole("button", { name: "Editar", exact: true }).click();
  const noAplica = editor.getByLabel("No aplica");
  await noAplica.fill(`${await noAplica.inputValue()} Tampoco en citas literales.`);
  await editor.getByLabel("Motivo del cambio").fill("Excluir las citas literales");
  await editor.getByRole("button", { name: "Guardar cambios" }).click();
  await page.locator(".successText", { hasText: "guardada" }).waitFor();
  await detail.getByText("Tampoco en citas literales.", { exact: false }).waitFor();
  await detail.getByText("versión 1", { exact: false }).waitFor();

  await detail.getByRole("button", { name: "Historial" }).click();
  await page.getByText("Excluir las citas literales").waitFor();
  await page.getByRole("button", { name: "Restaurar" }).click();
  await page.locator(".successText", { hasText: "Restaurada la versión 0" }).waitFor();
  await page.getByRole("button", { name: "Volver a la ficha" }).click();
  if ((await detail.getByText("Tampoco en citas literales.", { exact: false }).count()) !== 0) {
    throw new Error("Restaurar no devolvió la versión original.");
  }

  // Propuestas: se ve el cambio campo a campo y se puede aceptar.
  await page.getByRole("button", { name: /^Propuestas/ }).click();
  const proposal = page.locator(".oficioProposal", { hasText: "Queísmo" });
  await proposal.waitFor();
  await proposal.locator(".oficioDiffAfter", { hasText: "Tampoco en titulares" }).waitFor();
  await page.screenshot({ path: process.env.SCREENSHOT ?? "oficio-edit.png", fullPage: false });
  await proposal.getByRole("button", { name: "Aceptar", exact: true }).click();
  await page.locator(".successText", { hasText: "Propuesta aceptada" }).waitFor();
  await page.getByText("No hay propuestas pendientes.").waitFor();

  console.log("oficio-edit ok");
} finally {
  await browser.close();
}
