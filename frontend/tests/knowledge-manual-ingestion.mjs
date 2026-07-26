import { chromium } from "playwright";

const frontendUrl = process.env.FRONTEND_URL ?? "http://127.0.0.1:5173";

const browser = await chromium.launch();
const page = await browser.newPage();

try {
  await page.goto(frontendUrl, { waitUntil: "domcontentloaded" });
  await page.getByRole("button", { name: "Biblioteca" }).click();
  await page.getByRole("button", { name: "Ver modo tecnico" }).click();

  const panel = page.locator(".proposalBox", {
    has: page.getByRole("heading", { name: /^Crear lote de ingestion$/ }),
  });
  await panel.getByText("Solo un candidato real permite aprobar propuestas").waitFor();

  const sourceSelect = page.getByLabel("Fuente para ingestion manual");
  const button = panel.getByRole("button", { name: "Crear lote manual" });
  const hasCandidateSource = (await sourceSelect.locator("option").count()) > 0;
  if (!hasCandidateSource) {
    if (!(await button.isDisabled())) {
      throw new Error("Manual ingestion button should be disabled without candidate sources");
    }
  }
  if (hasCandidateSource) {
    await sourceSelect.locator("option").first().waitFor({ state: "attached" });
    const optionValue = await sourceSelect.evaluate((select) => {
      const options = Array.from(select.options);
      return (
        options.find((option) => !option.textContent?.includes("published"))?.value ??
        options[0]?.value
      );
    });
    await sourceSelect.selectOption(optionValue);

    const proposalResponse = page.waitForResponse(
      (response) => {
        const url = new URL(response.url());
        return (
          url.pathname.includes("/knowledge/extractions/") &&
          url.pathname.endsWith("/proposals") &&
          response.request().method() === "POST"
        );
      },
      { timeout: 90000 },
    );
    await button.click();
    await proposalResponse;

    for (const label of ["Edicion", "Indice", "Segmento", "Extraccion", "Propuestas"]) {
      await panel.locator(".pipelineStep.done", { hasText: new RegExp(`^${label}$`) }).waitFor();
    }
    await panel.locator(".metric", { hasText: "Extraccion" }).filter({ hasText: "completed" }).waitFor();
    await panel.locator(".metric", { hasText: "Propuestas" }).filter({ hasText: "5" }).waitFor();
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
  }
} finally {
  await browser.close();
}
