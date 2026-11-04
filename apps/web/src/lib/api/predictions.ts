import { apiFetch } from "./client";
import { predictionSchema, type PredictionRequest } from "./contracts";

export type HistoryFilters = {
  prediction?: string;
  model_version?: string;
  start_date?: string;
  end_date?: string;
};
export function historyPath(
  page = 1,
  pageSize = 20,
  filters: HistoryFilters = {},
) {
  const params = new URLSearchParams({
    page: String(page),
    page_size: String(pageSize),
  });
  for (const [key, value] of Object.entries(filters)) {
    if (value !== undefined && value !== "") params.set(key, value);
  }
  return `/predictions?${params}`;
}
export const predict = (payload: PredictionRequest) =>
  apiFetch("/predict", predictionSchema, {
    method: "POST",
    body: JSON.stringify(payload),
  });
