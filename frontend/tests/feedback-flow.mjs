import { chromium } from "playwright";

const frontendUrl = process.env.FRONTEND_URL ?? "http://127.0.0.1:5173";

const browser = await chromium.launch();
const page = await browser.newPage();

try {
  await page.goto(frontendUrl, { waitUntil: "networkidle" });
  await page.getByRole("button", { name: "Comparador" }).click();

  const compareResponse = page.waitForResponse((response) => {
    const url = new URL(response.url());
    return url.pathname === "/comparisons" && response.request().method() === "POST";
  });
  await page.getByRole("button", { name: "Comparar" }).click();
  await compareResponse;

  const comparePanel = page.locator(".panel", { hasText: "Resultado" });
  await comparePanel.locator(".metric", { hasText: "Modificacion" }).waitFor();
  await comparePanel.locator(".metric", { hasText: "Adecuacion" }).waitFor();

  const proposalResponse = page.waitForResponse((response) => {
    const url = new URL(response.url());
    return url.pathname.includes("/feedback") && response.request().method() === "POST";
  });
  await page.getByRole("button", { name: "Proponer feedback" }).click();
  await proposalResponse;

  const proposalBox = page.locator(".proposalBox", { hasText: "Feedback propuesto" });
  await proposalBox.getByText("proposed").waitFor();

  const rejectResponse = page.waitForResponse((response) => {
    const url = new URL(response.url());
    return url.pathname.includes("/feedback/proposals/") && response.request().method() === "PATCH";
  });
  await proposalBox.getByRole("button", { name: "No aprender" }).click();
  await rejectResponse;

  await proposalBox.getByText("rejected").waitFor();
} finally {
  await browser.close();
}
