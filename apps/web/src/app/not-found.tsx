import Link from "next/link";
import { EmptyState } from "@/components/shared";
import { Button } from "@/components/ui/button";
export default function NotFound() {
  return (
    <EmptyState
      title="Página não encontrada"
      description="O endereço informado não está disponível."
      action={
        <Button asChild>
          <Link href="/dashboard">Voltar à visão geral</Link>
        </Button>
      }
    />
  );
}
