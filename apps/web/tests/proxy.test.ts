import assert from "node:assert/strict";
import { createServer } from "node:http";
import { after, before, test } from "node:test";
import { NextRequest } from "next/server";
import { GET, POST } from "../src/app/api/backend/[...path]/route";

let base: string;
let receivedUrl = "";
let receivedBody = "";
const previousApiUrl = process.env.API_URL;
const server = createServer(async (request, response) => {
  receivedUrl = request.url ?? "";
  receivedBody = "";
  for await (const chunk of request) receivedBody += String(chunk);
  response.setHeader("content-type", "application/json");
  if (receivedUrl.includes("model_version=broken")) {
    response.writeHead(500);
    response.end("private diagnostic");
    return;
  }
  if (receivedUrl.includes("model_version=invalid")) {
    response.writeHead(422);
    response.end(JSON.stringify({ detail: "Filtro inválido" }));
    return;
  }
  if (receivedUrl.startsWith("/predictions/")) {
    response.writeHead(404);
    response.end(JSON.stringify({ detail: "Previsão não encontrada." }));
    return;
  }
  response.end(JSON.stringify({ accepted: true }));
});
before(async () => {
  await new Promise<void>((resolve) => server.listen(0, "127.0.0.1", resolve));
  const address = server.address();
  if (!address || typeof address === "string")
    throw new Error("Test server unavailable");
  base = `http://127.0.0.1:${address.port}`;
  process.env.API_URL = base;
});
after(async () => {
  if (previousApiUrl === undefined) delete process.env.API_URL;
  else process.env.API_URL = previousApiUrl;
  await new Promise<void>((resolve) => server.close(() => resolve()));
});
test("proxy forwards pagination and filters to the exact backend route", async () => {
  const response = await GET(
    new NextRequest(
      "http://localhost/api/backend/predictions?page=2&prediction=0",
    ),
    { params: Promise.resolve({ path: ["predictions"] }) },
  );
  assert.equal(response.status, 200);
  assert.equal(receivedUrl, "/predictions?page=2&prediction=0");
});
test("proxy forwards the prediction body without changing feature values", async () => {
  const body = JSON.stringify({ features: { Time: 12.5 } });
  const response = await POST(
    new NextRequest("http://localhost/api/backend/predict", {
      method: "POST",
      body,
    }),
    { params: Promise.resolve({ path: ["predict"] }) },
  );
  assert.equal(response.status, 200);
  assert.equal(receivedUrl, "/predict");
  assert.equal(receivedBody, body);
});
test("proxy preserves backend validation and not-found status", async () => {
  const invalid = await GET(
    new NextRequest(
      "http://localhost/api/backend/predictions?model_version=invalid",
    ),
    { params: Promise.resolve({ path: ["predictions"] }) },
  );
  assert.equal(invalid.status, 422);
  assert.equal((await invalid.json()).detail, "Filtro inválido");
  const missing = await GET(
    new NextRequest(
      "http://localhost/api/backend/predictions/00000000-0000-4000-8000-000000000001",
    ),
    {
      params: Promise.resolve({
        path: ["predictions", "00000000-0000-4000-8000-000000000001"],
      }),
    },
  );
  assert.equal(missing.status, 404);
});
test("proxy restricts paths and hides internal backend diagnostics", async () => {
  const blocked = await GET(
    new NextRequest("http://localhost/api/backend/metrics"),
    { params: Promise.resolve({ path: ["metrics"] }) },
  );
  assert.equal(blocked.status, 404);
  const failed = await GET(
    new NextRequest(
      "http://localhost/api/backend/predictions?model_version=broken",
    ),
    { params: Promise.resolve({ path: ["predictions"] }) },
  );
  assert.equal(failed.status, 500);
  assert.equal(
    JSON.stringify(await failed.json()).includes("private diagnostic"),
    false,
  );
});
test("proxy returns an honest unavailable state for a failed connection", async () => {
  process.env.API_URL = "http://127.0.0.1:1";
  try {
    const response = await GET(
      new NextRequest("http://localhost/api/backend/health"),
      { params: Promise.resolve({ path: ["health"] }) },
    );
    assert.equal(response.status, 503);
  } finally {
    process.env.API_URL = base;
  }
});
