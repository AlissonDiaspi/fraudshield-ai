import assert from "node:assert/strict";
import { test } from "node:test";
import {
  featureNames,
  predictionRequestSchema,
  overviewSchema,
} from "../src/lib/api/contracts";
import { errorDetail } from "../src/lib/api/client";
import { historyPath } from "../src/lib/api/predictions";

// Synthetic fixtures are confined to tests and are never served by the application.
const features = () =>
  Object.fromEntries(featureNames.map((name) => [name, 0]));
test("prediction contract accepts all 30 finite numeric features", () => {
  assert.equal(
    predictionRequestSchema.safeParse({ features: features() }).success,
    true,
  );
});
test("prediction rejects missing, extra, string, infinite and negative constrained features", () => {
  const missing = features();
  delete missing.V28;
  for (const invalid of [
    missing,
    { ...features(), Unknown: 0 },
    { ...features(), V1: "1" },
    { ...features(), V1: Infinity },
    { ...features(), Amount: -1 },
    { ...features(), Time: -1 },
  ]) {
    assert.equal(
      predictionRequestSchema.safeParse({ features: invalid }).success,
      false,
    );
  }
  assert.equal(
    predictionRequestSchema.safeParse({ features: features(), extra: 1 })
      .success,
    false,
  );
});
test("history query preserves false classification, pagination and timezone dates", () => {
  const path = historyPath(3, 50, {
    prediction: "0",
    model_version: "v & 1",
    start_date: "2026-11-03T03:00:00.000Z",
  });
  const query = new URL(path, "http://localhost").searchParams;
  assert.equal(query.get("prediction"), "0");
  assert.equal(query.get("page"), "3");
  assert.equal(query.get("page_size"), "50");
  assert.equal(query.get("model_version"), "v & 1");
  assert.equal(query.get("start_date"), "2026-11-03T03:00:00.000Z");
  assert.equal(query.has("end_date"), false);
});
test("FastAPI validation messages include affected field paths", () => {
  assert.equal(
    errorDetail({
      detail: [{ loc: ["body", "features", "Amount"], msg: "Valor inválido" }],
    }),
    "features → Amount: Valor inválido",
  );
  assert.equal(
    errorDetail({ detail: "Previsão não encontrada." }),
    "Previsão não encontrada.",
  );
  assert.equal(errorDetail(null), undefined);
});
test("statistics accept an empty real response and reject incompatible contracts", () => {
  assert.equal(
    overviewSchema.safeParse({
      total_predictions: 0,
      fraud_alerts: 0,
      legitimate_predictions: 0,
      alert_rate: 0,
      average_fraud_score: 0,
      last_prediction_at: null,
    }).success,
    true,
  );
  assert.equal(overviewSchema.safeParse({ total: 20 }).success, false);
});
