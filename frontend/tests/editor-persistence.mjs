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
  await editorPanel.getByLabel("Objetivo").selectOption("continue");
  await page.getByLabel("Recorrido de escritura").getByText("Borrador").waitFor();
  await page.getByLabel("Recorrido de escritura").getByText("Accion").waitFor();

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
  await resultPanel.getByText("Diagnostico automatico de cambios").waitFor();
  await resultPanel.getByText("Ver cambios en el texto").waitFor();
  await page.getByLabel("Recorrido de escritura").getByText("Hay una version nueva sin aplicar.").waitFor();
  await editorPanel.locator("textarea").first().fill(`${inputText} Cambio manual.`);
  await resultPanel.getByText("Borrador actualizado. Crea una nueva propuesta").waitFor();
  if ((await resultPanel.getByRole("button", { name: "Aceptar propuesta" }).count()) !== 0) {
    throw new Error("Editar el borrador no debe conservar una propuesta anterior.");
  }
  await editorPanel.locator("textarea").first().fill(inputText);

  const regeneratedResponse = page.waitForResponse(
    (response) => {
      const url = new URL(response.url());
      return url.pathname === "/generation" && response.request().method() === "POST";
    },
    { timeout: 90000 },
  );
  await page.getByRole("button", { name: "Crear propuesta" }).click();
  await regeneratedResponse;
  await resultPanel.getByText("Propuesta de continuacion").waitFor();
  await resultPanel.getByText("Diagnostico automatico de cambios").waitFor();
  await resultPanel.getByText("Ver cambios en el texto").waitFor();

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
  await editorPanel.getByLabel("Objetivo").selectOption("rewrite");
  const noChangeGenerationResponse = page.waitForResponse(
    (response) => {
      const url = new URL(response.url());
      return url.pathname === "/generation" && response.request().method() === "POST";
    },
    { timeout: 90000 },
  );
  await page.getByRole("button", { name: "Crear propuesta" }).click();
  await noChangeGenerationResponse;
  await resultPanel.getByText("Sin version nueva").waitFor();
  await resultPanel.getByText("Sin cambios detectados").waitFor();
  await page.getByLabel("Recorrido de escritura").getByText("No hay cambio seguro.").waitFor();
  await page.getByLabel("Recorrido de escritura").getByText("Sin version que aceptar.").waitFor();
  if ((await page.getByLabel("Recorrido de escritura").getByText("Acepta, copia o descarta.").count()) !== 0) {
    throw new Error("Una generacion sin cambios no debe activar el paso de decision.");
  }
  if ((await resultPanel.getByRole("button", { name: "Aceptar propuesta" }).count()) !== 0) {
    throw new Error("Una generacion sin cambios no debe mostrar una accion para usar version.");
  }
  const noChangeRevisionResponse = page.waitForResponse(
    (response) => {
      const url = new URL(response.url());
      return url.pathname === "/revision" && response.request().method() === "POST";
    },
    { timeout: 90000 },
  );
  await resultPanel.getByRole("button", { name: "Leer con fichas" }).click();
  await noChangeRevisionResponse;
  await resultPanel.getByRole("heading", { name: "Lectura con fichas" }).waitFor();
  if ((await resultPanel.getByText("Sin version nueva").count()) !== 0) {
    throw new Error("La lectura con fichas no debe quedar mezclada con el bloque sin cambios.");
  }
  if ((await resultPanel.getByText("Sin salida todavia").count()) !== 0) {
    throw new Error("La lectura con fichas no debe mostrar el estado vacio de salida.");
  }

  const exactSameText = "Texto que vuelve exactamente igual.";
  await page.route("**/generation", async (route) => {
    const body = JSON.parse(route.request().postData() ?? "{}");
    if (body.text === exactSameText) {
      await route.fulfill({
        contentType: "application/json",
        body: JSON.stringify({
          output: exactSameText,
          explanation: "Generacion LLM con gpt-5-mini.",
          used_profile_variables: ["precision_lexica", "densidad_argumental"],
          learning_applied: false,
          provider: "test",
        }),
      });
      return;
    }
    await route.fallback();
  });
  await page.route("**/comparisons", async (route) => {
    const body = JSON.parse(route.request().postData() ?? "{}");
    if (body.original === exactSameText && body.revised === exactSameText) {
      await route.fulfill({
        contentType: "application/json",
        body: JSON.stringify({
          id: "comparison-exact-same-regression",
          modification_score: 165,
          adequacy_score: 931,
          changed_words: 0,
          original_words: 5,
          revised_words: 5,
          summary: "Comparacion simulada erronea.",
          dimensions: { lexico: 165 },
          changes: [],
        }),
      });
      return;
    }
    await route.fallback();
  });
  await editorPanel.locator("textarea").first().fill(exactSameText);
  await editorPanel.getByLabel("Objetivo").selectOption("rewrite");
  const exactSameGenerationResponse = page.waitForResponse(
    (response) => {
      const url = new URL(response.url());
      return url.pathname === "/generation" && response.request().method() === "POST";
    },
    { timeout: 90000 },
  );
  await page.getByRole("button", { name: "Crear propuesta" }).click();
  await exactSameGenerationResponse;
  await resultPanel.getByText("Sin version nueva").waitFor();
  await resultPanel.getByText("Cambios: 0").waitFor();
  await resultPanel.getByText("Adecuacion: 1000").waitFor();
  if ((await resultPanel.getByText("Ver cambios en el texto").count()) !== 0) {
    throw new Error("Una salida identica no debe mostrar comparacion visual de cambios.");
  }
  await resultPanel.getByText("Ver detalles").click();
  await resultPanel.getByText("Aspectos tenidos en cuenta").waitFor();
  await resultPanel.getByText("Precision Lexica").waitFor();
  await resultPanel.getByText("Densidad Argumental").waitFor();
  if ((await resultPanel.getByText("precision_lexica").count()) !== 0) {
    throw new Error("La UI no debe mostrar claves tecnicas de perfil al escritor.");
  }
  if ((await resultPanel.getByText("gpt-5-mini").count()) !== 0) {
    throw new Error("La UI no debe mostrar el modelo tecnico en los detalles de escritura.");
  }
  if ((await resultPanel.getByRole("button", { name: "Aceptar propuesta" }).count()) !== 0) {
    throw new Error("Una salida identica no debe mostrarse como propuesta aunque el comparador falle.");
  }

  await editorPanel.locator("textarea").first().fill(" hola ,mundo. esto funciona ? si ! ");
  await editorPanel.getByLabel("Objetivo").selectOption("correction");
  const correctionResponse = page.waitForResponse(
    (response) => {
      const url = new URL(response.url());
      return url.pathname === "/generation" && response.request().method() === "POST";
    },
    { timeout: 90000 },
  );
  await page.getByRole("button", { name: "Crear propuesta" }).click();
  await correctionResponse;
  await resultPanel.getByText("Propuesta de correccion").waitFor();
  const correctedOutput = await resultPanel.locator("textarea[readonly]").inputValue();
  const normalizedCorrectionOutput = correctedOutput.replace(/\s+/g, " ").trim();
  if (
    !normalizedCorrectionOutput.includes("Hola, mundo.") ||
    !normalizedCorrectionOutput.includes("¿Esto funciona?") ||
    !normalizedCorrectionOutput.includes("¡Sí!")
  ) {
    throw new Error("Corregir sin reescribir no mostro una correccion visible segura.");
  }
  await resultPanel.getByText("Ver cambios en el texto").waitFor();
  await resultPanel.getByRole("button", { name: "Aceptar propuesta" }).waitFor();

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
  await page.getByRole("heading", { name: "Actividad reciente" }).waitFor();
  await page.getByText("Se trabajo un texto").first().waitFor();
  await page.getByText("Se reviso un borrador").first().waitFor();
} finally {
  await browser.close();
}
