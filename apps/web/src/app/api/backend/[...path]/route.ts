import { NextRequest, NextResponse } from "next/server";

export const dynamic = "force-dynamic";
type Context = { params: Promise<{ path: string[] }> };
async function forward(request: NextRequest, context: Context) {
  const { path } = await context.params;
  const route = path.join("/");
  const allowedGet =
    ["health", "statistics/overview", "predictions"].includes(route) ||
    /^predictions\/[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i.test(
      route,
    );
  if (
    !(request.method === "GET" && allowedGet) &&
    !(request.method === "POST" && route === "predict")
  ) {
    return NextResponse.json(
      { detail: "Rota não encontrada." },
      { status: 404 },
    );
  }
  try {
    const base = (process.env.API_URL || "http://127.0.0.1:8000").replace(
      /\/$/,
      "",
    );
    const url = new URL(`${base}/${route}`);
    url.search = request.nextUrl.search;
    const response = await fetch(url, {
      method: request.method,
      headers: {
        "Content-Type": "application/json",
        Accept: "application/json",
      },
      body: request.method === "POST" ? await request.text() : undefined,
      signal: AbortSignal.any([request.signal, AbortSignal.timeout(15000)]),
      cache: "no-store",
      redirect: "error",
    });
    if (response.status >= 500)
      return NextResponse.json(
        {
          detail:
            "O serviço encontrou um problema ao processar a solicitação. Tente novamente em instantes.",
        },
        { status: response.status },
      );
    const body: unknown = await response.json();
    return NextResponse.json(body, {
      status: response.status,
      headers: { "Cache-Control": "no-store" },
    });
  } catch {
    return NextResponse.json(
      {
        detail:
          "A API está indisponível ou demorou para responder. Verifique o serviço e tente novamente.",
      },
      { status: 503 },
    );
  }
}
export const GET = forward;
export const POST = forward;
