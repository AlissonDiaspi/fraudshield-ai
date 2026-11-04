"use client";

import Link from "next/link";
import {
  ArrowRight,
  ArrowUpRight,
  ChartNoAxesCombined,
  CircleCheck,
  RefreshCw,
  ScanLine,
  ShieldAlert,
  ShieldCheck,
} from "lucide-react";
import { useResource } from "@/hooks/use-resource";
import { historySchema, overviewSchema } from "@/lib/api/contracts";
import { historyPath } from "@/lib/api/predictions";
import { dateTime, number, percent } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import {
  ErrorState,
  LoadingSkeleton,
  PageHeader,
  Panel,
  PanelHeader,
  RiskScore,
  StatCard,
} from "@/components/shared";
import { DistributionChart } from "@/components/distribution-chart";
import { TransactionsTable } from "@/components/transactions-table";

export default function Dashboard() {
  const overview = useResource("/statistics/overview", overviewSchema);
  const recent = useResource(historyPath(1, 5), historySchema);
  const data = overview.data;
  const refresh = () => {
    overview.reload();
    recent.reload();
  };
  return (
    <div className="entry space-y-6">
      <PageHeader
        eyebrow="Centro de operações"
        title="Visão geral"
        description="Clareza para acompanhar transações. Inteligência para identificar riscos."
        action={
          <>
            <Button
              variant="outline"
              size="icon"
              onClick={refresh}
              disabled={overview.loading || recent.loading}
              aria-label="Atualizar dashboard"
            >
              <RefreshCw className={overview.loading ? "animate-spin" : ""} />
            </Button>
            <Button asChild>
              <Link href="/analyze">
                <ScanLine />
                Analisar transação
                <ArrowUpRight />
              </Link>
            </Button>
          </>
        }
      />
      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <StatCard
          title="Transações analisadas"
          value={data ? number(data.total_predictions) : "—"}
          detail="Total de previsões registradas"
          icon={<ChartNoAxesCombined />}
          loading={overview.loading}
        />
        <StatCard
          title="Transações legítimas"
          value={data ? number(data.legitimate_predictions) : "—"}
          detail="Classificadas sem alerta de fraude"
          icon={<CircleCheck />}
          tone="success"
          loading={overview.loading}
        />
        <StatCard
          title="Alertas de fraude"
          value={data ? number(data.fraud_alerts) : "—"}
          detail="Transações classificadas como fraude"
          icon={<ShieldAlert />}
          tone="coral"
          loading={overview.loading}
        />
        <StatCard
          title="Taxa de alertas"
          value={data ? percent(data.alert_rate) : "—"}
          detail="Proporção das classificações como fraude"
          icon={<ChartNoAxesCombined />}
          tone="amber"
          loading={overview.loading}
          tooltip="Alertas divididos pelo total de previsões. Esta taxa não representa a precisão do modelo."
        />
      </div>
      {overview.error && (
        <ErrorState
          message={overview.error.message}
          onRetry={overview.reload}
        />
      )}
      <div className="grid items-stretch gap-6 xl:grid-cols-[1.5fr_1fr]">
        <Panel>
          <PanelHeader
            title="Distribuição das classificações"
            description="Uma visão consolidada das análises realizadas"
            action={
              <span className="rounded-md border border-border bg-background/40 px-2 py-1 text-[10px] text-muted-foreground">
                Todo o histórico
              </span>
            }
          />
          {overview.loading ? (
            <LoadingSkeleton rows={3} />
          ) : data ? (
            <DistributionChart data={data} />
          ) : (
            <div className="flex min-h-64 items-center justify-center p-8 text-center text-sm text-muted-foreground">
              A distribuição estará disponível quando a conexão com a API for
              restabelecida.
            </div>
          )}
        </Panel>
        <Panel>
          <PanelHeader
            title="Leitura de risco"
            description="Contexto para acompanhar sua operação"
          />
          <div className="space-y-6 p-6">
            <div className="flex items-center gap-3">
              <span className="grid size-10 place-items-center rounded-xl border border-primary/15 bg-primary/5 text-primary">
                <ShieldCheck className="size-5" />
              </span>
              <div>
                <p className="text-xs text-muted-foreground">
                  Score médio de fraude
                </p>
                <p className="mt-1 font-mono text-2xl">
                  {data && data.total_predictions
                    ? percent(data.average_fraud_score)
                    : "—"}
                </p>
              </div>
            </div>
            {data && data.total_predictions > 0 && (
              <RiskScore score={data.average_fraud_score} />
            )}
            <div className="border-t border-border pt-5">
              <p className="text-[10px] uppercase tracking-widest text-muted-foreground">
                Última análise registrada
              </p>
              <p className="mt-2 text-sm">
                {data
                  ? dateTime(data.last_prediction_at)
                  : "Aguardando conexão com a API"}
              </p>
            </div>
            <p className="text-[11px] leading-relaxed text-muted-foreground">
              O score expressa a estimativa de fraude do modelo. A classificação
              considera o threshold utilizado em cada análise.
            </p>
          </div>
        </Panel>
      </div>
      <Panel>
        <PanelHeader
          title="Transações recentes"
          description="As últimas previsões registradas na operação"
          action={
            <Button asChild variant="ghost" size="sm">
              <Link href="/transactions">
                Ver histórico
                <ArrowRight />
              </Link>
            </Button>
          }
        />
        {recent.loading ? (
          <LoadingSkeleton rows={4} />
        ) : recent.error ? (
          <div className="p-5">
            <ErrorState
              message={recent.error.message}
              onRetry={recent.reload}
            />
          </div>
        ) : (
          recent.data && <TransactionsTable items={recent.data.items} />
        )}
      </Panel>
      <div className="flex flex-col justify-between gap-4 rounded-xl border border-primary/15 bg-gradient-to-r from-primary/[.065] to-transparent p-5 sm:flex-row sm:items-center">
        <div className="flex gap-4">
          <span className="mt-1 text-primary">
            <ScanLine className="size-6" strokeWidth={1.5} />
          </span>
          <div>
            <p className="text-sm font-medium">
              A próxima decisão começa com uma análise.
            </p>
            <p className="mt-1 text-xs leading-relaxed text-muted-foreground">
              Envie os dados de uma transação e consulte a classificação do
              modelo.
            </p>
          </div>
        </div>
        <Button asChild variant="outline" size="sm">
          <Link href="/analyze">
            Nova análise
            <ArrowUpRight />
          </Link>
        </Button>
      </div>
    </div>
  );
}
