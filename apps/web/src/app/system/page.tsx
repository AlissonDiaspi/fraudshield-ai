"use client";

import {
  Activity,
  Box,
  CircleCheck,
  Info,
  RefreshCw,
  Server,
  ShieldCheck,
} from "lucide-react";
import { useHealth } from "@/components/health-provider";
import { Button } from "@/components/ui/button";
import {
  ErrorState,
  LoadingSkeleton,
  PageHeader,
  Panel,
  PanelHeader,
} from "@/components/shared";
import { cn } from "@/lib/utils";

export default function System() {
  const { data, error, loading, reload } = useHealth();
  const healthy = data?.status === "healthy" && data.model_loaded;
  return (
    <div className="entry space-y-6">
      <PageHeader
        eyebrow="Disponibilidade"
        title="Status do sistema"
        description="Acompanhe a disponibilidade da API e o carregamento do modelo de predição."
        action={
          <Button variant="outline" onClick={reload} disabled={loading}>
            <RefreshCw className={loading ? "animate-spin" : ""} />
            Verificar agora
          </Button>
        }
      />
      {error && <ErrorState message={error.message} onRetry={reload} />}
      <Panel>
        <div className="flex flex-col items-start gap-5 p-6 sm:flex-row sm:items-center sm:p-8">
          <div
            className={cn(
              "grid size-16 shrink-0 place-items-center rounded-2xl border",
              error
                ? "border-destructive/20 bg-destructive/5 text-coral"
                : healthy
                  ? "border-success/20 bg-success/5 text-success"
                  : "border-amber/20 bg-amber/5 text-amber",
            )}
          >
            <Activity className="size-8" strokeWidth={1.4} />
          </div>
          <div>
            <p className="eyebrow">Disponibilidade do serviço</p>
            <h2
              className="text-xl font-medium tracking-tight"
              aria-live="polite"
            >
              {loading && !data
                ? "Verificando o serviço…"
                : error
                  ? "API indisponível"
                  : healthy
                    ? "API operacional"
                    : "Serviço com restrições"}
            </h2>
            <p className="mt-2 text-xs leading-relaxed text-muted-foreground">
              Consulta automática a cada 60 segundos. Atualize a verificação
              quando precisar.
            </p>
          </div>
        </div>
      </Panel>
      {loading && !data ? (
        <Panel>
          <LoadingSkeleton rows={3} />
        </Panel>
      ) : (
        <div className="grid gap-4 md:grid-cols-3">
          {[
            {
              title: "Conexão com a API",
              icon: Server,
              value: error
                ? "Indisponível"
                : data
                  ? "Conectada"
                  : "Não verificada",
              detail: "Resposta do endpoint de saúde da aplicação",
              ok: !!data && !error,
            },
            {
              title: "Modelo de predição",
              icon: Box,
              value:
                data && !error
                  ? data.model_loaded
                    ? "Carregado"
                    : "Não carregado"
                  : "Não verificado",
              detail: "Indicação de modelo carregado no health check",
              ok: !!data?.model_loaded && !error,
            },
            {
              title: "Serviço de predição",
              icon: ShieldCheck,
              value:
                data && !error
                  ? healthy
                    ? "Disponível no health check"
                    : "Com restrições"
                  : "Não verificado",
              detail: "Disponibilidade informada, sem executar uma análise",
              ok: !!healthy && !error,
            },
          ].map(({ title, icon: Icon, value, detail, ok }) => (
            <Panel key={title} className="p-6">
              <Icon className="mb-6 size-5 text-muted-foreground" />
              <p className="text-xs text-muted-foreground">{title}</p>
              <p
                className={cn(
                  "mt-3 flex items-center gap-2 text-sm font-medium",
                  ok ? "text-success" : "text-amber",
                )}
              >
                {ok && <CircleCheck className="size-4 shrink-0" />}
                {value}
              </p>
              <p className="mt-3 text-xs leading-relaxed text-muted-foreground">
                {detail}
              </p>
            </Panel>
          ))}
        </div>
      )}
      {data && !error && (
        <Panel>
          <PanelHeader
            title="Informações do health check"
            description="Dados efetivamente retornados pela API"
          />
          <dl className="grid gap-6 p-6 sm:grid-cols-3">
            <div>
              <dt className="field-label">Serviço</dt>
              <dd className="break-all font-mono text-sm">{data.service}</dd>
            </div>
            <div>
              <dt className="field-label">Status reportado</dt>
              <dd className="break-all font-mono text-sm">{data.status}</dd>
            </div>
            <div>
              <dt className="field-label">Modelo carregado</dt>
              <dd className="font-mono text-sm">
                {data.model_loaded ? "Sim" : "Não"}
              </dd>
            </div>
          </dl>
        </Panel>
      )}
      <div className="flex gap-3 rounded-xl border border-border bg-card/40 p-5">
        <Info className="mt-0.5 size-4 shrink-0 text-primary" />
        <p className="text-xs leading-relaxed text-muted-foreground">
          Esta página reflete o health check da API. A saúde de PostgreSQL,
          Kafka, MLflow e dos serviços de observabilidade não é verificada por
          esse endpoint. A observabilidade técnica continua no Grafana.
        </p>
      </div>
    </div>
  );
}
