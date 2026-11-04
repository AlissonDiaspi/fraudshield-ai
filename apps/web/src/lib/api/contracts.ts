import { z } from "zod";

export const featureNames = [
  "Time",
  "Amount",
  ...Array.from({ length: 28 }, (_, i) => `V${i + 1}`),
];
export const featuresSchema = z
  .record(z.string(), z.number({ error: "Informe um número válido." }).finite())
  .superRefine((features, ctx) => {
    for (const name of featureNames) {
      if (!(name in features))
        ctx.addIssue({
          code: "custom",
          path: [name],
          message: "Campo obrigatório.",
        });
    }
    for (const name of Object.keys(features)) {
      if (!featureNames.includes(name))
        ctx.addIssue({
          code: "custom",
          path: [name],
          message: "Feature não aceita pela API.",
        });
    }
    for (const name of ["Time", "Amount"]) {
      if (features[name] < 0)
        ctx.addIssue({
          code: "custom",
          path: [name],
          message: "O valor deve ser maior ou igual a zero.",
        });
    }
  });
export const predictionRequestSchema = z
  .object({ features: featuresSchema })
  .strict();
const predictionFields = {
  id: z.uuid(),
  fraud_score: z.number().finite(),
  prediction: z.union([z.literal(0), z.literal(1)]),
  threshold: z.number().finite(),
  model_version: z.string(),
};
export const predictionSchema = z.object({
  ...predictionFields,
  classification: z.string(),
});
export const historyItemSchema = z.object({
  ...predictionFields,
  created_at: z.iso.datetime({ offset: true }),
  features: z.record(z.string(), z.number().finite()),
});
export const historySchema = z.object({
  items: z.array(historyItemSchema),
  total: z.number().int().nonnegative(),
  page: z.number().int().min(1),
  page_size: z.number().int().min(1).max(100),
  total_pages: z.number().int().nonnegative(),
});
export const overviewSchema = z.object({
  total_predictions: z.number().int().nonnegative(),
  fraud_alerts: z.number().int().nonnegative(),
  legitimate_predictions: z.number().int().nonnegative(),
  alert_rate: z.number().finite(),
  average_fraud_score: z.number().finite(),
  last_prediction_at: z.iso.datetime({ offset: true }).nullable(),
});
export const healthSchema = z.object({
  status: z.string(),
  service: z.string(),
  model_loaded: z.boolean(),
});
export type PredictionRequest = z.infer<typeof predictionRequestSchema>;
export type Prediction = z.infer<typeof predictionSchema>;
export type HistoryItem = z.infer<typeof historyItemSchema>;
export type History = z.infer<typeof historySchema>;
export type Overview = z.infer<typeof overviewSchema>;
export type Health = z.infer<typeof healthSchema>;
