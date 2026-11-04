import type { z } from "zod";

export class ApiError extends Error {
  constructor(
    message: string,
    public readonly status: number = 0,
  ) {
    super(message);
    this.name = "ApiError";
  }
}
export function errorDetail(body: unknown): string | undefined {
  if (!body || typeof body !== "object" || !("detail" in body)) return;
  const detail = body.detail;
  if (typeof detail === "string") return detail;
  if (Array.isArray(detail)) {
    return detail
      .map((entry: unknown) => {
        if (!entry || typeof entry !== "object" || !("msg" in entry))
          return "Verifique os campos informados.";
        const location =
          "loc" in entry && Array.isArray(entry.loc)
            ? entry.loc.filter((part) => part !== "body").join(" → ")
            : "";
        return `${location ? `${location}: ` : ""}${String(entry.msg)}`;
      })
      .join(" · ");
  }
}
export async function apiFetch<T>(
  path: string,
  schema: z.ZodType<T>,
  init?: RequestInit,
): Promise<T> {
  let response: Response;
  try {
    response = await fetch(`/api/backend${path}`, {
      ...init,
      cache: "no-store",
      headers: { "Content-Type": "application/json", ...init?.headers },
    });
  } catch (error) {
    if (error instanceof Error && error.name === "AbortError") throw error;
    throw new ApiError(
      "Não foi possível conectar ao serviço. Verifique sua conexão e tente novamente.",
    );
  }
  const body: unknown = await response.json().catch(() => null);
  if (!response.ok)
    throw new ApiError(
      errorDetail(body) ?? "Não foi possível concluir a solicitação.",
      response.status,
    );
  const parsed = schema.safeParse(body);
  if (!parsed.success)
    throw new ApiError(
      "A API retornou dados em um formato inesperado. Verifique a compatibilidade do serviço.",
    );
  return parsed.data;
}
