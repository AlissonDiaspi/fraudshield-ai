"use client";

import { useState } from "react";
import Link from "next/link";
import {
  ArrowUpRight,
  ChevronLeft,
  ChevronRight,
  ScanLine,
} from "lucide-react";
import { useResource } from "@/hooks/use-resource";
import { historySchema } from "@/lib/api/contracts";
import { historyPath, type HistoryFilters } from "@/lib/api/predictions";
import { number } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import {
  ErrorState,
  LoadingSkeleton,
  PageHeader,
  Panel,
  PanelHeader,
} from "@/components/shared";
import { TransactionsTable } from "@/components/transactions-table";
import { TransactionFilters } from "@/components/transaction-filters";

export default function Transactions() {
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(20);
  const [filters, setFilters] = useState<HistoryFilters>({});
  const { data, error, loading, reload } = useResource(
    historyPath(page, pageSize, filters),
    historySchema,
  );
  const filtered = Object.values(filters).some(Boolean);
  return (
    <div className="entry">
      <PageHeader
        eyebrow="Rastreabilidade"
        title="Histórico de transações"
        description="Consulte as previsões registradas e acompanhe cada decisão do modelo."
        action={
          <Button asChild>
            <Link href="/analyze">
              <ScanLine />
              Nova análise
              <ArrowUpRight />
            </Link>
          </Button>
        }
      />
      <Panel>
        <PanelHeader
          title="Previsões registradas"
          description={
            data && !loading
              ? `${number(data.total)} ${data.total === 1 ? "registro encontrado" : "registros encontrados"}`
              : "Consulte e filtre os registros da operação"
          }
        />
        <TransactionFilters
          onApply={(next) => {
            setFilters(next);
            setPage(1);
          }}
        />
        {loading ? (
          <LoadingSkeleton rows={5} />
        ) : error ? (
          <div className="p-5">
            <ErrorState message={error.message} onRetry={reload} />
          </div>
        ) : (
          data && <TransactionsTable items={data.items} filtered={filtered} />
        )}
        <div className="flex flex-col justify-between gap-4 border-t border-border p-5 text-xs text-muted-foreground sm:flex-row sm:items-center">
          <div className="flex items-center gap-3">
            <label htmlFor="page-size">Por página</label>
            <select
              id="page-size"
              className="select-input w-20"
              value={pageSize}
              onChange={(event) => {
                setPageSize(Number(event.target.value));
                setPage(1);
              }}
            >
              <option value={10}>10</option>
              <option value={20}>20</option>
              <option value={50}>50</option>
              <option value={100}>100</option>
            </select>
          </div>
          <div className="flex flex-wrap items-center gap-3">
            <span aria-live="polite">
              {data && !loading
                ? data.total_pages
                  ? `Página ${data.page} de ${data.total_pages}`
                  : "Nenhuma página"
                : "Aguardando resultados"}
            </span>
            <Button
              variant="outline"
              size="icon"
              aria-label="Página anterior"
              disabled={loading || !data || data.page <= 1 || !!error}
              onClick={() => setPage(data ? data.page - 1 : 1)}
            >
              <ChevronLeft />
            </Button>
            <Button
              variant="outline"
              size="icon"
              aria-label="Próxima página"
              disabled={
                loading || !data || data.page >= data.total_pages || !!error
              }
              onClick={() => setPage(data ? data.page + 1 : 1)}
            >
              <ChevronRight />
            </Button>
          </div>
        </div>
      </Panel>
    </div>
  );
}
