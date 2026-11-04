import { expect, test, type Page } from "@playwright/test";

// Explicit synthetic test fixtures. No application page imports this module.
const id = "00000000-0000-4000-8000-000000000001";
const features = Object.fromEntries(
  ["Time", "Amount", ...Array.from({ length: 28 }, (_, i) => `V${i + 1}`)].map(
    (name) => [name, 0],
  ),
);
const item = {
  id,
  created_at: "2026-11-03T12:00:00Z",
  features,
  fraud_score: 0.12,
  prediction: 0,
  threshold: 0.5,
  model_version: "test-only",
};
const emptyHistory = {
  items: [],
  total: 0,
  page: 1,
  page_size: 20,
  total_pages: 0,
};
const overview = {
  total_predictions: 2,
  fraud_alerts: 1,
  legitimate_predictions: 1,
  alert_rate: 0.5,
  average_fraud_score: 0.42,
  last_prediction_at: item.created_at,
};
async function fixtures(page: Page) {
  await page.route("**/api/backend/**", async (route) => {
    const url = new URL(route.request().url());
    const path = url.pathname;
    if (path.endsWith("/health"))
      return route.fulfill({
        json: {
          status: "healthy",
          service: "fraudshield-api",
          model_loaded: true,
        },
      });
    if (path.endsWith("/statistics/overview"))
      return route.fulfill({ json: overview });
    if (path.endsWith("/predict"))
      return route.fulfill({ json: { ...item, classification: "legitimate" } });
    if (path.endsWith(`/${id}`)) return route.fulfill({ json: item });
    return route.fulfill({ json: emptyHistory });
  });
}
test("real unavailable backend renders honest errors on the dashboard", async ({
  page,
}) => {
  await page.goto("/dashboard");
  await expect(
    page.getByText("API indisponível", { exact: true }),
  ).toBeVisible();
  await expect(page.getByRole("main").getByRole("alert").first()).toBeVisible();
  await expect(
    page
      .getByText("A API está indisponível ou demorou para responder.", {
        exact: false,
      })
      .first(),
  ).toBeVisible();
});
test("dashboard renders actual contract aggregates and empty history", async ({
  page,
}) => {
  await fixtures(page);
  await page.goto("/dashboard");
  await expect(
    page.getByRole("banner").getByText("API operacional", { exact: true }),
  ).toBeVisible();
  await expect(page.getByText("50%", { exact: true }).first()).toBeVisible();
  await expect(page.getByText("Nenhuma transação por aqui")).toBeVisible();
  await expect(page.locator(".recharts-wrapper")).toBeVisible();
});
test("history forwards filters, timezone and real backend pagination", async ({
  page,
}) => {
  await fixtures(page);
  await page.route("**/api/backend/predictions?**", async (route) => {
    const query = new URL(route.request().url()).searchParams;
    const current = Number(query.get("page") || 1);
    return route.fulfill({
      json: {
        items: [item],
        total: 41,
        page: current,
        page_size: 20,
        total_pages: 3,
      },
    });
  });
  await page.goto("/transactions");
  await expect(page.getByText("Página 1 de 3")).toBeVisible();
  await page.getByRole("button", { name: "Próxima página" }).click();
  await expect(page.getByText("Página 2 de 3")).toBeVisible();
  await page.getByLabel("Classificação", { exact: true }).selectOption("0");
  await page.getByLabel("Versão do modelo", { exact: true }).fill("test-only");
  await page.getByLabel("Data e hora inicial").fill("2026-11-03T09:00");
  const outgoing = page.waitForRequest((request) =>
    request.url().includes("prediction=0"),
  );
  await page.getByRole("button", { name: "Aplicar filtros" }).click();
  const query = new URL((await outgoing).url()).searchParams;
  expect(query.get("page")).toBe("1");
  expect(query.get("model_version")).toBe("test-only");
  expect(query.get("start_date")).toBe("2026-11-03T12:00:00.000Z");
});
test("prediction validates fields and submits the exact 30-feature payload", async ({
  page,
}) => {
  await fixtures(page);
  await page.goto("/analyze");
  await page
    .getByRole("button", { name: "Analisar transação", exact: true })
    .click();
  await expect(page.getByRole("main").getByRole("alert")).toContainText(
    "Revise os campos",
  );
  await page.getByRole("main").getByText("Já possui os dados em JSON?").click();
  await page
    .getByLabel("Cole o payload real da transação")
    .fill(JSON.stringify({ features }));
  await page.getByRole("button", { name: "Preencher formulário" }).click();
  const outgoing = page.waitForRequest("**/api/backend/predict");
  await page
    .getByRole("button", { name: "Analisar transação", exact: true })
    .click();
  expect((await outgoing).postDataJSON()).toEqual({ features });
  await expect(page.getByText("Previsão concluída e registrada")).toBeVisible();
  await page.getByRole("link", { name: "Ver registro completo" }).click();
  await expect(
    page.getByRole("heading", { name: "Detalhes da transação" }),
  ).toBeVisible();
  await expect(
    page.getByText("30 features registradas nesta previsão"),
  ).toBeVisible();
});
test("prediction surfaces HTTP 422 feedback", async ({ page }) => {
  await fixtures(page);
  await page.route("**/api/backend/predict", (route) =>
    route.fulfill({
      status: 422,
      json: { detail: "Amount não pode ser negativo." },
    }),
  );
  await page.goto("/analyze");
  await page.getByRole("main").getByText("Já possui os dados em JSON?").click();
  await page
    .getByLabel("Cole o payload real da transação")
    .fill(JSON.stringify({ features }));
  await page.getByRole("button", { name: "Preencher formulário" }).click();
  await page
    .getByRole("button", { name: "Analisar transação", exact: true })
    .click();
  await expect(page.getByRole("main").getByRole("alert")).toContainText(
    "Amount não pode ser negativo.",
  );
});
test("details handles backend 404", async ({ page }) => {
  await fixtures(page);
  await page.route(`**/api/backend/predictions/${id}`, (route) =>
    route.fulfill({
      status: 404,
      json: { detail: "Previsão não encontrada." },
    }),
  );
  await page.goto(`/transactions/${id}`);
  await expect(
    page.getByText("Previsão não encontrada", { exact: true }),
  ).toBeVisible();
});
test("loading skeleton remains visible while a request is pending", async ({
  page,
}) => {
  await fixtures(page);
  let release!: () => void;
  const pending = new Promise<void>((resolve) => {
    release = resolve;
  });
  await page.route("**/api/backend/predictions?**", async (route) => {
    await pending;
    await route.fulfill({ json: emptyHistory });
  });
  await page.goto("/transactions");
  await expect(
    page.getByRole("status", { name: "Carregando dados" }),
  ).toBeVisible();
  release();
  await expect(page.getByText("Nenhuma transação por aqui")).toBeVisible();
});
test("empty aggregate response displays an informative chart state", async ({
  page,
}) => {
  await fixtures(page);
  await page.route("**/api/backend/statistics/overview", (route) =>
    route.fulfill({
      json: {
        ...overview,
        total_predictions: 0,
        fraud_alerts: 0,
        legitimate_predictions: 0,
        alert_rate: 0,
        average_fraud_score: 0,
        last_prediction_at: null,
      },
    }),
  );
  await page.goto("/dashboard");
  await expect(
    page.getByText("A distribuição começa na primeira análise"),
  ).toBeVisible();
});
test("responsive routes fit 320px through ultrawide and mobile drawer supports keyboard", async ({
  page,
}) => {
  await fixtures(page);
  for (const width of [320, 390, 768, 1024, 1440, 2560]) {
    await page.setViewportSize({ width, height: 900 });
    for (const path of [
      "/dashboard",
      "/analyze",
      "/transactions",
      `/transactions/${id}`,
      "/system",
    ]) {
      await page.goto(path);
      await expect(page.locator("h1:visible")).toBeVisible();
      expect(
        await page.evaluate(
          () => document.documentElement.scrollWidth <= window.innerWidth,
        ),
        `${path} at ${width}px`,
      ).toBe(true);
    }
  }
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto("/dashboard");
  await page.getByRole("button", { name: "Abrir navegação" }).click();
  await expect(page.getByRole("dialog")).toBeVisible();
  await page.keyboard.press("Escape");
  await expect(page.getByRole("dialog")).not.toBeVisible();
  await page.screenshot({
    path: "test-results/dashboard-mobile.png",
    fullPage: true,
    animations: "disabled",
  });
  await page.setViewportSize({ width: 1440, height: 1000 });
  await page.screenshot({
    path: "test-results/dashboard-desktop.png",
    fullPage: true,
    animations: "disabled",
  });
});

test("system reports a missing model without claiming prediction readiness", async ({
  page,
}) => {
  await fixtures(page);
  await page.route("**/api/backend/health", (route) =>
    route.fulfill({
      json: {
        status: "unhealthy",
        service: "fraudshield-api",
        model_loaded: false,
      },
    }),
  );
  await page.goto("/system");
  await expect(
    page.getByRole("heading", { name: "Serviço com restrições" }),
  ).toBeVisible();
  await expect(page.getByText("Não carregado", { exact: true })).toBeVisible();
  await expect(
    page.getByText("Disponível no health check", { exact: true }),
  ).not.toBeVisible();
});

test("successful routes render without browser runtime errors and the sidebar collapses", async ({
  page,
}) => {
  await fixtures(page);
  const errors: string[] = [];
  page.on("pageerror", (error) => errors.push(error.message));
  page.on("console", (message) => {
    if (message.type() === "warning" || message.type() === "error")
      errors.push(message.text());
  });
  await page.setViewportSize({ width: 1440, height: 1000 });
  await page.goto("/dashboard");
  await page.getByRole("button", { name: "Recolher menu" }).click();
  await expect(page.locator(".app-shell")).toHaveClass(/sidebar-collapsed/);
  await page.getByRole("button", { name: "Expandir menu" }).click();
  for (const path of [
    "/analyze",
    "/transactions",
    `/transactions/${id}`,
    "/system",
  ]) {
    await page.goto(path);
    await expect(page.locator("h1:visible")).toBeVisible();
    await expect(
      page.getByRole("banner").getByText("API operacional", { exact: true }),
    ).toBeVisible();
  }
  expect(errors).toEqual([]);
});
