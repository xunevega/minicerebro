import { chromium } from "playwright";

const frontendUrl = process.env.FRONTEND_URL ?? "http://127.0.0.1:5173";

const browser = await chromium.launch();
const page = await browser.newPage();

try {
  await page.goto(frontendUrl, { waitUntil: "domcontentloaded" });
  await page.getByRole("button", { name: "Mi perfil" }).click();
  await page.getByRole("button", { name: "Puntuacion" }).click();

  await page.getByLabel("Por que cambias la puntuacion").fill("Smoke UI de ajuste manual revisable.");

  const scoreRow = page.locator(".scoreRow", { hasText: "Dinamismo" }).first();
  const slider = scoreRow.locator('input[type="range"]');
  const targetValue = (await slider.inputValue()) === "80" ? "60" : "80";

  const patchResponse = page.waitForResponse((response) => {
    const url = new URL(response.url());
    return (
      url.pathname === "/profiles/default/scores/dinamismo" &&
      response.request().method() === "PATCH"
    );
  });
  await slider.evaluate((element, value) => {
    const valueSetter = Object.getOwnPropertyDescriptor(
      HTMLInputElement.prototype,
      "value",
    )?.set;
    valueSetter?.call(element, value);
    element.dispatchEvent(new Event("input", { bubbles: true }));
    element.dispatchEvent(new Event("change", { bubbles: true }));
  }, targetValue);
  await patchResponse;
  await scoreRow.getByText(`Ajuste: ${targetValue}`).waitFor();

  const resetResponse = page.waitForResponse((response) => {
    const url = new URL(response.url());
    return (
      url.pathname === "/profiles/default/scores/dinamismo" &&
      response.request().method() === "PATCH"
    );
  });
  await scoreRow.getByRole("button", { name: "Restablecer" }).click();
  await resetResponse;
  await scoreRow.getByText("Ajuste: 0").waitFor();
} finally {
  await browser.close();
}
