"use client";

import { useState } from "react";
import { Filter, RotateCcw } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import type { HistoryFilters } from "@/lib/api/predictions";

export function TransactionFilters({
  onApply,
}: {
  onApply: (filters: HistoryFilters) => void;
}) {
  const [error, setError] = useState("");
  function submit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    const start = String(form.get("start_date") || "");
    const end = String(form.get("end_date") || "");
    if (start && end && new Date(start) > new Date(end)) {
      setError("A data inicial deve ser anterior ou igual à data final.");
      return;
    }
    setError("");
    onApply({
      prediction: String(form.get("prediction") || ""),
      model_version: String(form.get("model_version") || "").trim(),
      start_date: start ? new Date(start).toISOString() : "",
      end_date: end ? new Date(end).toISOString() : "",
    });
  }
  return (
    <form
      onSubmit={submit}
      onReset={() => {
        setError("");
        onApply({});
      }}
      className="space-y-4 border-b border-border bg-background/15 p-5 sm:p-6"
    >
      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <div>
          <label htmlFor="classification" className="field-label">
            Classificação
          </label>
          <select
            id="classification"
            name="prediction"
            className="select-input"
          >
            <option value="">Todas as classificações</option>
            <option value="0">Legítima</option>
            <option value="1">Alerta de fraude</option>
          </select>
        </div>
        <div>
          <label htmlFor="model-version" className="field-label">
            Versão do modelo
          </label>
          <Input
            id="model-version"
            name="model_version"
            placeholder="Digite a versão exata"
            maxLength={128}
          />
        </div>
        <div>
          <label htmlFor="start-date" className="field-label">
            Data e hora inicial
          </label>
          <Input id="start-date" name="start_date" type="datetime-local" />
        </div>
        <div>
          <label htmlFor="end-date" className="field-label">
            Data e hora final
          </label>
          <Input id="end-date" name="end_date" type="datetime-local" />
        </div>
      </div>
      <div className="flex flex-wrap items-center justify-between gap-4">
        <p className="text-[11px] leading-relaxed text-muted-foreground">
          Datas no fuso horário do seu navegador. Enviadas à API em UTC.
        </p>
        <div className="flex gap-2">
          <Button type="reset" size="sm" variant="ghost">
            <RotateCcw />
            Limpar
          </Button>
          <Button type="submit" size="sm">
            <Filter />
            Aplicar filtros
          </Button>
        </div>
      </div>
      {error && (
        <p role="alert" className="field-error">
          {error}
        </p>
      )}
    </form>
  );
}
