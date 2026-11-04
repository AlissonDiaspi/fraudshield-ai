import type { ReactNode } from "react";
import {
  AlertTriangle,
  Check,
  Database,
  Info,
  RefreshCw,
  ShieldAlert,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Tooltip } from "@/components/ui/tooltip";
import { cn, percent } from "@/lib/utils";

export function PageHeader({
  eyebrow,
  title,
  description,
  action,
}: {
  eyebrow: string;
  title: string;
  description: string;
  action?: ReactNode;
}) {
  return (
    <div className="page-heading">
      <div>
        <p className="eyebrow">{eyebrow}</p>
        <h1>{title}</h1>
        <p className="mt-2 max-w-2xl text-sm leading-relaxed text-muted-foreground">
          {description}
        </p>
      </div>
      {action && (
        <div className="flex shrink-0 flex-wrap items-center gap-2">
          {action}
        </div>
      )}
    </div>
  );
}
export function Panel({
  children,
  className,
}: {
  children: ReactNode;
  className?: string;
}) {
  return <section className={cn("panel", className)}>{children}</section>;
}
export function PanelHeader({
  title,
  description,
  action,
}: {
  title: string;
  description?: string;
  action?: ReactNode;
}) {
  return (
    <div className="flex flex-wrap items-center justify-between gap-3 border-b border-border px-5 py-5 sm:px-6">
      <div>
        <h2 className="text-sm font-semibold tracking-wide">{title}</h2>
        {description && (
          <p className="mt-1 text-xs leading-relaxed text-muted-foreground">
            {description}
          </p>
        )}
      </div>
      {action}
    </div>
  );
}
export function StatusBadge({ prediction }: { prediction: number }) {
  const fraud = prediction === 1;
  return (
    <span
      className={cn(
        "badge",
        fraud
          ? "border-destructive/20 bg-destructive/10 text-coral"
          : "border-success/20 bg-success/10 text-success",
      )}
    >
      {fraud ? (
        <ShieldAlert className="size-3.5" />
      ) : (
        <Check className="size-3.5" />
      )}
      {fraud ? "Alerta de fraude" : "Legítima"}
    </span>
  );
}
export function RiskScore({
  score,
  className,
}: {
  score: number;
  className?: string;
}) {
  return (
    <div className={cn("min-w-24", className)}>
      <div className="mb-2 flex items-baseline justify-between gap-4 text-xs">
        <span className="text-muted-foreground">Score</span>
        <span className="font-mono text-foreground">{percent(score)}</span>
      </div>
      <div
        role="meter"
        aria-label="Score de fraude"
        aria-valuemin={0}
        aria-valuemax={100}
        aria-valuenow={Math.round(score * 100)}
        className="h-1.5 overflow-hidden rounded-full bg-muted"
      >
        <div
          style={{ width: `${Math.max(0, Math.min(1, score)) * 100}%` }}
          className="h-full rounded-full bg-primary"
        />
      </div>
    </div>
  );
}
export function EmptyState({
  title = "Nenhuma transação por aqui",
  description = "As análises registradas aparecerão nesta área.",
  action,
}: {
  title?: string;
  description?: string;
  action?: ReactNode;
}) {
  return (
    <div className="flex min-h-60 flex-col items-center justify-center px-6 py-10 text-center">
      <div className="mb-4 grid size-14 place-items-center rounded-2xl border border-border bg-accent/40">
        <Database className="size-6 text-muted-foreground" />
      </div>
      <h3 className="text-sm font-medium">{title}</h3>
      <p className="mt-2 max-w-sm text-sm leading-relaxed text-muted-foreground">
        {description}
      </p>
      {action && <div className="mt-5">{action}</div>}
    </div>
  );
}
export function ErrorState({
  message,
  onRetry,
  title = "Não foi possível carregar os dados",
}: {
  message: string;
  onRetry?: () => void;
  title?: string;
}) {
  return (
    <div
      role="alert"
      className="flex flex-col items-start gap-4 rounded-xl border border-destructive/20 bg-destructive/5 p-5 sm:flex-row sm:items-center"
    >
      <AlertTriangle className="size-5 shrink-0 text-coral" />
      <div className="flex-1">
        <h3 className="text-sm font-medium">{title}</h3>
        <p className="mt-1 text-sm leading-relaxed text-muted-foreground">
          {message}
        </p>
      </div>
      {onRetry && (
        <Button variant="outline" size="sm" onClick={onRetry}>
          <RefreshCw />
          Tentar novamente
        </Button>
      )}
    </div>
  );
}
export function LoadingSkeleton({ rows = 4 }: { rows?: number }) {
  return (
    <div role="status" aria-label="Carregando dados" className="space-y-4 p-6">
      <span className="sr-only">Carregando dados…</span>
      {Array.from({ length: rows }, (_, i) => (
        <div key={i} className="skeleton h-12" />
      ))}
    </div>
  );
}
export function StatCard({
  title,
  value,
  detail,
  icon,
  tone = "primary",
  loading,
  tooltip,
}: {
  title: string;
  value: string;
  detail: string;
  icon: ReactNode;
  tone?: "primary" | "success" | "coral" | "amber";
  loading?: boolean;
  tooltip?: string;
}) {
  return (
    <div className={cn("stat-card", `stat-${tone}`)}>
      <div className="flex items-center justify-between gap-3">
        <span className="text-xs font-medium text-muted-foreground">
          {title}
        </span>
        <span className="stat-icon">{icon}</span>
      </div>
      <div className="mt-4 flex items-baseline gap-2">
        {loading ? (
          <div className="skeleton h-9 w-28" />
        ) : (
          <p className="break-all font-mono text-3xl font-medium tracking-tight xl:text-[2rem]">
            {value}
          </p>
        )}
        {tooltip && (
          <Tooltip content={tooltip}>
            <button
              type="button"
              aria-label={`Sobre ${title}`}
              className="-my-3 inline-flex size-10 shrink-0 items-center justify-center rounded-lg text-muted-foreground"
            >
              <Info className="size-3.5" />
            </button>
          </Tooltip>
        )}
      </div>
      <p className="mt-3 text-xs leading-relaxed text-muted-foreground">
        {detail}
      </p>
    </div>
  );
}
