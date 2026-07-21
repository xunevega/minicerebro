import { chromium } from "playwright";

const frontendUrl = process.env.FRONTEND_URL ?? "http://127.0.0.1:5173";

const browser = await chromium.launch();
const page = await browser.newPage();

try {
  await page.goto(frontendUrl, { waitUntil: "networkidle" });

  await page.getByRole("button", { name: "Persistencia" }).click();
  const persistencePanel = page.locator(".panel", { hasText: "Dominios persistidos" });
  await persistencePanel.locator("article.knowledgeItem > strong", { hasText: "knowledge" }).waitFor();
  await persistencePanel.locator("article.knowledgeItem > strong", { hasText: "preferences" }).waitFor();
  await persistencePanel.getByText("generated_texts").waitFor();
  await persistencePanel.getByText("knowledge_versions").waitFor();

  await page.getByRole("button", { name: "Cierre" }).click();
  const closurePanel = page.locator(".panel", { hasText: "Condiciones de cierre" });
  await closurePanel.getByText("V1 solo trata escritura en lengua espanola.").waitFor();
  await closurePanel.getByText("satisfied").first().waitFor();
  await closurePanel.getByRole("heading", { name: "Cierre tecnico" }).waitFor();
  await closurePanel.getByText("Limites 21/22").waitFor();
  await closurePanel.getByText("not_defined_in_v1").first().waitFor();
  await closurePanel.getByText("Mantener V1 cerrada").waitFor();

  await page.getByRole("button", { name: "Roadmap" }).click();
  const roadmapPanel = page.locator(".panel", { hasText: "Roadmap tecnico" });
  await roadmapPanel.getByText("Conocimiento").waitFor();
  await roadmapPanel.getByText("validacion visible y auditada").waitFor();
  await roadmapPanel.getByText("Observabilidad").waitFor();
  await roadmapPanel.getByText("retrieval_quality").waitFor();
  await roadmapPanel.getByText("available").first().waitFor();

  await page.getByRole("button", { name: "Pantallas" }).click();
  const screensPanel = page.locator(".panel", { hasText: "Pantallas V1" });
  await screensPanel.getByText("Reglas").waitFor();
  await screensPanel.getByText("Persistencia").waitFor();
  await screensPanel.getByText("Auditoria").waitFor();
  await screensPanel.getByText("implemented · /audit").waitFor();
} finally {
  await browser.close();
}
