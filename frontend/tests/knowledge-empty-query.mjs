import { chromium } from "playwright";

const frontendUrl = process.env.FRONTEND_URL ?? "http://127.0.0.1:5173";
const emptyQuery = "zzzinexistente";

const browser = await chromium.launch();
const page = await browser.newPage();

try {
  await page.goto(frontendUrl, { waitUntil: "networkidle" });
  await page.locator(".proposalBox", { hasText: "Consulta" }).locator("input").fill(emptyQuery);
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
  await page.getByText("Historial de consultas de conocimiento").waitFor();
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
  await page
    .locator(".panel", { hasText: "Eventos recientes" })
    .locator("select")
    .selectOption("Consultas de conocimiento");
  await filteredAuditResponse;
  await page
    .getByText("knowledge-v0 -> consulta · 0 fichas · 0 claims · 0 evidencias")
    .first()
    .waitFor();
  await page.getByText("knowledge.query.executed").first().waitFor();
} finally {
  await browser.close();
}
