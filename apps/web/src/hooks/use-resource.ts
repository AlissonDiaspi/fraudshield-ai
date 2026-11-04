"use client";

import { useCallback, useEffect, useState } from "react";
import type { z } from "zod";
import { apiFetch, ApiError } from "@/lib/api/client";

type Resource<T> = { data: T | null; error: ApiError | null; loading: boolean };
export function useResource<T>(
  path: string,
  schema: z.ZodType<T>,
  interval?: number,
) {
  const [state, setState] = useState<Resource<T>>({
    data: null,
    error: null,
    loading: true,
  });
  const [revision, setRevision] = useState(0);
  const [resolvedPath, setResolvedPath] = useState(path);
  const reload = useCallback(() => setRevision((value) => value + 1), []);
  useEffect(() => {
    let active = true;
    const controller = new AbortController();
    async function load() {
      if (active) setState((old) => ({ ...old, loading: true, error: null }));
      try {
        const data = await apiFetch(path, schema, {
          signal: controller.signal,
        });
        if (active) {
          setState({ data, error: null, loading: false });
          setResolvedPath(path);
        }
      } catch (error) {
        if (active) {
          setState({
            data: null,
            error:
              error instanceof ApiError
                ? error
                : new ApiError("Ocorreu um erro ao carregar os dados."),
            loading: false,
          });
          setResolvedPath(path);
        }
      }
    }
    void load();
    const timer = interval
      ? setInterval(() => {
          void load();
        }, interval)
      : undefined;
    return () => {
      active = false;
      controller.abort();
      if (timer) clearInterval(timer);
    };
  }, [path, schema, revision, interval]);
  return { ...state, loading: state.loading || resolvedPath !== path, reload };
}
