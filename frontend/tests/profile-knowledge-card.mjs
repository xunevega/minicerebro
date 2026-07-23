import { chromium } from "playwright";

const frontendUrl = process.env.FRONTEND_URL ?? "http://127.0.0.1:5173";

const browser = await chromium.launch();
const page = await browser.newPage();

try {
  await page.goto(frontendUrl, { waitUntil: "networkidle" });

  const complementoClaim = page.locator(".traceClaim", {
    hasText: "El complemento directo funciona como participante seleccionado por el predicado verbal",
  });
  await complementoClaim.getByRole("button", { name: "Ver ficha" }).click();

  const selectedCard = page.locator(".proposalBox", { hasText: "Ficha seleccionada" });
  await selectedCard.locator("article.knowledgeItem > strong", { hasText: "Complemento directo" }).waitFor();
  await selectedCard.getByRole("button", { name: "Cambiar" }).click();

  await selectedCard.getByLabel("Feedback de usuario").fill("Smoke UI de ficha de usuario.");
  await selectedCard.getByLabel("Mantener").fill("precision, trazabilidad");
  await selectedCard.getByLabel("Cambiar").fill("menos rigidez");
  await selectedCard.getByLabel("Notas").fill("Registro visual sin modificar conocimiento estable.");

  const saveResponse = page.waitForResponse((response) => {
    const url = new URL(response.url());
    return (
      url.pathname === "/profiles/default/knowledge-cards/card-complemento-directo" &&
      response.request().method() === "POST"
    );
  });
  await selectedCard.getByRole("button", { name: "Guardar ficha" }).click();
  await saveResponse;

  await selectedCard.locator(".metric", { hasText: "Estado" }).filter({ hasText: "changed" }).waitFor();
  await selectedCard.getByText("Propuesta de scoring").waitFor();
  await selectedCard.locator(".metric", { hasText: "Ajustes" }).waitFor();
  await selectedCard.getByRole("button", { name: "Aplicar a la puntuacion" }).waitFor();
} finally {
  await browser.close();
}
