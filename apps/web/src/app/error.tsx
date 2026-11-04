"use client";
import { ErrorState } from "@/components/shared";
export default function ErrorPage({
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  return (
    <ErrorState
      title="Esta página encontrou um problema"
      message="Tente carregar a página novamente."
      onRetry={reset}
    />
  );
}
