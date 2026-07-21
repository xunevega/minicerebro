import { chromium } from "playwright";

const frontendUrl = process.env.FRONTEND_URL ?? "http://127.0.0.1:5173";

const browser = await chromium.launch();
const page = await browser.newPage();

try {
  await page.goto(frontendUrl, { waitUntil: "networkidle" });

  await page.getByRole("button", { name: "Cerebro" }).click();
  const cerebroPanel = page.locator(".panel", { hasText: "Auditoria Cerebro" });
  await cerebroPanel.getByText("Auditoria Cerebro").waitFor();
  await cerebroPanel.getByText("pending_code_evidence").first().waitFor();
  await cerebroPanel.getByText("Bloqueos antes de reutilizar").waitFor();
  await cerebroPanel.getByText("blocked_until_checked").first().waitFor();

  await page.getByRole("button", { name: "Aceptacion" }).click();
  const acceptancePanel = page.locator(".panel", { hasText: "Aceptacion V1" });
  await acceptancePanel.getByText("Aceptacion V1").waitFor();
  await acceptancePanel.getByText("implemented").first().waitFor();
  await acceptancePanel.getByText("conocimiento").first().waitFor();
} finally {
  await browser.close();
}
