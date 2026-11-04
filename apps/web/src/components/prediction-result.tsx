import Link from "next/link";
import { ArrowRight, Check, RotateCcw, ShieldAlert } from "lucide-react";
import type { Prediction } from "@/lib/api/contracts";
import { percent } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import {
  Panel,
  PanelHeader,
  RiskScore,
  StatusBadge,
} from "@/components/shared";

export function PredictionResult({
  result,
  onReset,
}: {
  result: Prediction;
  onReset: () => void;
}) {
  const fraud = result.prediction === 1;
  return (
    <Panel className="entry">
      <PanelHeader
        title="Resultado da análise"
        description="Previsão concluída e registrada"
        action={
          <span
            role="status"
            className="flex items-center gap-1 text-[10px] text-success"
          >
            <Check className="size-3" />
            Concluída
          </span>
        }
      />
      <div className="space-y-6 p-6">
        <div
          className={`grid size-14 place-items-center rounded-2xl border ${fraud ? "border-destructive/20 bg-destructive/10 text-coral" : "border-success/20 bg-success/10 text-success"}`}
        >
          {fraud ? (
            <ShieldAlert className="size-7" />
          ) : (
            <Check className="size-7" />
          )}
        </div>
        <div>
          <StatusBadge prediction={result.prediction} />
          <p className="mt-4 text-xs text-muted-foreground">
            Score estimado de fraude
          </p>
          <p className="mt-2 break-all font-mono text-4xl tracking-tight">
            {percent(result.fraud_score)}
          </p>
        </div>
        <RiskScore score={result.fraud_score} />
        <dl className="space-y-4 border-t border-border pt-5">
          <div>
            <dt className="field-label">Versão do modelo</dt>
            <dd className="break-all font-mono text-xs">
              {result.model_version}
            </dd>
          </div>
          <div>
            <dt className="field-label">Threshold aplicado</dt>
            <dd className="font-mono text-xs">{percent(result.threshold)}</dd>
          </div>
          <div>
            <dt className="field-label">Identificador da previsão</dt>
            <dd className="break-all font-mono text-xs text-muted-foreground">
              {result.id}
            </dd>
          </div>
          <div>
            <dt className="field-label">Classificação do serviço</dt>
            <dd className="break-all font-mono text-xs text-muted-foreground">
              {result.classification}
            </dd>
          </div>
        </dl>
        <p className="text-xs leading-relaxed text-muted-foreground">
          Esta é uma classificação automatizada de risco. Considere o contexto
          da operação ao avaliar o resultado.
        </p>
        <div className="flex flex-col gap-2">
          <Button asChild>
            <Link href={`/transactions/${result.id}`}>
              Ver registro completo
              <ArrowRight />
            </Link>
          </Button>
          <Button variant="outline" onClick={onReset}>
            <RotateCcw />
            Realizar nova análise
          </Button>
        </div>
      </div>
    </Panel>
  );
}
