import { chromium } from "playwright";

const frontendUrl = process.env.FRONTEND_URL ?? "http://127.0.0.1:5173";
const emptyQuery = "zzzinexistente";

const browser = await chromium.launch();
const page = await browser.newPage();

try {
  await page.goto(frontendUrl, { waitUntil: "networkidle" });
  await page.locator(".proposalBox", { hasText: "Consulta" }).locator("input").fill(emptyQuery);
  await page.getByLabel("Limite de fichas").selectOption("3");
  await page.getByRole("button", { name: "Consultar" }).click();

  await page.getByText("Consulta valida sin resultados").waitFor();
  await page
    .getByText("0 fichas, 0 claims y 0 evidencias en version knowledge-v0.")
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

  await page.getByRole("button", { name: "Auditoria" }).click();
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
      url.searchParams.get("version") === "knowledge-v0" &&
      url.searchParams.get("limit") === "50"
    );
  });
  await page.getByLabel("Limite historial").selectOption("50");
  await historyLimitResponse;
  await page.getByText("knowledge-v0 -> consulta").first().waitFor();
  const filteredAuditResponse = page.waitForResponse((response) => {
    const url = new URL(response.url());
    return (
      url.pathname === "/audit/events" &&
      url.searchParams.get("event_type") === "knowledge.query.executed" &&
      url.searchParams.get("entity_type") === "knowledge_version" &&
      url.searchParams.get("entity_id") === "knowledge-v0"
    );
  });
  await page.getByLabel("Filtro auditoria").selectOption("Consultas de conocimiento");
  await filteredAuditResponse;
  await page
    .getByText("knowledge-v0 -> consulta · 0 fichas · 0 claims · 0 evidencias")
    .first()
    .waitFor();
  await page.getByText("knowledge.query.executed").first().waitFor();
} finally {
  await browser.close();
}
