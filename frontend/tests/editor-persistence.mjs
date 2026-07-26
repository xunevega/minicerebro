import { chromium } from "playwright";

const frontendUrl = process.env.FRONTEND_URL ?? "http://127.0.0.1:5173";
const apiBase = process.env.VITE_API_BASE ?? "http://127.0.0.1:8000";

const browser = await chromium.launch();
const page = await browser.newPage();

try {
  await page.goto(frontendUrl, { waitUntil: "domcontentloaded" });
  await page
    .getByRole("button", {
      name: "Escribir",
      description: "Redacta, corrige y compara sin perder tu criterio.",
    })
    .click();

  const editorPanel = page.locator(".panel", { hasText: "Borrador" });
  const inputText = `Smoke editor persistencia ${Date.now()}. Frase para guardar.`;
  await editorPanel.locator("textarea").first().fill(inputText);

  const generationResponse = page.waitForResponse(
    (response) => {
      const url = new URL(response.url());
      return url.pathname === "/generation" && response.request().method() === "POST";
    },
    { timeout: 90000 },
  );
  await page.getByRole("button", { name: "Aplicar reescribir" }).click();
  await generationResponse;

  const resultPanel = page.locator(".inspector", { hasText: "Resultado" });
  await resultPanel.getByText("deterministic").waitFor();

  const revisionResponse = page.waitForResponse(
    (response) => {
      const url = new URL(response.url());
      return url.pathname === "/revision" && response.request().method() === "POST";
    },
    { timeout: 90000 },
  );
  await page.getByRole("button", { name: "Revisar con fichas" }).click();
  await revisionResponse;
  await resultPanel.getByText("Revision con fichas").waitFor();
  await resultPanel.getByText("Diagnostico de reescritura").waitFor();
  const feedbackResponse = page.waitForResponse(
    (response) => {
      const url = new URL(response.url());
      return url.pathname.startsWith("/revision/feedback/") && response.request().method() === "POST";
    },
    { timeout: 90000 },
  );
  await resultPanel.getByRole("button", { name: "Me sirve" }).first().click();
  await feedbackResponse;
  await resultPanel.getByText("Guardado en ficha").first().waitFor();
  const scoreApplyResponse = page.waitForResponse(
    (response) => {
      const url = new URL(response.url());
      return url.pathname.includes("/score-proposal/apply") && response.request().method() === "POST";
    },
    { timeout: 90000 },
  );
  await resultPanel.getByRole("button", { name: "Aplicar ajuste" }).first().click();
  await scoreApplyResponse;
  await resultPanel.getByText("Scoring actualizado").first().waitFor();

  const output = await resultPanel.locator("textarea[readonly]").inputValue();
  if (!output || output.length < 10) {
    throw new Error("La generacion no devolvio un texto persistible.");
  }
  await resultPanel.getByRole("button", { name: "Usar este texto" }).click();
  const updatedDraft = await editorPanel.locator("textarea").first().inputValue();
  if (updatedDraft !== output) {
    throw new Error("Usar este texto no sustituyo el borrador por la propuesta.");
  }
  await resultPanel.getByRole("button", { name: "Comparar con original" }).click();
  const comparePanel = page.locator(".panel", { hasText: "Textos" });
  await comparePanel.waitFor();
  const compareTextareas = comparePanel.locator("textarea");
  if ((await compareTextareas.nth(0).inputValue()) !== inputText) {
    throw new Error("El comparador no conserva el texto original previo a la propuesta.");
  }
  if ((await compareTextareas.nth(1).inputValue()) !== output) {
    throw new Error("El comparador no recibio el texto propuesto.");
  }
  await page.locator(".subnav").getByRole("button", { name: "Escribir" }).click();

  const textsResponse = await page.request.get(`${apiBase}/texts?context=general`, {
    timeout: 90000,
  });
  if (!textsResponse.ok()) {
    throw new Error(`No se pudieron leer los textos persistidos: ${textsResponse.status()}`);
  }
  const texts = await textsResponse.json();
  if (!texts.some((text) => text.output_text === output)) {
    throw new Error("La generacion no quedo persistida en /texts.");
  }
} finally {
  await browser.close();
}
