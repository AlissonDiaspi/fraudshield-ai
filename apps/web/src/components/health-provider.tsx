"use client";

import { createContext, useContext } from "react";
import { healthSchema } from "@/lib/api/contracts";
import { useResource } from "@/hooks/use-resource";

type HealthState = ReturnType<
  typeof useResource<import("@/lib/api/contracts").Health>
>;
const HealthContext = createContext<HealthState | null>(null);
export function HealthProvider({ children }: { children: React.ReactNode }) {
  const resource = useResource("/health", healthSchema, 60000);
  return (
    <HealthContext.Provider value={resource}>{children}</HealthContext.Provider>
  );
}
export function useHealth() {
  const context = useContext(HealthContext);
  if (!context) throw new Error("HealthProvider ausente");
  return context;
}
export function ApiStatus() {
  const { data, error, loading } = useHealth();
  const ok = data?.status === "healthy" && data.model_loaded;
  return (
    <span
      role="status"
      className="flex items-center gap-2 text-xs text-muted-foreground"
    >
      <span
        className={`size-1.5 shrink-0 rounded-full ${error ? "bg-destructive" : loading && !data ? "bg-amber" : ok ? "bg-success shadow-[0_0_8px_#34d39950]" : "bg-amber"}`}
      />
      {error
        ? "API indisponível"
        : loading && !data
          ? "Verificando API"
          : ok
            ? "API operacional"
            : "API com restrições"}
    </span>
  );
}
