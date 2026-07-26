import { chromium } from "playwright";

const frontendUrl = process.env.FRONTEND_URL ?? "http://127.0.0.1:5173";
const emptyQuery = "zzzinexistente";
const queryTimeout = 180000;

const browser = await chromium.launch();
const page = await browser.newPage();

try {
  await page.goto(frontendUrl, { waitUntil: "domcontentloaded" });
  await page.getByRole("button", { name: "Biblioteca" }).click();
  await page.getByLabel("Vista").selectOption("latest");
  await page.locator(".metric", { hasText: "Base lista" }).filter({ hasText: "Base publicada actual" }).first().waitFor({
    timeout: 90000,
  });
  await page.locator(".metric", { hasText: "Por revisar" }).first().waitFor({ timeout: 90000 });
  const libraryPanel = page.locator(".proposalBox", { hasText: "Estanterias" });
  await libraryPanel.getByText("Orden bibliotecario").waitFor();
  await libraryPanel.locator(".statusPill", { hasText: "187 fichas" }).waitFor({ timeout: 90000 });
  await libraryPanel.locator(".libraryShelf.active", { hasText: "Todo" }).waitFor();
  await libraryPanel.locator(".libraryCard").first().waitFor();
  await libraryPanel.getByText("uso:").first().waitFor();
  await libraryPanel.getByText("nivel:").first().waitFor();
  await libraryPanel.getByRole("button", { name: /Estilo/ }).click();
  await libraryPanel.locator(".libraryShelf.active", { hasText: "Estilo" }).waitFor();
  await libraryPanel.locator(".libraryCard").first().waitFor();
  await libraryPanel.getByText(/uso: /).first().waitFor();
  await libraryPanel.getByText(/nivel: /).first().waitFor();
  const gymPanel = page.locator(".proposalBox", { hasText: "Calidad de la base" });
  await gymPanel.locator(".statusPill", { hasText: "sano" }).first().waitFor({ timeout: 90000 });
  await gymPanel.locator(".metric", { hasText: "Fichas" }).filter({ hasText: "187" }).waitFor({
    timeout: 90000,
  });
  await gymPanel.locator("strong", { hasText: /^Precision$/ }).waitFor();
  await gymPanel.locator("strong", { hasText: /^Trazabilidad$/ }).waitFor();
  await page.getByRole("button", { name: "Mostrar panel tecnico" }).click();
  await page.getByRole("heading", { name: "Limites actuales" }).waitFor();
  const versionPanel = page.locator(".proposalBox", { hasText: "Versiones de la base" });
  await versionPanel.locator(".versionItem", { hasText: "knowledge-v40" }).locator(".metric", { hasText: "Fuentes" }).filter({ hasText: "26" }).waitFor();
  await versionPanel.locator(".versionItem", { hasText: "knowledge-v40" }).getByText("0 fuentes").waitFor();
  await versionPanel.locator(".versionItem", { hasText: "knowledge-v40" }).getByText("+5 nodos").waitFor();
  await versionPanel.locator(".versionItem", { hasText: "knowledge-v0" }).getByText("base congelada").waitFor();
  const sourceExplorerPanel = page.locator(".proposalBox", {
    has: page.getByRole("heading", { name: /^Fuentes$/ }),
  });
  await sourceExplorerPanel.getByText("Publicadas · 26").waitFor();
  await sourceExplorerPanel.getByText("Ingeridas sin publicar · 0").waitFor();
  await sourceExplorerPanel.getByText("Disponibles sin ingerir · 0").waitFor();
  await sourceExplorerPanel.getByText("Registradas pendientes · 0").waitFor();
  await sourceExplorerPanel.locator(".sourceMiniCard", { hasText: "Ortografia de la lengua espanola" }).getByText("available · publicada").waitFor();
  await sourceExplorerPanel.locator(".sourceMiniCard", { hasText: "Glosario de terminos gramaticales" }).getByText("available · publicada").waitFor();
  await sourceExplorerPanel.locator(".sourceMiniCard", { hasText: "El arte de escribir bien en espanol" }).getByText("available · publicada").waitFor();
  await sourceExplorerPanel.locator(".sourceMiniCard", { hasText: "Ortografia y ortotipografia del espanol actual" }).getByText("available · publicada").waitFor();
  await sourceExplorerPanel.locator(".sourceMiniCard", { hasText: "Como se comenta un texto literario" }).getByText("available · publicada").waitFor();
  await sourceExplorerPanel
    .locator(".sourceMiniCard", { has: page.locator("strong", { hasText: /^Retorica$/ }) })
    .getByText("available · publicada")
    .waitFor();
  await sourceExplorerPanel
    .locator(".sourceMiniCard", { has: page.locator("strong", { hasText: /^Institutio oratoria$/ }) })
    .getByText("available · publicada")
    .waitFor();
  await sourceExplorerPanel
    .locator(".sourceMiniCard", { has: page.locator("strong", { hasText: /^Como hablar bien en publico e influir en los hombres de negocios$/ }) })
    .getByText("available · publicada")
    .waitFor();
  await sourceExplorerPanel
    .locator(".sourceMiniCard", { has: page.locator("strong", { hasText: /^Poetica$/ }) })
    .getByText("available · publicada")
    .waitFor();
  await sourceExplorerPanel
    .locator(".sourceMiniCard", { has: page.locator("strong", { hasText: /^Discurso del relato$/ }) })
    .getByText("available · publicada")
    .waitFor();
  await sourceExplorerPanel
    .locator(".sourceMiniCard", { has: page.locator("strong", { hasText: /^Teoria de la literatura$/ }) })
    .getByText("available · publicada")
    .waitFor();
  await sourceExplorerPanel
    .locator(".sourceMiniCard", { has: page.locator("strong", { hasText: /^Curso de linguistica general$/ }) })
    .getByText("available · publicada")
    .waitFor();
  await sourceExplorerPanel
    .locator(".sourceMiniCard", { has: page.locator("strong", { hasText: /^CORPES XXI$/ }) })
    .getByText("available · publicada")
    .waitFor();
  await sourceExplorerPanel
    .locator(".sourceMiniCard", { has: page.locator("strong", { hasText: /^Aspectos de la teoria de la sintaxis$/ }) })
    .getByText("available · publicada")
    .waitFor();
  await sourceExplorerPanel
    .locator(".sourceMiniCard", { has: page.locator("strong", { hasText: /^The Elements of Style$/ }) })
    .getByText("available · publicada")
    .waitFor();
  await sourceExplorerPanel
    .locator(".sourceMiniCard", { has: page.locator("strong", { hasText: /^On Writing Well$/ }) })
    .getByText("available · publicada")
    .waitFor();
  await sourceExplorerPanel
    .locator(".sourceMiniCard", { has: page.locator("strong", { hasText: /^Diccionario de sinonimos y antonimos$/ }) })
    .getByText("available · publicada")
    .waitFor();
  await sourceExplorerPanel
    .locator(".sourceMiniCard", { has: page.locator("strong", { hasText: /^Diccionario ideologico de la lengua espanola$/ }) })
    .getByText("available · publicada")
    .waitFor();
  await sourceExplorerPanel
    .locator(".sourceMiniCard", { has: page.locator("strong", { hasText: /^La cocina de la escritura$/ }) })
    .getByText("available · publicada")
    .waitFor();
  const ingestionPanel = page.locator(".proposalBox", { hasText: "Estado de fuentes" });
  await ingestionPanel.locator(".metric", { hasText: "Publicadas" }).filter({ hasText: "26" }).waitFor();
  await ingestionPanel.locator(".metric", { hasText: "Ingeridas" }).filter({ hasText: "26" }).waitFor();
  await ingestionPanel.locator(".metric", { hasText: "Pendientes" }).filter({ hasText: "0" }).waitFor();
  await ingestionPanel.getByText("publicada: 26").waitFor();
  await ingestionPanel.locator(".ingestionItem", { hasText: "Ortografia de la lengua espanola" }).getByText("publicada").waitFor();
  await ingestionPanel.locator(".ingestionItem", { hasText: "Glosario de terminos gramaticales" }).getByText("publicada").waitFor();
  await ingestionPanel.locator(".ingestionItem", { hasText: "El arte de escribir bien en espanol" }).getByText("publicada").waitFor();
  await ingestionPanel.locator(".ingestionItem", { hasText: "Ortografia y ortotipografia del espanol actual" }).getByText("publicada").waitFor();
  await ingestionPanel.locator(".ingestionItem", { hasText: "Como se comenta un texto literario" }).getByText("publicada").waitFor();
  await ingestionPanel
    .locator(".ingestionItem", { has: page.locator("strong", { hasText: /^Retorica$/ }) })
    .getByText("publicada")
    .waitFor();
  await ingestionPanel
    .locator(".ingestionItem", { has: page.locator("strong", { hasText: /^Institutio oratoria$/ }) })
    .getByText("publicada")
    .waitFor();
  await ingestionPanel
    .locator(".ingestionItem", { has: page.locator("strong", { hasText: /^Como hablar bien en publico e influir en los hombres de negocios$/ }) })
    .getByText("publicada")
    .waitFor();
  await ingestionPanel
    .locator(".ingestionItem", { has: page.locator("strong", { hasText: /^Poetica$/ }) })
    .getByText("publicada")
    .waitFor();
  await ingestionPanel
    .locator(".ingestionItem", { has: page.locator("strong", { hasText: /^Discurso del relato$/ }) })
    .getByText("publicada")
    .waitFor();
  await ingestionPanel
    .locator(".ingestionItem", { has: page.locator("strong", { hasText: /^Teoria de la literatura$/ }) })
    .getByText("publicada")
    .waitFor();
  await ingestionPanel
    .locator(".ingestionItem", { has: page.locator("strong", { hasText: /^Curso de linguistica general$/ }) })
    .getByText("publicada")
    .waitFor();
  await ingestionPanel
    .locator(".ingestionItem", { has: page.locator("strong", { hasText: /^CORPES XXI$/ }) })
    .getByText("publicada")
    .waitFor();
  await ingestionPanel
    .locator(".ingestionItem", { has: page.locator("strong", { hasText: /^Aspectos de la teoria de la sintaxis$/ }) })
    .getByText("publicada")
    .waitFor();
  await ingestionPanel
    .locator(".ingestionItem", { has: page.locator("strong", { hasText: /^The Elements of Style$/ }) })
    .getByText("publicada")
    .waitFor();
  await ingestionPanel
    .locator(".ingestionItem", { has: page.locator("strong", { hasText: /^On Writing Well$/ }) })
    .getByText("publicada")
    .waitFor();
  await ingestionPanel
    .locator(".ingestionItem", { has: page.locator("strong", { hasText: /^Diccionario de sinonimos y antonimos$/ }) })
    .getByText("publicada")
    .waitFor();
  await ingestionPanel
    .locator(".ingestionItem", { has: page.locator("strong", { hasText: /^Diccionario ideologico de la lengua espanola$/ }) })
    .getByText("publicada")
    .waitFor();
  const pipelinePanel = page.locator(".proposalBox", { hasText: "Recorrido de fuentes" });
  await pipelinePanel.locator(".pipelineCard", { hasText: "Glosario de terminos gramaticales" }).getByText("Fuente").waitFor();
  await pipelinePanel.locator(".pipelineCard", { hasText: "Glosario de terminos gramaticales" }).getByText("ExtractionRun").waitFor();
  await pipelinePanel.locator(".pipelineCard", { hasText: "Glosario de terminos gramaticales" }).getByText("Publicacion").waitFor();
  const explorationPanel = page.locator(".proposalBox", { hasText: "Recorrido completo" });
  await explorationPanel.getByText("Trazabilidad").waitFor();
  await explorationPanel.locator(".metric", { hasText: "Fuentes" }).filter({ hasText: "26" }).waitFor({
    timeout: 90000,
  });
  await explorationPanel.locator(".metric", { hasText: "Nodos" }).filter({ hasText: "189" }).waitFor();
  await explorationPanel.locator(".metric", { hasText: "Evidencias" }).filter({ hasText: "187" }).waitFor();
  await explorationPanel.locator(".pipelineStep", { hasText: /^Fuente$/ }).first().waitFor();
  await explorationPanel.locator(".pipelineStep", { hasText: /^Publicacion$/ }).first().waitFor();
  const complementoClaim = explorationPanel.locator(".traceClaim", {
    hasText: "El complemento directo funciona como participante seleccionado por el predicado verbal",
  });
  await complementoClaim.getByRole("button", { name: "Ver ficha" }).click();
  const selectedCard = page.locator(".proposalBox", {
    has: page.getByRole("heading", { name: /^Ficha editorial$/ }),
  });
  await selectedCard.locator("article.knowledgeItem > strong", { hasText: "Complemento directo" }).waitFor();
  await selectedCard.getByText("Nueva gramatica de la lengua espanola").waitFor();
  await selectedCard.getByText("Validacion pendiente").first().waitFor();

  const queryPanel = page.locator(".proposalBox", {
    has: page.getByRole("heading", { name: /^Consultar la base$/ }),
  });
  await queryPanel.locator("input").fill("complemento directo");
  await page.getByLabel("Limite de resultados").selectOption("3");
  const firstQueryResponse = page.waitForResponse((response) => {
    const url = new URL(response.url());
    return url.pathname === "/knowledge/query" && response.request().method() === "POST";
  }, { timeout: queryTimeout });
  await queryPanel.getByRole("button", { name: "Consultar" }).click();
  await firstQueryResponse;
  await queryPanel.getByText("Resultado para \"complemento directo\"").waitFor({ timeout: queryTimeout });
  await queryPanel.getByText("Ver detalle tecnico").waitFor();
  await queryPanel.getByText("Ver detalle tecnico").click();
  await queryPanel.locator(".metric", { hasText: "Base recuperada" }).filter({ hasText: "knowledge-v40" }).waitFor();
  await queryPanel.getByText("Nueva gramatica de la lengua espanola").first().waitFor();
  await queryPanel.getByText("ev-rae-ngle-complemento-directo-candidata").first().waitFor();
  await queryPanel.locator("article.knowledgeItem > strong", { hasText: /^Complemento directo$/ }).waitFor();

  await queryPanel.locator("input").fill(emptyQuery);
  const emptyQueryResponse = page.waitForResponse((response) => {
    const url = new URL(response.url());
    return url.pathname === "/knowledge/query" && response.request().method() === "POST";
  }, { timeout: queryTimeout });
  await queryPanel.getByRole("button", { name: "Consultar" }).click();
  await emptyQueryResponse;
  await page.getByText("No hay ficha para esa busqueda").waitFor({ timeout: queryTimeout });
  await page.getByText("Prueba con otra palabra, una materia mas amplia o revisa las estanterias.").waitFor();

  const metrics = queryPanel.locator(".metric");
  const expectedMetrics = [
    ["Resultados", "0"],
    ["Ideas", "0"],
    ["Apoyos", "0"],
  ];

  for (const [label, value] of expectedMetrics) {
    await metrics.filter({ hasText: new RegExp(`^${label}\\s*${value}$`) }).waitFor();
  }

  await page.getByLabel("Navegacion principal").getByRole("button", { name: "Historial" }).click();
  const auditPanel = page.locator(".panel", { hasText: "Historial de busquedas" });
  await page.getByText("Historial de busquedas").waitFor();
  await auditPanel.locator(".metric", { hasText: "Consultas" }).waitFor();
  await auditPanel.locator(".metric", { hasText: "Sin resultado" }).waitFor();
  await auditPanel.getByText("sin resultado").first().waitFor();
  await page.getByText("Consulta en la base publicada").first().waitFor({ timeout: 90000 });
  const historyItem = auditPanel.locator(".auditItem", {
    hasText: "No hubo ficha util para esa busqueda.",
  }).first();
  await historyItem.getByText("No hubo ficha util para esa busqueda.").waitFor();
  await historyItem.getByRole("button", { name: "Detalle" }).click();
  await historyItem.locator("dt", { hasText: "Evento" }).waitFor();
  await historyItem.locator("dt", { hasText: "Base" }).waitFor();
  await historyItem.locator("dt", { hasText: "Longitud" }).waitFor();
  await historyItem.locator("dt", { hasText: "Detalle tecnico" }).waitFor();
  await historyItem.locator("dt", { hasText: "Validacion" }).waitFor();
  await historyItem.getByText("0 pendientes").waitFor();
} finally {
  await browser.close();
}
