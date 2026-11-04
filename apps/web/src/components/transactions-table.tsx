import Link from "next/link";
import { ArrowUpRight, Fingerprint } from "lucide-react";
import type { HistoryItem } from "@/lib/api/contracts";
import { dateTime } from "@/lib/utils";
import { EmptyState, RiskScore, StatusBadge } from "@/components/shared";
import { Button } from "@/components/ui/button";

export function TransactionsTable({
  items,
  filtered = false,
}: {
  items: HistoryItem[];
  filtered?: boolean;
}) {
  if (!items.length)
    return (
      <EmptyState
        title={filtered ? "Nenhum resultado para estes filtros" : undefined}
        description={
          filtered
            ? "Ajuste o período ou os filtros para ampliar a busca."
            : undefined
        }
        action={
          !filtered && (
            <Button asChild variant="outline">
              <Link href="/analyze">
                Analisar uma transação
                <ArrowUpRight />
              </Link>
            </Button>
          )
        }
      />
    );
  return (
    <>
      <div className="hidden overflow-x-auto md:block">
        <table className="data-table">
          <caption className="sr-only">
            Previsões de transações financeiras
          </caption>
          <thead>
            <tr>
              <th>IDENTIFICADOR</th>
              <th>DATA E HORA</th>
              <th>CLASSIFICAÇÃO</th>
              <th>SCORE DE FRAUDE</th>
              <th>MODELO</th>
              <th>
                <span className="sr-only">Detalhes</span>
              </th>
            </tr>
          </thead>
          <tbody>
            {items.map((item) => (
              <tr key={item.id}>
                <td>
                  <Link
                    href={`/transactions/${item.id}`}
                    className="inline-flex items-center gap-2 font-mono text-xs hover:text-primary"
                  >
                    <Fingerprint className="size-4 text-muted-foreground" />
                    {item.id.slice(0, 8)}
                    <span className="text-muted-foreground">…</span>
                  </Link>
                </td>
                <td className="whitespace-nowrap text-muted-foreground">
                  {dateTime(item.created_at)}
                </td>
                <td>
                  <StatusBadge prediction={item.prediction} />
                </td>
                <td>
                  <RiskScore score={item.fraud_score} />
                </td>
                <td>
                  <span className="break-all rounded border border-border bg-background/30 px-2 py-1 font-mono text-[10px] text-muted-foreground">
                    v{item.model_version}
                  </span>
                </td>
                <td>
                  <Button asChild variant="ghost" size="icon">
                    <Link
                      href={`/transactions/${item.id}`}
                      aria-label={`Ver detalhes da previsão ${item.id}`}
                    >
                      <ArrowUpRight />
                    </Link>
                  </Button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <div className="divide-y divide-border md:hidden">
        {items.map((item) => (
          <article key={item.id} className="space-y-4 p-5">
            <div className="flex flex-wrap items-center justify-between gap-2">
              <Link
                href={`/transactions/${item.id}`}
                className="inline-flex min-h-10 items-center gap-2 font-mono text-xs text-primary"
              >
                {item.id.slice(0, 8)}…<ArrowUpRight className="size-4" />
                <span className="sr-only">Ver detalhes</span>
              </Link>
              <StatusBadge prediction={item.prediction} />
            </div>
            <RiskScore score={item.fraud_score} />
            <div className="flex flex-wrap items-center justify-between gap-2 text-xs text-muted-foreground">
              <time dateTime={item.created_at}>
                {dateTime(item.created_at)}
              </time>
              <span className="break-all font-mono">
                Modelo v{item.model_version}
              </span>
            </div>
          </article>
        ))}
      </div>
    </>
  );
}
