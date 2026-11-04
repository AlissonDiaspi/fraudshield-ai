"use client";

import { Cell, Pie, PieChart, ResponsiveContainer, Tooltip } from "recharts";
import type { Overview } from "@/lib/api/contracts";
import { number, percent } from "@/lib/utils";
import { EmptyState } from "@/components/shared";
import { useReducedMotion } from "@/hooks/use-reduced-motion";

export function DistributionChart({ data }: { data: Overview }) {
  const reducedMotion = useReducedMotion();
  if (!data.total_predictions)
    return (
      <EmptyState
        title="A distribuição começa na primeira análise"
        description="As classificações das transações registradas serão exibidas aqui."
      />
    );
  const chartData = [
    { name: "Legítimas", value: data.legitimate_predictions, color: "#46d6a0" },
    { name: "Alertas de fraude", value: data.fraud_alerts, color: "#f88c95" },
  ];
  return (
    <div className="flex flex-col items-center gap-4 px-6 py-6 sm:flex-row sm:gap-8">
      <div
        role="img"
        aria-label={`${number(data.legitimate_predictions)} legítimas e ${number(data.fraud_alerts)} alertas de fraude`}
        className="relative h-[220px] w-[220px] shrink-0"
      >
        <ResponsiveContainer width="100%" height="100%" minWidth={0}>
          <PieChart>
            <Pie
              data={chartData}
              dataKey="value"
              nameKey="name"
              innerRadius={77}
              outerRadius={96}
              paddingAngle={
                data.fraud_alerts && data.legitimate_predictions ? 4 : 0
              }
              stroke="none"
              isAnimationActive={!reducedMotion}
              animationDuration={600}
            >
              {chartData.map((item) => (
                <Cell key={item.name} fill={item.color} />
              ))}
            </Pie>
            <Tooltip
              content={({ active, payload }) =>
                active && payload?.length ? (
                  <div className="rounded-lg border border-border bg-popover p-3 text-xs shadow-xl">
                    <p className="text-muted-foreground">{payload[0].name}</p>
                    <p className="mt-1 font-mono">
                      {number(Number(payload[0].value))}{" "}
                      {Number(payload[0].value) === 1
                        ? "transação"
                        : "transações"}
                    </p>
                  </div>
                ) : null
              }
            />
          </PieChart>
        </ResponsiveContainer>
        <div className="pointer-events-none absolute inset-0 flex flex-col items-center justify-center">
          <span className="font-mono text-3xl font-medium tracking-tight">
            {number(data.total_predictions)}
          </span>
          <span className="mt-2 text-[10px] text-muted-foreground">
            transações analisadas
          </span>
        </div>
      </div>
      <div className="w-full flex-1 space-y-5">
        {chartData.map((item) => (
          <div key={item.name}>
            <div className="flex items-center justify-between gap-3">
              <span className="flex items-center gap-2 text-xs text-muted-foreground">
                <span
                  className="size-2 rounded-full"
                  style={{ background: item.color }}
                />
                {item.name}
              </span>
              <span className="font-mono text-sm">
                {percent(item.value / data.total_predictions)}
              </span>
            </div>
            <p className="ml-4 mt-2 text-xs text-muted-foreground">
              {number(item.value)}{" "}
              {item.value === 1 ? "transação" : "transações"}
            </p>
          </div>
        ))}
        <p className="border-t border-border pt-4 text-[10px] leading-relaxed text-muted-foreground">
          Distribuição de todas as previsões armazenadas.
        </p>
      </div>
    </div>
  );
}
