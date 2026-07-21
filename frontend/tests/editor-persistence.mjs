import { chromium } from "playwright";

const frontendUrl = process.env.FRONTEND_URL ?? "http://127.0.0.1:5173";

const browser = await chromium.launch();
const page = await browser.newPage();

try {
  await page.goto(frontendUrl, { waitUntil: "networkidle" });
  await page.getByRole("button", { name: "Editor" }).click();

  const editorPanel = page.locator(".panel", { hasText: "Texto" });
  const inputText = `Smoke editor persistencia ${Date.now()}. Frase para guardar.`;
  await editorPanel.locator("textarea").first().fill(inputText);

  const generationResponse = page.waitForResponse((response) => {
    const url = new URL(response.url());
    return url.pathname === "/generation" && response.request().method() === "POST";
  });
  await page.getByRole("button", { name: "Ejecutar" }).click();
  await generationResponse;

  const resultPanel = page.locator(".inspector", { hasText: "Resultado" });
  await resultPanel.getByText("deterministic").waitFor();

  const output = await resultPanel.locator("textarea[readonly]").inputValue();
  if (!output || output.length < 10) {
    throw new Error("La generacion no devolvio un texto persistible.");
  }

  await page.getByRole("button", { name: "Persistencia" }).click();

  const persistencePanel = page.locator(".panel", { hasText: "Dominios persistidos" });
  await persistencePanel.getByText("Textos").waitFor();
  await persistencePanel.getByText("rewrite · deterministic").first().waitFor();
  await persistencePanel.locator("pre", { hasText: output.slice(0, 40) }).first().waitFor();
} finally {
  await browser.close();
}
