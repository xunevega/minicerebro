import { chromium } from "playwright";

const frontendUrl = process.env.FRONTEND_URL ?? "http://127.0.0.1:5173";

const browser = await chromium.launch();
const page = await browser.newPage();

try {
  await page.route("**/profiles/default/editorial-card**", async (route) => {
    await route.fulfill({
      contentType: "application/json",
      body: JSON.stringify({
        profile_id: "default",
        context: "general",
        summary: "Perfil editorial de prueba.",
        strongest_variables: [],
        low_confidence_variables: [],
        accepted_preferences: [],
        maintained_elements: ["claridad"],
        change_requests: ["No va por ahi: Recortar incisos sin revisar intencion."],
        knowledge_card_feedback_count: 1,
        generated_text_count: 0,
        profile_mutation_source: "test",
        stable_knowledge_mutated: false,
        generated_at: new Date().toISOString(),
      }),
    });
  });

  await page.goto(frontendUrl, { waitUntil: "domcontentloaded" });
  await page.getByRole("button", { name: "Mi criterio" }).click();
  await page.getByLabel("Vista").selectOption("profile");

  await page.getByRole("heading", { name: "Lo que Editados sabe de mi" }).waitFor();
  await page.getByText("Gustos, decisiones y ajustes personales.", { exact: true }).waitFor();
  await page.getByRole("heading", { name: "No insistir en esto" }).waitFor();
  await page.getByText("Recortar incisos sin revisar intencion.").waitFor();
  await page.getByText("No va por ahi:").waitFor({ state: "detached" });
} finally {
  await browser.close();
}
