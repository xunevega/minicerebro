import { chromium } from "playwright";

const frontendUrl = process.env.FRONTEND_URL ?? "http://127.0.0.1:5173";

const browser = await chromium.launch();
const page = await browser.newPage();

try {
  await page.goto(frontendUrl, { waitUntil: "networkidle" });

  const panel = page.locator(".proposalBox", { hasText: "Ingestion manual minima" });
  await panel.getByText("Solo una candidate real permite aprobar propuestas").waitFor();

  const sourceSelect = page.getByLabel("Fuente para ingestion manual");
  const optionValue = await sourceSelect.evaluate((select) => {
    const options = Array.from(select.options);
    return (
      options.find((option) => !option.textContent?.includes("published"))?.value ??
      options[0]?.value
    );
  });
  await sourceSelect.selectOption(optionValue);

  const proposalResponse = page.waitForResponse((response) => {
    const url = new URL(response.url());
    return (
      url.pathname.includes("/knowledge/extractions/") &&
      url.pathname.endsWith("/proposals") &&
      response.request().method() === "POST"
    );
  });
  await panel.getByRole("button", { name: "Crear lote manual" }).click();
  await proposalResponse;

  for (const label of ["Edicion", "Indice", "Segmento", "ExtractionRun", "Proposals"]) {
    await panel.locator(".pipelineStep.done", { hasText: new RegExp(`^${label}$`) }).waitFor();
  }
  await panel.locator(".metric", { hasText: "Extraccion" }).filter({ hasText: "completed" }).waitFor();
  await panel.locator(".metric", { hasText: "Proposals" }).filter({ hasText: "5" }).waitFor();
  await panel.locator(".metric", { hasText: "Destino" }).filter({ hasText: "candidate-pending" }).waitFor();
  await panel.locator("article.knowledgeItem > strong", { hasText: /^Nodo candidato manual$/ }).waitFor();
  await panel.getByText("node · proposed").waitFor();
  await panel.getByText("card · proposed").waitFor();
  await panel.getByText("evidence · proposed").waitFor();
  await panel.getByText("claim · proposed").waitFor();
  await panel.getByText("relation · proposed").waitFor();

  const rejectResponse = page.waitForResponse((response) => {
    const url = new URL(response.url());
    return (
      url.pathname.includes("/knowledge/proposals/") &&
      url.pathname.endsWith("/reject") &&
      response.request().method() === "POST"
    );
  });
  await panel.getByRole("button", { name: "Rechazar" }).first().click();
  await rejectResponse;
  await panel.getByText("node · rejected").waitFor();
} finally {
  await browser.close();
}
