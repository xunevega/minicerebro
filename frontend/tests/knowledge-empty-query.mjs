import { chromium } from "playwright";

const frontendUrl = process.env.FRONTEND_URL ?? "http://127.0.0.1:5173";
const emptyQuery = "zzzinexistente";
const queryTimeout = 180000;

const browser = await chromium.launch();
const page = await browser.newPage();

try {
  await page.goto(frontendUrl, { waitUntil: "domcontentloaded" });
  await page.getByRole("button", { name: "Biblioteca" }).click();
  await page.getByRole("heading", { name: "Biblioteca", exact: true }).waitFor({ timeout: 90000 });
  await page.getByRole("heading", { name: "Fichas de escritura" }).waitFor({ timeout: 90000 });

  const queryPanel = page.locator(".proposalBox", {
    has: page.getByRole("heading", { name: /^Consultar la base$/ }),
  });
  await queryPanel.locator("input").fill("claridad");
  const firstQueryResponse = page.waitForResponse((response) => {
    const url = new URL(response.url());
    return url.pathname === "/knowledge/query" && response.request().method() === "POST";
  }, { timeout: queryTimeout });
  await queryPanel.getByRole("button", { name: "Consultar" }).click();
  await firstQueryResponse;
  await queryPanel.getByText("Resultado para \"claridad\"").waitFor({ timeout: queryTimeout });
  await queryPanel.locator("article.knowledgeItem").first().waitFor({ timeout: queryTimeout });

  await queryPanel.locator("input").fill(emptyQuery);
  const emptyQueryResponse = page.waitForResponse((response) => {
    const url = new URL(response.url());
    return url.pathname === "/knowledge/query" && response.request().method() === "POST";
  }, { timeout: queryTimeout });
  await queryPanel.getByRole("button", { name: "Consultar" }).click();
  await emptyQueryResponse;
  await page.getByText("No hay ficha para esa busqueda").waitFor({ timeout: queryTimeout });
  await page.getByText("Prueba con otra palabra, una materia mas amplia o revisa las estanterias.").waitFor();

  await page.getByLabel("Navegacion principal").getByRole("button", { name: "Historial" }).click();
  const auditPanel = page.locator(".panel", { hasText: "Ultimas consultas" });
  await auditPanel.getByRole("heading", { name: "Ultimas consultas" }).waitFor();
  const historyItem = auditPanel.locator(".auditItem", {
    hasText: "No hubo ficha util para esa busqueda.",
  }).first();
  await historyItem.getByText("No hubo ficha util para esa busqueda.").waitFor({ timeout: 90000 });
  await historyItem.getByRole("button", { name: "Detalle" }).click();
  await historyItem.locator("dt", { hasText: "Base" }).waitFor();
  await historyItem.locator("dt", { hasText: "Datos de consulta" }).waitFor();
} finally {
  await browser.close();
}
