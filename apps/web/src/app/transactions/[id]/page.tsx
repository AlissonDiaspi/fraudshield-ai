"use client";

import { use } from "react";
import Link from "next/link";
import { ArrowLeft, Fingerprint, ShieldCheck } from "lucide-react";
import { useResource } from "@/hooks/use-resource";
import { historyItemSchema } from "@/lib/api/contracts";
import { dateTime, percent } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import {
  EmptyState,
  ErrorState,
  LoadingSkeleton,
  PageHeader,
  Panel,
  PanelHeader,
  RiskScore,
  StatusBadge,
} from "@/components/shared";

export default function TransactionDetail({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = use(params);
  const { data, error, loading, reload } = useResource(
    `/predictions/${encodeURIComponent(id)}`,
    historyItemSchema,
  );
  return (
    <div className="entry space-y-6">
      <PageHeader
        eyebrow="Rastreabilidade / Detalhes"
        title="Detalhes da transação"
        description="O registro completo da previsão, dos dados de entrada à classificação."
        action={
          <Button asChild variant="outline">
            <Link href="/transactions">
              <ArrowLeft />
              Voltar ao histórico
            </Link>
          </Button>
        }
      />
      {loading ? (
        <Panel>
          <LoadingSkeleton rows={6} />
        </Panel>
      ) : error?.status === 404 ? (
        <Panel>
          <EmptyState
            title="Previsão não encontrada"
            description="Não há uma previsão com este identificador. Verifique o endereço ou consulte o histórico."
          />
        </Panel>
      ) : error ? (
        <ErrorState message={error.message} onRetry={reload} />
      ) : (
        data && (
          <>
            <div className="grid gap-6 xl:grid-cols-[1.4fr_1fr]">
              <Panel>
                <PanelHeader
                  title="Registro da previsão"
                  action={<Fingerprint className="size-5 text-primary" />}
                />
                <dl className="grid gap-6 p-6 sm:grid-cols-2">
                  <div className="sm:col-span-2">
                    <dt className="field-label">Identificador</dt>
                    <dd className="break-all font-mono text-sm">{data.id}</dd>
                  </div>
                  <div>
                    <dt className="field-label">Data e hora</dt>
                    <dd className="text-sm">{dateTime(data.created_at)}</dd>
                  </div>
                  <div>
                    <dt className="field-label">Classificação</dt>
                    <dd>
                      <StatusBadge prediction={data.prediction} />
                    </dd>
                  </div>
                  <div>
                    <dt className="field-label">Versão do modelo</dt>
                    <dd className="break-all font-mono text-sm">
                      {data.model_version}
                    </dd>
                  </div>
                  <div>
                    <dt className="field-label">Threshold aplicado</dt>
                    <dd className="font-mono text-sm">
                      {percent(data.threshold)}
                    </dd>
                  </div>
                </dl>
              </Panel>
              <Panel>
                <PanelHeader
                  title="Resultado da análise"
                  action={<ShieldCheck className="size-5 text-primary" />}
                />
                <div className="space-y-6 p-6">
                  <p className="font-mono text-5xl tracking-tight">
                    {percent(data.fraud_score)}
                  </p>
                  <RiskScore score={data.fraud_score} />
                  <p className="text-xs leading-relaxed text-muted-foreground">
                    Score estimado de fraude para esta transação. A
                    classificação exibida é a decisão retornada pelo modelo com
                    o threshold registrado.
                  </p>
                </div>
              </Panel>
            </div>
            <Panel>
              <PanelHeader
                title="Dados utilizados na análise"
                description={`${Object.keys(data.features).length} features registradas nesta previsão`}
              />
              <dl className="grid grid-cols-2 gap-px bg-border sm:grid-cols-3 lg:grid-cols-5">
                {Object.entries(data.features)
                  .sort(([a], [b]) => {
                    const order = (name: string) =>
                      name === "Time"
                        ? -2
                        : name === "Amount"
                          ? -1
                          : Number(name.slice(1));
                    return order(a) - order(b);
                  })
                  .map(([name, value]) => (
                    <div key={name} className="min-w-0 bg-card p-5">
                      <dt className="text-[10px] text-muted-foreground">
                        {name}
                      </dt>
                      <dd className="mt-2 break-all font-mono text-xs">
                        {String(value)}
                      </dd>
                    </div>
                  ))}
              </dl>
            </Panel>
          </>
        )
      )}
    </div>
  );
}
