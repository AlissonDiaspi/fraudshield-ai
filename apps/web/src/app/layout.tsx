import type { Metadata } from "next";
import { AppShell } from "@/components/app-shell";
import "./globals.css";

export const metadata: Metadata = {
  title: {
    default: "FraudShield AI | Console operacional",
    template: "%s | FraudShield AI",
  },
  description:
    "Console operacional para análise de risco e detecção de fraudes financeiras.",
};
export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="pt-BR" className="dark">
      <body>
        <AppShell>{children}</AppShell>
      </body>
    </html>
  );
}
