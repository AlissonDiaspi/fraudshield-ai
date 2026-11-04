"use client";

import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import {
  Braces,
  ChevronDown,
  FileCheck2,
  Info,
  LoaderCircle,
  ScanLine,
  ShieldCheck,
} from "lucide-react";
import {
  predictionRequestSchema,
  type Prediction,
  type PredictionRequest,
} from "@/lib/api/contracts";
import { predict } from "@/lib/api/predictions";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  EmptyState,
  ErrorState,
  PageHeader,
  Panel,
  PanelHeader,
} from "@/components/shared";
import { PredictionResult } from "@/components/prediction-result";

const groups = Array.from({ length: 4 }, (_, group) =>
  Array.from({ length: 7 }, (_, index) => `V${group * 7 + index + 1}`),
);
export default function Analyze() {
  const [result, setResult] = useState<Prediction | null>(null);
  const [error, setError] = useState("");
  const [json, setJson] = useState("");
  const [jsonError, setJsonError] = useState("");
  const [revealErrors, setRevealErrors] = useState(false);
  const {
    register,
    handleSubmit,
    reset,
    formState: { errors, isSubmitting },
  } = useForm<PredictionRequest>({
    resolver: zodResolver(predictionRequestSchema),
    defaultValues: { features: {} },
    shouldFocusError: true,
  });
  function importJson() {
    try {
      const parsed: unknown = JSON.parse(json);
      const payload = predictionRequestSchema.safeParse(parsed);
      if (!payload.success) {
        setJsonError(
          "Informe o objeto { features: { ... } } com Time, Amount e V1 a V28, todos numéricos e finitos. Time e Amount não podem ser negativos.",
        );
        return;
      }
      reset(payload.data);
      setResult(null);
      setJsonError("");
      setError("");
    } catch {
      setJsonError("JSON inválido. Verifique a sintaxe do conteúdo colado.");
    }
  }
  async function submit(payload: PredictionRequest) {
    setError("");
    setResult(null);
    try {
      setResult(await predict(payload));
    } catch (cause) {
      setError(
        cause instanceof Error
          ? cause.message
          : "Não foi possível analisar a transação.",
      );
    }
  }
  function newAnalysis() {
    reset({ features: {} });
    setResult(null);
    setError("");
    setJson("");
    setRevealErrors(false);
  }
  function numericField(name: string, label = name, help?: string) {
    const message = errors.features?.[name]?.message;
    return (
      <div key={name}>
        <label className="field-label" htmlFor={`feature-${name}`}>
          {label}
          <span className="ml-1 text-primary" aria-hidden="true">
            *
          </span>
        </label>
        <Input
          id={`feature-${name}`}
          type="number"
          step="any"
          min={name === "Time" || name === "Amount" ? 0 : undefined}
          inputMode="decimal"
          placeholder="Informe o valor"
          aria-required="true"
          aria-invalid={!!message}
          aria-describedby={
            message ? `error-${name}` : help ? `help-${name}` : undefined
          }
          {...register(`features.${name}`, { valueAsNumber: true })}
        />
        {help && (
          <p id={`help-${name}`} className="field-help">
            {help}
          </p>
        )}
        {message && (
          <p id={`error-${name}`} className="field-error">
            {String(message)}
          </p>
        )}
      </div>
    );
  }
  return (
    <div className="entry">
      <PageHeader
        eyebrow="Motor de detecção"
        title="Analisar transação"
        description="Transforme os dados de uma transação em uma decisão informada sobre risco."
      />
      <div className="grid items-start gap-6 xl:grid-cols-[1.55fr_1fr]">
        <div className="space-y-5">
          <Panel>
            <PanelHeader
              title="Dados da transação"
              description="Preencha os valores reais utilizados pelo modelo"
              action={<ScanLine className="size-5 text-primary" />}
            />
            <div className="border-b border-border bg-primary/[.025] px-6 py-4">
              <p className="flex gap-2 text-xs leading-relaxed text-muted-foreground">
                <Info className="mt-0.5 size-4 shrink-0 text-primary" />
                Todos os 30 campos são obrigatórios. As features V1 a V28 devem
                vir da mesma transformação utilizada no treinamento.
              </p>
            </div>
            <form
              noValidate
              onSubmit={handleSubmit(submit, () => setRevealErrors(true))}
            >
              <fieldset disabled={isSubmitting} className="min-w-0">
                <div className="grid gap-5 p-6 sm:grid-cols-2">
                  {numericField(
                    "Time",
                    "Tempo (Time)",
                    "Tempo da transação conforme a origem dos dados.",
                  )}
                  {numericField(
                    "Amount",
                    "Valor (Amount)",
                    "Valor numérico na unidade original do dataset.",
                  )}
                </div>
                <div className="border-t border-border px-6 py-5">
                  <p className="mb-4 text-xs font-medium">
                    Componentes da transação
                  </p>
                  <div className="space-y-3">
                    {groups.map((group, index) => (
                      <details
                        key={index}
                        open={
                          revealErrors &&
                          group.some((name) => !!errors.features?.[name])
                            ? true
                            : undefined
                        }
                        className="group overflow-hidden rounded-lg border border-border bg-background/20"
                      >
                        <summary className="flex min-h-12 list-none items-center justify-between gap-2 px-4 text-xs [&::-webkit-details-marker]:hidden">
                          <span className="flex items-center gap-3">
                            <span className="font-mono text-[10px] text-primary">
                              0{index + 1}
                            </span>
                            Features {group[0]} a {group[group.length - 1]}
                          </span>
                          <ChevronDown className="size-4 text-muted-foreground transition-transform group-open:rotate-180" />
                        </summary>
                        <div className="grid gap-4 border-t border-border p-4 sm:grid-cols-2 lg:grid-cols-3">
                          {group.map((name) => numericField(name))}
                        </div>
                      </details>
                    ))}
                  </div>
                </div>
                <div className="flex flex-col items-start justify-between gap-4 border-t border-border p-6 sm:flex-row sm:items-center">
                  <span className="flex gap-2 text-[11px] text-muted-foreground">
                    <ShieldCheck className="size-4 shrink-0 text-primary" />A
                    análise será registrada no histórico.
                  </span>
                  <Button type="submit" disabled={isSubmitting}>
                    {isSubmitting ? (
                      <LoaderCircle className="animate-spin" />
                    ) : (
                      <ScanLine />
                    )}
                    {isSubmitting ? "Analisando…" : "Analisar transação"}
                  </Button>
                </div>
              </fieldset>
              {Object.keys(errors).length > 0 && (
                <p role="alert" className="px-6 pb-5 text-xs text-coral">
                  Revise os campos destacados. Todos os valores devem ser
                  números finitos.
                </p>
              )}
            </form>
          </Panel>
          <Panel>
            <details className="group">
              <summary className="flex min-h-14 list-none items-center justify-between gap-3 px-6 text-xs [&::-webkit-details-marker]:hidden">
                <span className="flex items-center gap-3">
                  <Braces className="size-4 text-primary" />
                  Já possui os dados em JSON?
                </span>
                <ChevronDown className="size-4 text-muted-foreground group-open:rotate-180" />
              </summary>
              <div className="space-y-4 border-t border-border p-6">
                <label htmlFor="json-input" className="field-label">
                  Cole o payload real da transação
                </label>
                <p className="text-xs leading-relaxed text-muted-foreground">
                  Use o formato da API: um objeto com a chave{" "}
                  <code className="text-primary">features</code>, contendo Time,
                  Amount e V1 a V28.
                </p>
                <textarea
                  id="json-input"
                  rows={7}
                  value={json}
                  onChange={(event) => setJson(event.target.value)}
                  className="w-full resize-y rounded-lg border border-input bg-background p-3 font-mono text-xs outline-none focus-visible:border-primary"
                  spellCheck={false}
                  disabled={isSubmitting}
                />
                <Button
                  variant="outline"
                  type="button"
                  disabled={isSubmitting || !json.trim()}
                  onClick={importJson}
                >
                  <FileCheck2 />
                  Preencher formulário
                </Button>
                {jsonError && (
                  <p role="alert" className="field-error">
                    {jsonError}
                  </p>
                )}
              </div>
            </details>
          </Panel>
        </div>
        <div className="space-y-5 xl:sticky xl:top-6" aria-live="polite">
          {error && (
            <ErrorState
              title="Não foi possível concluir a análise"
              message={error}
            />
          )}
          {result ? (
            <PredictionResult result={result} onReset={newAnalysis} />
          ) : (
            <Panel>
              <PanelHeader
                title="Resultado da análise"
                description="Uma leitura clara do risco da transação"
              />
              {isSubmitting ? (
                <div
                  role="status"
                  className="flex min-h-80 flex-col items-center justify-center gap-5 p-8"
                >
                  <LoaderCircle className="size-10 animate-spin text-primary" />
                  <p className="text-sm">Processando sua transação…</p>
                  <p className="text-center text-xs leading-relaxed text-muted-foreground">
                    Aguarde a classificação retornada pelo modelo.
                  </p>
                </div>
              ) : (
                <EmptyState
                  title="Pronto para uma nova análise"
                  description="Preencha os dados da transação ao lado. A classificação, o score e a versão do modelo aparecerão aqui."
                />
              )}
              <div className="border-t border-border px-6 py-5">
                <div className="mb-3 flex items-center gap-2 text-xs font-medium">
                  <ShieldCheck className="size-4 text-primary" />
                  Como interpretar o resultado
                </div>
                <p className="text-xs leading-relaxed text-muted-foreground">
                  O score indica a estimativa de fraude. A decisão entre
                  legítima e alerta de fraude considera o threshold do modelo
                  usado na análise.
                </p>
              </div>
            </Panel>
          )}
        </div>
      </div>
    </div>
  );
}
