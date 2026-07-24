import { chromium } from "playwright";

const frontendUrl = process.env.FRONTEND_URL ?? "http://127.0.0.1:5173";
const emptyQuery = "zzzinexistente";

const browser = await chromium.launch();
const page = await browser.newPage();

try {
  await page.goto(frontendUrl, { waitUntil: "networkidle" });
  await page.getByLabel("Version explorada").selectOption("latest");
  await page.locator(".metric", { hasText: "Version cargada" }).filter({ hasText: "knowledge-v16" }).first().waitFor();
  await page.locator(".metric", { hasText: "Validacion" }).filter({ hasText: "201 pendientes" }).first().waitFor();
  await page.getByRole("heading", { name: "Todavia no incluido en V1" }).waitFor();
  const versionPanel = page.locator(".proposalBox", { hasText: "Versiones de conocimiento" });
  await versionPanel.locator(".versionItem", { hasText: "knowledge-v16" }).locator(".metric", { hasText: "Fuentes" }).filter({ hasText: "14" }).waitFor();
  await versionPanel.locator(".versionItem", { hasText: "knowledge-v16" }).getByText("+1 fuentes").waitFor();
  await versionPanel.locator(".versionItem", { hasText: "knowledge-v16" }).getByText("+5 nodos").waitFor();
  await versionPanel.locator(".versionItem", { hasText: "knowledge-v0" }).getByText("base congelada").waitFor();
  const sourceExplorerPanel = page.locator(".proposalBox", { hasText: "Explorador de fuentes" });
  await sourceExplorerPanel.getByText("Publicadas · 14").waitFor();
  await sourceExplorerPanel.getByText("Ingeridas sin publicar · 0").waitFor();
  await sourceExplorerPanel.getByText("Disponibles sin ingerir · 0").waitFor();
  await sourceExplorerPanel.getByText("Registradas pendientes · 9").waitFor();
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
  const ingestionPanel = page.locator(".proposalBox", { hasText: "Registro frente a ingestion" });
  await ingestionPanel.locator(".metric", { hasText: "Publicadas" }).filter({ hasText: "14" }).waitFor();
  await ingestionPanel.locator(".metric", { hasText: "Ingeridas" }).filter({ hasText: "14" }).waitFor();
  await ingestionPanel.locator(".metric", { hasText: "No ingeridas" }).filter({ hasText: "9" }).waitFor();
  await ingestionPanel.getByText("publicada: 14").waitFor();
  await ingestionPanel.getByText("con edicion: 9").waitFor();
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
  const pipelinePanel = page.locator(".proposalBox", { hasText: "Explorador de pipeline" });
  await pipelinePanel.locator(".pipelineCard", { hasText: "Glosario de terminos gramaticales" }).getByText("Fuente").waitFor();
  await pipelinePanel.locator(".pipelineCard", { hasText: "Glosario de terminos gramaticales" }).getByText("ExtractionRun").waitFor();
  await pipelinePanel.locator(".pipelineCard", { hasText: "Glosario de terminos gramaticales" }).getByText("Publicacion").waitFor();
  const explorationPanel = page.locator(".proposalBox", { hasText: "Exploracion persistente" });
  await explorationPanel.getByText("Trazabilidad persistente").waitFor();
  await explorationPanel.locator(".metric", { hasText: "Fuentes" }).filter({ hasText: "14" }).waitFor();
  await explorationPanel.locator(".metric", { hasText: "Nodos" }).filter({ hasText: "69" }).waitFor();
  await explorationPanel.locator(".metric", { hasText: "Evidencias" }).filter({ hasText: "67" }).waitFor();
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

  const queryPanel = page.locator(".proposalBox", { hasText: "Consulta" });
  await queryPanel.locator("input").fill("complemento directo");
  await page.getByLabel("Limite de fichas").selectOption("3");
  await page.getByRole("button", { name: "Consultar" }).click();
  await queryPanel.getByText("Resultado para \"complemento directo\"").waitFor();
  await queryPanel.getByText("Trazabilidad de consulta").waitFor();
  await queryPanel.locator(".metric", { hasText: "Version recuperada" }).filter({ hasText: "knowledge-v16" }).waitFor();
  await queryPanel.getByText("Nueva gramatica de la lengua espanola").first().waitFor();
  await queryPanel.getByText("ev-rae-ngle-complemento-directo-candidata").first().waitFor();
  await queryPanel.locator("article.knowledgeItem > strong", { hasText: /^Complemento directo$/ }).waitFor();

  await queryPanel.locator("input").fill(emptyQuery);
  await page.getByRole("button", { name: "Consultar" }).click();
  await page.getByText("Consulta valida sin resultados").waitFor();
  await page
    .getByText("0 fichas, 0 claims y 0 evidencias en version knowledge-v16.")
    .waitFor();

  const metrics = page.locator(".proposalBox", { hasText: "Consulta" }).locator(".metric");
  const expectedMetrics = [
    ["Fichas", "0"],
    ["Claims", "0"],
    ["Evidencias", "0"],
  ];

  for (const [label, value] of expectedMetrics) {
    await metrics.filter({ hasText: label }).filter({ hasText: value }).waitFor();
  }

  await page.getByRole("button", { name: "Sistema" }).click();
  await page.getByRole("button", { name: "Historial" }).click();
  const auditPanel = page.locator(".panel", { hasText: "Historial de consultas de conocimiento" });
  await page.getByText("Historial de consultas de conocimiento").waitFor();
  await auditPanel.locator(".metric", { hasText: "Consultas" }).waitFor();
  await auditPanel.locator(".metric", { hasText: "Sin resultado" }).waitFor();
  await auditPanel.getByText("sin resultado").first().waitFor();
  await auditPanel.getByText("14 caracteres · limite 3").first().waitFor();
  const historyLimitResponse = page.waitForResponse((response) => {
    const url = new URL(response.url());
    return (
      url.pathname === "/knowledge/query-history" &&
      url.searchParams.get("version") === "knowledge-v16" &&
      url.searchParams.get("limit") === "50"
    );
  });
  await page.getByLabel("Limite historial").selectOption("50");
  await historyLimitResponse;
  await page.getByText("knowledge-v16 -> consulta").first().waitFor();
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
  const filteredAuditResponse = page.waitForResponse((response) => {
    const url = new URL(response.url());
    return (
      url.pathname === "/audit/events" &&
      url.searchParams.get("event_type") === "knowledge.query.executed" &&
      url.searchParams.get("entity_type") === "knowledge_version" &&
      url.searchParams.get("entity_id") === "knowledge-v16"
    );
  });
  await page.getByLabel("Filtro auditoria").selectOption("Consultas de conocimiento");
  await filteredAuditResponse;
  await page
    .getByText("knowledge-v16 -> consulta · 0 fichas · 0 claims · 0 evidencias")
    .first()
    .waitFor();
  await page.getByText("knowledge.query.executed").first().waitFor();
  await historyItem.getByRole("button", { name: "Ver version consultada" }).click();
  await page.getByText("Version navegada: knowledge-v16").waitFor();
} finally {
  await browser.close();
}
