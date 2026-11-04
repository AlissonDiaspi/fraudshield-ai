"use client";

import { useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  Activity,
  ArrowUpRight,
  ChevronRight,
  ChevronsLeft,
  ChevronsRight,
  Command,
  LayoutDashboard,
  ListFilter,
  Menu,
  ScanLine,
  ShieldCheck,
  Sparkles,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  Sheet,
  SheetContent,
  SheetDescription,
  SheetTitle,
  SheetTrigger,
} from "@/components/ui/sheet";
import { Tooltip, TooltipProvider } from "@/components/ui/tooltip";
import { ApiStatus, HealthProvider } from "@/components/health-provider";
import { cn } from "@/lib/utils";

const navigation = [
  { href: "/dashboard", title: "Visão geral", icon: LayoutDashboard },
  { href: "/analyze", title: "Analisar transação", icon: ScanLine },
  { href: "/transactions", title: "Histórico", icon: ListFilter },
  { href: "/system", title: "Status do sistema", icon: Activity },
];
function Brand({ compact = false }: { compact?: boolean }) {
  return (
    <Link
      href="/dashboard"
      aria-label="FraudShield AI — visão geral"
      className="flex items-center gap-3"
    >
      <span className="brand-icon">
        <ShieldCheck className="size-6" strokeWidth={1.6} />
      </span>
      {!compact && (
        <span className="whitespace-nowrap text-lg font-semibold tracking-tight">
          FraudShield<span className="ml-1 text-primary">AI</span>
          <span className="mt-0.5 block text-[9px] font-medium uppercase tracking-[.14em] text-muted-foreground">
            Inteligência antifraude
          </span>
        </span>
      )}
    </Link>
  );
}
function Navigation({
  compact,
  onNavigate,
}: {
  compact?: boolean;
  onNavigate?: () => void;
}) {
  const pathname = usePathname();
  return (
    <nav aria-label="Navegação principal" className="space-y-2">
      {navigation.map(({ href, title, icon: Icon }) => {
        const active = pathname === href || pathname.startsWith(`${href}/`);
        const link = (
          <Link
            href={href}
            onClick={onNavigate}
            aria-current={active ? "page" : undefined}
            className={cn(
              "nav-item",
              active && "nav-active",
              compact && "justify-center px-0",
            )}
          >
            <Icon className="size-[18px] shrink-0" />
            {!compact && (
              <>
                <span className="flex-1">{title}</span>
                {active && (
                  <span className="size-1.5 rounded-full bg-primary" />
                )}
              </>
            )}
            {compact && <span className="sr-only">{title}</span>}
          </Link>
        );
        return compact ? (
          <Tooltip key={href} content={title}>
            {link}
          </Tooltip>
        ) : (
          <div key={href}>{link}</div>
        );
      })}
    </nav>
  );
}
export function AppShell({ children }: { children: React.ReactNode }) {
  const [collapsed, setCollapsed] = useState(false);
  const [mobileOpen, setMobileOpen] = useState(false);
  const pathname = usePathname();
  const current =
    navigation.find((item) => pathname.startsWith(item.href))?.title ??
    "Visão geral";
  return (
    <TooltipProvider delayDuration={200}>
      <HealthProvider>
        <a href="#main-content" className="skip-link">
          Ir para o conteúdo
        </a>
        <div className={cn("app-shell", collapsed && "sidebar-collapsed")}>
          <aside className="desktop-sidebar">
            <div className="px-5 pt-8">
              <Brand compact={collapsed} />
            </div>
            <div className="mt-11 px-4">
              {!collapsed && (
                <p className="mb-4 px-3 text-[10px] font-medium uppercase tracking-[.18em] text-muted-foreground/70">
                  Workspace
                </p>
              )}
              <Navigation compact={collapsed} />
            </div>
            <div className="mt-auto px-4 pb-5">
              {!collapsed && (
                <div className="mb-5 rounded-xl border border-primary/10 bg-primary/[.035] p-4">
                  <Sparkles className="mb-3 size-5 text-primary" />
                  <p className="text-xs font-medium">
                    Decisões com inteligência.
                  </p>
                  <p className="mt-2 text-xs leading-relaxed text-muted-foreground">
                    Uma visão clara do risco em cada transação.
                  </p>
                  <Link
                    href="/analyze"
                    className="mt-4 flex items-center gap-2 text-xs font-medium text-primary"
                  >
                    Iniciar análise
                    <ArrowUpRight className="size-3.5" />
                  </Link>
                </div>
              )}
              <div
                className={cn(
                  "flex items-center gap-3 border-t border-border pt-5",
                  collapsed && "justify-center",
                )}
              >
                <div className="grid size-9 shrink-0 place-items-center rounded-lg border border-border bg-accent text-primary">
                  <Command className="size-4" />
                </div>
                {!collapsed && (
                  <div className="flex-1">
                    <p className="text-xs font-medium">Workspace operacional</p>
                    <p className="mt-1 text-[10px] text-muted-foreground">
                      FraudShield AI
                    </p>
                  </div>
                )}
              </div>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setCollapsed(!collapsed)}
                className="mt-4 w-full"
                aria-label={collapsed ? "Expandir menu" : "Recolher menu"}
              >
                {collapsed ? (
                  <ChevronsRight />
                ) : (
                  <>
                    <ChevronsLeft />
                    <span>Recolher menu</span>
                  </>
                )}
              </Button>
            </div>
          </aside>
          <div className="workspace">
            <header className="app-header">
              <div className="flex min-w-0 items-center gap-3">
                <Sheet open={mobileOpen} onOpenChange={setMobileOpen}>
                  <SheetTrigger asChild>
                    <Button
                      variant="ghost"
                      size="icon"
                      className="lg:hidden"
                      aria-label="Abrir navegação"
                    >
                      <Menu />
                    </Button>
                  </SheetTrigger>
                  <SheetContent>
                    <SheetTitle className="sr-only">
                      Navegação FraudShield AI
                    </SheetTitle>
                    <SheetDescription className="sr-only">
                      Acesse as páginas da plataforma.
                    </SheetDescription>
                    <div className="mb-10 mt-5">
                      <Brand />
                    </div>
                    <Navigation onNavigate={() => setMobileOpen(false)} />
                  </SheetContent>
                </Sheet>
                <span className="hidden text-xs text-muted-foreground sm:inline">
                  Workspace
                </span>
                <ChevronRight className="hidden size-3 text-muted-foreground/50 sm:block" />
                <span className="truncate text-xs font-medium">
                  {pathname.startsWith("/transactions/")
                    ? "Detalhes da transação"
                    : current}
                </span>
              </div>
              <div className="flex shrink-0 items-center gap-4">
                <ApiStatus />
                <span className="hidden h-5 w-px bg-border sm:block" />
                <span className="hidden rounded-md border border-border px-2 py-1 font-mono text-[10px] text-muted-foreground sm:block">
                  CONSOLE
                </span>
              </div>
            </header>
            <main id="main-content" tabIndex={-1} className="main-content">
              {children}
            </main>
            <footer className="app-footer">
              <span>
                FraudShield AI<span className="mx-2 text-border">/</span>
                Inteligência aplicada à segurança financeira
              </span>
              <span className="flex items-center gap-1.5">
                <ShieldCheck className="size-3.5" />
                Análise orientada por dados
              </span>
            </footer>
          </div>
        </div>
      </HealthProvider>
    </TooltipProvider>
  );
}
