import { chromium } from "playwright";

const frontendUrl = process.env.FRONTEND_URL ?? "http://127.0.0.1:5173";
const apiBase = process.env.VITE_API_BASE ?? "http://127.0.0.1:8000";

const browser = await chromium.launch();
const page = await browser.newPage();

try {
  await page.goto(frontendUrl, { waitUntil: "domcontentloaded" });
  if ((await page.getByLabel("Navegacion principal").getByRole("button", { name: "Sistema" }).count()) !== 0) {
    throw new Error("La navegacion normal muestra la seccion tecnica Sistema.");
  }
  await page
    .getByRole("button", {
      name: "Escribir",
      description: "Redacta, corrige y compara sin perder tu criterio.",
    })
    .click();

  const editorPanel = page.locator(".panel", { hasText: "Borrador" });
  const inputText = `Smoke editor persistencia ${Date.now()}.  Frase para guardar.`;
  await editorPanel.locator("textarea").first().fill(inputText);
  await editorPanel.getByLabel("Que quieres hacer").selectOption("continue");
  await page.getByLabel("Recorrido de escritura").getByText("Borrador").waitFor();
  await page.getByLabel("Recorrido de escritura").getByText("Propuesta").waitFor();

  const generationResponse = page.waitForResponse(
    (response) => {
      const url = new URL(response.url());
      return url.pathname === "/generation" && response.request().method() === "POST";
    },
    { timeout: 90000 },
  );
  await page.getByRole("button", { name: "Crear propuesta" }).click();
  await generationResponse;

  const resultPanel = page.locator(".inspector", { hasText: "Salida" });
  await resultPanel.getByText("Propuesta de continuacion").waitFor();
  await resultPanel.getByText("Comparacion automatica").waitFor();
  await page.getByLabel("Recorrido de escritura").getByText("Hay una version nueva sin aplicar.").waitFor();

  const revisionResponse = page.waitForResponse(
    (response) => {
      const url = new URL(response.url());
      return url.pathname === "/revision" && response.request().method() === "POST";
    },
    { timeout: 90000 },
  );
  await page.getByRole("button", { name: "Leer con fichas" }).click();
  await revisionResponse;
  await resultPanel.getByText("Lectura con fichas").waitFor();
  await resultPanel.getByText("Diagnostico de reescritura").waitFor();
  await resultPanel.getByText("Por que aplica").first().waitFor();
  await resultPanel.getByText("Que haria").first().waitFor();
  await resultPanel.getByText("Como probarlo").first().waitFor();
  await resultPanel.getByText("Senales miradas").first().waitFor();
  await resultPanel.getByText("Ficha 1 de").waitFor();
  if ((await resultPanel.locator(".revisionStepCard").count()) !== 1) {
    throw new Error("La lectura debe mostrar una sola ficha pendiente cada vez.");
  }
  await resultPanel.getByRole("button", { name: "No va por ahi" }).first().waitFor();
  const feedbackResponse = page.waitForResponse(
    (response) => {
      const url = new URL(response.url());
      return url.pathname.startsWith("/revision/feedback/") && response.request().method() === "POST";
    },
    { timeout: 90000 },
  );
  await resultPanel.getByRole("button", { name: "Me sirve" }).first().click();
  await feedbackResponse;
  await resultPanel.getByText("ficha decidida").first().waitFor();
  await resultPanel.getByText("Ficha 2 de").waitFor();
  if ((await resultPanel.locator(".revisionStepCard").count()) !== 1) {
    throw new Error("Despues de decidir una ficha solo debe verse la siguiente.");
  }
  await page.getByLabel("Recorrido de escritura").getByText("criterio guardado").first().waitFor();
  if ((await resultPanel.getByRole("button", { name: "Aplicar ajuste" }).count()) !== 0) {
    throw new Error("La lectura muestra acciones tecnicas de scoring.");
  }

  const output = await resultPanel.locator("textarea[readonly]").inputValue();
  if (!output || output.length < 10) {
    throw new Error("La generacion no devolvio un texto persistible.");
  }
  await resultPanel.getByRole("button", { name: "Aceptar propuesta" }).click();
  const updatedDraft = await editorPanel.locator("textarea").first().inputValue();
  if (updatedDraft !== output) {
    throw new Error("Aceptar propuesta no sustituyo el borrador por la propuesta.");
  }
  await editorPanel.getByRole("button", { name: "Borrar texto" }).click();
  if ((await editorPanel.locator("textarea").first().inputValue()) !== "") {
    throw new Error("Borrar texto no dejo el borrador vacio.");
  }
  await page.getByLabel("Recorrido de escritura").getByText("Escribe o pega un texto.").waitFor();

  const cleanText = "Texto limpio para revisar.";
  await editorPanel.locator("textarea").first().fill(cleanText);
  await editorPanel.getByLabel("Que quieres hacer").selectOption("rewrite");
  const noChangeGenerationResponse = page.waitForResponse(
    (response) => {
      const url = new URL(response.url());
      return url.pathname === "/generation" && response.request().method() === "POST";
    },
    { timeout: 90000 },
  );
  await page.getByRole("button", { name: "Crear propuesta" }).click();
  await noChangeGenerationResponse;
  await resultPanel.getByText("No he encontrado una reescritura segura").waitFor();
  await resultPanel.getByText("Sin cambios detectados").waitFor();
  if ((await resultPanel.getByRole("button", { name: "Aceptar propuesta" }).count()) !== 0) {
    throw new Error("Una generacion sin cambios no debe mostrar Aceptar propuesta.");
  }
  await resultPanel.getByRole("button", { name: "Probar otra revision" }).click();
  await resultPanel.getByText("Propuesta descartada. El borrador no ha cambiado.").waitFor();

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

  await page.getByLabel("Navegacion principal").getByRole("button", { name: "Historial" }).click();
  await page.getByRole("heading", { name: "Actividad de escritura" }).waitFor();
  await page.getByText("Se trabajo un texto").first().waitFor();
  await page.getByText("Se reviso un borrador").first().waitFor();
} finally {
  await browser.close();
}
