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
} finally {
  await browser.close();
}
