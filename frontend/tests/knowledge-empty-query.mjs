import { chromium } from "playwright";

const frontendUrl = process.env.FRONTEND_URL ?? "http://127.0.0.1:5173";
const emptyQuery = "zzzinexistente";
const queryTimeout = 180000;

const browser = await chromium.launch();
const page = await browser.newPage();

try {
  await page.goto(frontendUrl, { waitUntil: "domcontentloaded" });
  await page.getByLabel("Version explorada").selectOption("latest");
  await page.locator(".metric", { hasText: "Version cargada" }).filter({ hasText: "knowledge-v32" }).first().waitFor();
  await page.locator(".metric", { hasText: "Validacion" }).first().waitFor();
  const gymPanel = page.locator(".proposalBox", { hasText: "Gimnasio de conocimiento" });
  await gymPanel.locator(".statusPill", { hasText: "sano" }).first().waitFor();
  await gymPanel.locator(".metric", { hasText: "Fichas revisadas" }).filter({ hasText: "147" }).waitFor();
  await gymPanel.locator("strong", { hasText: /^Precision$/ }).waitFor();
  await gymPanel.locator("strong", { hasText: /^Trazabilidad$/ }).waitFor();
  await page.getByRole("heading", { name: "Todavia no incluido en V1" }).waitFor();
  const versionPanel = page.locator(".proposalBox", { hasText: "Versiones de conocimiento" });
  await versionPanel.locator(".versionItem", { hasText: "knowledge-v32" }).locator(".metric", { hasText: "Fuentes" }).filter({ hasText: "26" }).waitFor();
  await versionPanel.locator(".versionItem", { hasText: "knowledge-v32" }).getByText("0 fuentes").waitFor();
  await versionPanel.locator(".versionItem", { hasText: "knowledge-v32" }).getByText("+5 nodos").waitFor();
  await versionPanel.locator(".versionItem", { hasText: "knowledge-v0" }).getByText("base congelada").waitFor();
  const sourceExplorerPanel = page.locator(".proposalBox", { hasText: "Explorador de fuentes" });
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
  const ingestionPanel = page.locator(".proposalBox", { hasText: "Registro frente a ingestion" });
  await ingestionPanel.locator(".metric", { hasText: "Publicadas" }).filter({ hasText: "26" }).waitFor();
  await ingestionPanel.locator(".metric", { hasText: "Ingeridas" }).filter({ hasText: "26" }).waitFor();
  await ingestionPanel.locator(".metric", { hasText: "No ingeridas" }).filter({ hasText: "0" }).waitFor();
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
  const pipelinePanel = page.locator(".proposalBox", { hasText: "Explorador de pipeline" });
  await pipelinePanel.locator(".pipelineCard", { hasText: "Glosario de terminos gramaticales" }).getByText("Fuente").waitFor();
  await pipelinePanel.locator(".pipelineCard", { hasText: "Glosario de terminos gramaticales" }).getByText("ExtractionRun").waitFor();
  await pipelinePanel.locator(".pipelineCard", { hasText: "Glosario de terminos gramaticales" }).getByText("Publicacion").waitFor();
  const explorationPanel = page.locator(".proposalBox", { hasText: "Exploracion persistente" });
  await explorationPanel.getByText("Trazabilidad persistente").waitFor();
  await explorationPanel.locator(".metric", { hasText: "Fuentes" }).filter({ hasText: "26" }).waitFor({
    timeout: 90000,
  });
  await explorationPanel.locator(".metric", { hasText: "Nodos" }).filter({ hasText: "149" }).waitFor();
  await explorationPanel.locator(".metric", { hasText: "Evidencias" }).filter({ hasText: "147" }).waitFor();
  await explorationPanel.locator(".pipelineStep", { hasText: /^Fuente$/ }).first().waitFor();
  await explorationPanel.locator(".pipelineStep", { hasText: /^Publicacion$/ }).first().waitFor();
  const complementoClaim = explorationPanel.locator(".traceClaim", {
    hasText: "El complemento directo funciona como participante seleccionado por el predicado verbal",
  });
  await complementoClaim.getByRole("button", { name: "Ver ficha" }).click();
  const selectedCard = page.locator(".proposalBox", { hasText: "Ficha seleccionada" });
  await selectedCard.locator("article.knowledgeItem > strong", { hasText: "Complemento directo" }).waitFor();
  await selectedCard.getByText("Nueva gramatica de la lengua espanola").waitFor();
  await selectedCard.getByText("Manual 2010").waitFor();
  await selectedCard.getByText("Validacion pendiente").first().waitFor();

  const queryPanel = page.locator(".proposalBox", {
    has: page.getByRole("heading", { name: /^Consulta$/ }),
  });
  await queryPanel.locator("input").fill("complemento directo");
  await page.getByLabel("Limite de fichas").selectOption("3");
  const firstQueryResponse = page.waitForResponse((response) => {
    const url = new URL(response.url());
    return url.pathname === "/knowledge/query" && response.request().method() === "POST";
  }, { timeout: queryTimeout });
  await queryPanel.getByRole("button", { name: "Consultar" }).click();
  await firstQueryResponse;
  await queryPanel.getByText("Resultado para \"complemento directo\"").waitFor({ timeout: queryTimeout });
  await queryPanel.getByText("Trazabilidad de consulta").waitFor();
  await queryPanel.locator(".metric", { hasText: "Version recuperada" }).filter({ hasText: "knowledge-v32" }).waitFor();
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
  await page.getByText("Consulta valida sin resultados").waitFor({ timeout: queryTimeout });
  await page
    .getByText("0 fichas, 0 claims y 0 evidencias en version knowledge-v32.")
    .waitFor();

  const metrics = queryPanel.locator(".metric");
  const expectedMetrics = [
    ["Fichas", "0"],
    ["Claims", "0"],
    ["Evidencias", "0"],
  ];

  for (const [label, value] of expectedMetrics) {
    await metrics.filter({ hasText: new RegExp(`^${label}\\s*${value}$`) }).waitFor();
  }

  await page.getByRole("button", { name: "Sistema" }).click();
  await page.getByRole("button", { name: "Historial" }).click();
  const auditPanel = page.locator(".panel", { hasText: "Historial de consultas de conocimiento" });
  await page.getByText("Historial de consultas de conocimiento").waitFor();
  await auditPanel.locator(".metric", { hasText: "Consultas" }).waitFor();
  await auditPanel.locator(".metric", { hasText: "Sin resultado" }).waitFor();
  await auditPanel.getByText("sin resultado").first().waitFor();
  await page.getByText("knowledge-v32 -> consulta").first().waitFor();
  const historyItem = auditPanel.locator(".auditItem", {
    hasText: "0 validaciones pendientes",
  }).first();
  await historyItem.getByText("0 validaciones pendientes").waitFor();
  await historyItem.getByRole("button", { name: "Detalle" }).click();
  await historyItem.locator("dt", { hasText: "Evento" }).waitFor();
  await historyItem.locator("dt", { hasText: "Version" }).waitFor();
  await historyItem.locator("dt", { hasText: "Longitud" }).waitFor();
  await historyItem.locator("dt", { hasText: "Recorrido" }).waitFor();
  await historyItem.locator("dt", { hasText: "Validacion" }).waitFor();
  await historyItem.getByText("0 pendientes").waitFor();
} finally {
  await browser.close();
}
